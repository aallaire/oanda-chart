"""Refresher reference for canvas coordinates:

There are two kinds of coordinates:
    View Coordinates:
        * Its height and width depend on the user resizing the canvas widget.
        * This is the width and height of the canvas widget itself.
        * It is only a view of part of the whole canvas though.
        * to see how many pixels it is to the left of whole canvas: canvas_obj.canvasx(0)
        * to see how many pixels down from top of whole canvas: canvas_obj.canvasy(0)

    Scroll Coordinates/Canvas Coordinates:
        * The height and width of the entire area one can pan or scroll the view over.
        * This is configured as the scrollregion box of the canvas widget.
        * When you create items on the canvas, you give them these coordinates.
"""


from typing import List, Optional
from tkinter import Widget, Canvas
from forex_types import FracPips, Pair, Price

from oanda_candles import (
    QuoteKind,
    Gran,
    Candle,
    CandleCollector,
)

from oanda_chart.geo.candle_offset import CandleOffset
from oanda_chart.util.candle_range import get_candle_range
from oanda_chart.chart_widgets.price_scale import PriceScale


class Tag:
    CANDLE = "candle"
    MIST = "mist"
    PRICE_GRID = "pricegrid"


class ConfigAttr:
    WIDTH: str = "width"
    HEIGHT: str = "height"


class Color:
    BACKGROUND: str = "#000000"
    BADGE: str = "#212121"
    GRID: str = "#333333"
    MIST: str = "#111111"


class CandleColor:
    BULL: str = "#00FF00"
    BEAR: str = "#FF0000"
    DOJI: str = "#aaaaaa"
    WICK: str = "#999999"


class UnfinishedCandleColor:
    BULL: str = "#447744"
    BEAR: str = "#774444"
    WICK: str = "#777777"
    DOJI: str = "#aaaaaa"


class Event:
    LEFT_CLICK: str = "<ButtonPress-1>"
    LEFT_DRAG: str = "<B1-Motion>"
    LEFT_RELEASE: str = "<ButtonRelease-1>"
    MOUSE_WHEEL: str = "<MouseWheel>"
    RESIZE: str = "<Configure>"


class Const:
    TAIL_PADDING = 200  # num pixels to pad to right of candles when tailing.
    DEFAULT_FPP = 10.0  # initial frac pips per pixel value before data loaded.
    MIN_FPP = 0.01  # lowest allowed value for fpp
    PRICE_PAD: FracPips = FracPips(10_000)
    FP_MIN: FracPips = FracPips(0)
    FP_MAX: FracPips = FracPips(1_000_000)
    PRICE_VIEW_PAD = 25
    ONE_THIRD = float(1) / float(3)


class NewChart(Canvas):
    def __init__(
        self, parent: Widget, token: str, width: int = 1200, height: int = 700
    ):
        """Initialize chart canvas.
        
        Args:
            parent: tkinter widget canvas should belong to
            token: secret Oanda API access token
            width: width to make canvas in pixels (viewable area)
            height: height to make canvas in pixels (viewable area)
        Attributes (not all set upon initialization).
        """
        # Misc Attributes
        self.token = token
        self.marked_x: Optional[int] = None
        self.tailing: bool = True
        self.price_view: bool = True
        self.missing_history: int = 0
        self.future_slots: int = 0
        # Candle Data Attributes
        self.candles: Optional[List[Candle]] = None
        self.candle_ndx: int = 0
        self.collector: Optional[CandleCollector] = None
        self.gran: Optional[Gran] = None
        self.pair: Optional[Pair] = None
        self.quote_kind: QuoteKind = QuoteKind.MID
        self.fp_top: Optional[FracPips] = None
        self.fp_bottom: Optional[FracPips] = None
        # Size/Coordinates Attributes (updated by resize)
        self.view_width: int = width
        self.view_height: int = height
        self.scroll_width: int = width * 3
        self.scroll_height: int = height * 3
        self.offset: CandleOffset = CandleOffset.DEFAULT
        self.slots: int = int(self.scroll_width / self.offset)
        full_width = (2 * self.view_width) - Const.TAIL_PADDING
        self.full_slots: int = round(full_width / self.offset)
        self.other_slots: int = self.slots - self.full_slots
        self.fpp: float = Const.DEFAULT_FPP
        self.price_scale: Optional[PriceScale] = None
        Canvas.__init__(
            self,
            master=parent,
            background=Color.BACKGROUND,
            height=height,
            scrollregion=(0, 0, width * 3, height * 3),
            width=width,
        )
        self.bind(Event.LEFT_CLICK, self.scroll_start)
        self.bind(Event.LEFT_DRAG, self.scroll_move)
        self.bind(Event.LEFT_RELEASE, self.scroll_release)
        self.bind(Event.RESIZE, self.resize)
        self.bind(Event.MOUSE_WHEEL, self.squeeze_or_expand)

    def load(self, pair: Pair, gran: Gran):
        if pair == self.pair and gran == self.gran and self.collector is not None:
            return
        self.price_scale = None
        self.candle_ndx = 0
        self.pair = pair
        self.gran = gran
        self.fpp = Const.DEFAULT_FPP
        self.collector = CandleCollector(self.token, pair, gran)
        self._draw_candles()
        self._enforce_price_view()

    def y_fp(self, fp: FracPips) -> int:
        """Get y pixel coord for given FracPips."""
        return round((self.fp_top - fp) / self.fpp)

    def y_price(self, price: Price) -> int:
        """Get y pixel coord for given price."""
        fp = FracPips.from_price(price)
        return self.y_fp(fp)

    # ---------------------------------------------------------------------------
    # Event Callbacks
    # ---------------------------------------------------------------------------

    def scroll_start(self, event):
        self.marked_x = event.x
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def scroll_release(self, event):
        shift = event.x - self.marked_x
        ndx_shift = round(shift / self.offset)
        self.delete(Tag.CANDLE)
        self.candle_ndx += ndx_shift
        if self.candle_ndx < 0:
            self.candle_ndx = 0
        if self.pair is not None:
            self._draw_candles()
            if self.price_view:
                self._enforce_price_view()
        self.xview_moveto(Const.ONE_THIRD)

    def resize(self, event):
        self._apply_resize(width=event.width, height=event.height)
        if self.candles:
            self._apply_resize()
            self._draw_candles()
            self._apply_resize()
            if self.price_view:
                self._apply_resize()
                self._enforce_price_view()

    def squeeze_or_expand(self, event):
        """Squeeze candle offset or expand it according to mouse wheel direction."""
        if not self.candles:
            return
        old_offset = self.offset
        if event.delta > 0:
            new_offset = CandleOffset(old_offset + 1)
        elif event.delta < 0:
            new_offset = CandleOffset(old_offset - 1)
        else:
            return
        if new_offset != old_offset:
            self._apply_offset(new_offset)
            if self.price_view:
                self._enforce_price_view()

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _apply_resize(self, width: Optional[int] = None, height: Optional[int] = None):
        """Adjust attributes to reflect current width and height."""
        if self.fp_top is None or self.fp_bottom is None:
            return
        if width is not None:
            self.view_width = width
        if height is not None:
            self.view_height = height
        self.scroll_width = self.view_width * 3
        fp_height = self.fp_top - self.fp_bottom
        self.scroll_height = round(float(fp_height) / self.fpp)
        self.slots = int(self.scroll_width / self.offset)
        full_width = (2 * self.view_width) - Const.TAIL_PADDING
        self.full_slots = round(full_width / self.offset)
        self.other_slots = self.slots - self.full_slots
        self.config(scrollregion=(0, 0, self.scroll_width, self.scroll_height))

    def _apply_offset(self, offset: CandleOffset):
        """Apply a new offset (candle width) to chart."""
        self.offset = CandleOffset(offset)
        self._apply_resize()
        self._draw_candles()

    def _draw_candles(self):
        self._pull_candles()
        self._find_top_and_bottom()
        self._apply_resize()
        self._draw_mist()
        self._draw_price_grid()
        self.delete(Tag.CANDLE)
        num_to_draw = self.slots - self.missing_history - self.future_slots
        for ndx in range(num_to_draw):
            candle = self.candles[ndx]
            slot = self.missing_history + ndx
            self._draw_candle_at(candle, slot)

    def _draw_candle_at(self, candle: Candle, slot: int):
        ohlc = candle.quote(self.quote_kind)
        o = self.y_price(ohlc.o)
        h = self.y_price(ohlc.h)
        l = self.y_price(ohlc.l)
        c = self.y_price(ohlc.c)
        left = slot * self.offset
        right = left + self.offset.far_side()
        middle = left + self.offset.wick()
        color = CandleColor if candle.complete else UnfinishedCandleColor
        self.create_line(middle, l, middle, h, fill=color.WICK, tags=Tag.CANDLE)
        if ohlc.o < ohlc.c:
            self.create_rectangle(
                left, o, right, c, fill=color.BULL, tags=Tag.CANDLE, width=0.0,
            )
        elif ohlc.o > ohlc.c:
            self.create_rectangle(
                left, c, right, o, fill=color.BEAR, tags=Tag.CANDLE, width=0.0,
            )
        else:
            self.create_line(left, o, right, o, fill=color.DOJI, tags=Tag.CANDLE)

    def _draw_mist(self):
        self.delete(Tag.MIST)
        if self.missing_history:
            x_right = self.missing_history * self.offset
            self._mist_at(0, 0, x_right, self.scroll_height)
        if self.future_slots:
            x_right = self.slots * self.offset
            x_left = x_right - (self.future_slots * self.offset)
            self._mist_at(x_left, 0, x_right, self.scroll_height)

    def _draw_price_grid(self):
        self.delete(Tag.PRICE_GRID)
        if self.fpp is None or self.fp_bottom is None or self.fp_top is None:
            return
        if self.price_scale is None:
            self.price_scale = PriceScale(self.fpp)
        for grid_fp in self.price_scale.get_grid_list(self.fp_bottom, self.fp_top):
            print(grid_fp)
            y = self.y_fp(grid_fp)
            self.create_line(
                0, y, self.scroll_width, y, fill=Color.GRID, tag=Tag.PRICE_GRID
            )

    def _enforce_price_view(self):
        """Adjust so that prices fill screen."""
        if not self.price_view:
            return
        remainder = self.slots % 3
        little_third = round((self.slots - remainder) / 3)
        big_third = round(self.slots / 3)
        start_ndx = little_third - self.missing_history
        end_ndx = min(big_third + little_third + 1, len(self.candles))
        num_candles = end_ndx - start_ndx
        if num_candles <= 0:
            return
        # Find max and min prices for the current range.
        fp_min = Const.FP_MAX
        fp_max = Const.FP_MIN
        for ndx in range(start_ndx, end_ndx):
            candle = self.candles[ndx]
            fp_low = FracPips.from_price(candle.bid.l)
            fp_high = FracPips.from_price(candle.ask.h)
            if fp_low < fp_min:
                fp_min = fp_low
            if fp_high > fp_max:
                fp_max = fp_high
        # figure out how many fractional pips we want to fit into view height.
        fp_delta = fp_max - fp_min
        target_height = self.view_height - (2 * Const.PRICE_VIEW_PAD)
        self.fpp = max((fp_delta / target_height), Const.MIN_FPP)
        self._draw_candles()
        pixels_down = self.y_fp(fp_max) - Const.PRICE_VIEW_PAD
        percent_down = float(pixels_down) / float(self.scroll_height)
        self.yview_moveto(percent_down)

    def _find_top_and_bottom(self):
        """Set top and bottom price of scrollable area.

        To do this we pull the last 500 monthly candles (e.g. all of them),
        and then we find the highest ask and lowest bid price in them.
        We pad both by a Const.PRICE_PAD.
        """
        if self.candles:
            low, high = get_candle_range(self.candles)
            self.fp_top = FracPips.from_price(high) + Const.PRICE_PAD
            self.fp_bottom = FracPips.from_price(low) - Const.PRICE_PAD

    def _mist_at(self, x1, y1, x2, y2):
        self.create_rectangle(x1, y1, x2, y2, fill=Color.MIST, width=0.0, tag=Tag.MIST)

    def _pull_candles(self):
        request_num = self.full_slots + self.candle_ndx  # number of candles to request
        self.candles = self.collector.grab(request_num)  # candles back to first we need
        self.missing_history = request_num - len(self.candles)
        self.future_slots = max(0, self.other_slots - self.candle_ndx)
