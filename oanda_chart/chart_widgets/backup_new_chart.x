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


from typing import List, Tuple, Optional
from tkinter import Widget, Canvas, Button
from forex_types import FracPips, Pair, Price

from oanda_candles import (
    QuoteKind,
    Gran,
    Candle,
    CandleCollector,
    CandleMeister,
)

from oanda_chart.geo.candle_offset import CandleOffset
from oanda_chart.util.candle_range import get_candle_range


class Tag:
    CANDLE = "candle"
    MIST = "mist"


class ConfigAttr:
    WIDTH: str = "width"
    HEIGHT: str = "height"


class Color:
    BACKGROUND: str = "#000000"
    BADGE: str = "#212121"
    GRID: str = "#000000"
    MIST: str = "#131313"


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
    TAIL_PADDING = 50  # num pixels to pad to right of candles when tailing.
    DEFAULT_FPP = 10.0  # initial frac pips per pixel value before data loaded.
    MIN_FPP = 0.01  # lowest allowed value for fpp
    PRICE_PAD: FracPips = FracPips(10_000)
    FP_MIN: FracPips = FracPips(0)
    FP_MAX: FracPips = FracPips(1_000_000)
    PRICE_VIEW_PAD = 25


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

    def find_top_and_bottom(self):
        """Set top and bottom price of scrollable area.

        To do this we pull the last 500 monthly candles (e.g. all of them),
        and then we find the highest ask and lowest bid price in them.
        We pad both by a Const.PRICE_PAD.
        """
        CandleMeister.init_meister(self.token)
        candles = CandleMeister.grab(self.pair, Gran.M, 500)
        low, high = get_candle_range(candles)
        fp_low = FracPips.from_price(low)
        fp_high = FracPips.from_price(high)
        self.fp_top = FracPips(fp_high + Const.PRICE_PAD)
        self.fp_bottom = FracPips(fp_low - Const.PRICE_PAD)

    def enforce_price_view(self):
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
        self.draw_candles()
        pixels_down = self.y_fp(fp_max) - Const.PRICE_VIEW_PAD
        percent_down = float(pixels_down) / float(self.scroll_height)
        self.yview_moveto(percent_down)

    def apply_resize(self):
        """Adjust attributes to reflect current width and height."""
        if self.fp_top is None or self.fp_bottom is None:
            return
        self.view_width = int(self.cget(ConfigAttr.WIDTH))
        self.view_height = int(self.cget(ConfigAttr.HEIGHT))
        self.scroll_width = self.view_width * 3
        fp_height = self.fp_top - self.fp_bottom
        self.scroll_height = round(fp_height / self.fpp)
        self.slots = int(self.scroll_width / self.offset)
        full_width = (2 * self.view_width) - Const.TAIL_PADDING
        self.full_slots = round(full_width / self.offset)
        self.other_slots = self.slots - self.full_slots
        self.config(scrollregion=(0, 0, self.scroll_width, self.scroll_height))

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
            self.draw_candles()
            if self.price_view:
                self.enforce_price_view()
        self.xview_moveto(0.333333)

    def load(self, pair: Pair, gran: Gran):
        if pair == self.pair and gran == self.gran and self.collector is not None:
            return
        self.candle_ndx = 0
        self.pair = pair
        self.gran = gran
        self.find_top_and_bottom()
        self.fpp = Const.DEFAULT_FPP
        self.apply_resize()
        self.collector = CandleCollector(self.token, pair, gran)
        self.draw_candles()
        self.enforce_price_view()

    def y_fp(self, fp: FracPips) -> int:
        """Get y pixel coord for given FracPips."""
        return round((self.fp_top - fp) / self.fpp)

    def y_price(self, price: Price) -> int:
        """Get y pixel coord for given price."""
        fp = FracPips.from_price(price)
        return self.y_fp(fp)

    def draw_candles(self):
        self.pull_candles()
        self.apply_resize()
        self.draw_mist()
        self.delete(Tag.CANDLE)
        num_to_draw = self.slots - self.missing_history - self.future_slots
        for ndx in range(num_to_draw):
            candle = self.candles[ndx]
            slot = self.missing_history + ndx
            self.draw_candle_at(candle, slot)

    def pull_candles(self):
        request_num = self.full_slots + self.candle_ndx  # number of candles to request
        self.candles = self.collector.grab(request_num)  # candles back to first we need
        self.missing_history = request_num - len(self.candles)
        self.future_slots = max(0, self.other_slots - self.candle_ndx)

    def draw_mist(self):
        self.delete(Tag.MIST)
        if self.missing_history:
            x_right = self.missing_history * self.offset
            self.mist_at(0, 0, x_right, self.scroll_height)
        if self.future_slots:
            x_right = self.slots * self.offset
            x_left = x_right - (self.future_slots * self.offset)
            self.mist_at(x_left, 0, x_right, self.scroll_height)

    def mist_at(self, x1, y1, x2, y2):
        self.create_rectangle(x1, y1, x2, y2, fill=Color.MIST, width=0.0, tag=Tag.MIST)

    def draw_candle_at(self, candle: Candle, slot: int):
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