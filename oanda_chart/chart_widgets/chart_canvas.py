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


from typing import List, Optional, Set
from tkinter import Widget, Canvas
from uuid import uuid4

from forex_types import FracPips, Pair, Price, Currency

from oanda_candles import (
    QuoteKind,
    Gran,
    Candle,
    CandleCollector,
)

from oanda_chart.geo.candle_offset import CandleOffset
from oanda_chart.util.candle_range import get_candle_range
from oanda_chart.chart_widgets.price_scale import PriceScale
from oanda_chart.env.const import (
    CandleColor,
    Color,
    Const,
    Event,
    Tag,
    UnfinishedCandleColor,
)


class ChartCanvas(Canvas):
    def __init__(self, parent: Widget, width: int = 1200, height: int = 700):
        """Initialize chart canvas.
        
        Args:
            parent: tkinter widget canvas should belong to
            width: width to make canvas in pixels (viewable area)
            height: height to make canvas in pixels (viewable area)
        Attributes (not all set upon initialization).
        """
        # Misc Attributes
        self.token: Optional[str] = None
        self.marked_x: Optional[int] = None
        self.tailing: bool = False
        self.tail_lock_set: Set[str] = set()
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
        """
        self.bind(Event.LEFT_CLICK, self.scroll_start)
        self.bind(Event.LEFT_DRAG, self.scroll_move)
        self.bind(Event.LEFT_RELEASE, self.scroll_release)
        self.bind(Event.RESIZE, self.resize)
        self.bind(Event.MOUSE_WHEEL, self.squeeze_or_expand)
        self.bind(Event.DOUBLE_CLICK, self.toggle_price_view)
        """

    def load(self, token: str, pair: Pair, gran: Gran, quote_kind: QuoteKind):
        if pair == self.pair and gran == self.gran and self.collector is not None:
            if quote_kind != self.quote_kind:
                self.quote_kind = quote_kind
                self.update_candles()
            return
        self.token = token
        self.price_scale = None
        self.candle_ndx = 0
        self.pair = pair
        self.gran = gran
        self.quote_kind = quote_kind
        self.fpp = Const.DEFAULT_FPP
        self.collector = CandleCollector(self.token, pair, gran)
        self.update_candles()
        self.enforce_price_view()
        self.price_scale = PriceScale(self.fpp)
        self.go_home()

    def y_fp(self, fp: FracPips) -> int:
        """Get y pixel coord for given FracPips."""
        return round((self.fp_top - fp) / self.fpp)

    def y_price(self, price: Price) -> int:
        """Get y pixel coord for given price."""
        fp = FracPips.from_price(price)
        return self.y_fp(fp)

    def fp_y(self, y: int) -> FracPips:
        """Get fractional pips from canvas y coordinate"""
        return FracPips(self.fp_top - round(y * self.fpp))

    def go_home(self):
        self.delete(Tag.CANDLE)
        self.candle_ndx = 0
        self.price_view = True
        self.offset = CandleOffset.DEFAULT
        if self.pair is not None:
            self.update_candles()
            self.enforce_price_view()
            self.update_candles()
            self.enforce_price_view()
        self.xview_moveto(Const.ONE_THIRD)
        self.tailing = True
        self.start_tail()

    # ---------------------------------------------------------------------------
    # Event Callbacks
    # ---------------------------------------------------------------------------

    '''
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
            self._update_candles()
            if self.price_view:
                self._enforce_price_view()
        self.xview_moveto(Const.ONE_THIRD)
        if self._end_in_sight():
            self.tailing = True
            self._start_tail()
        else:
            self.tailing = False

    def resize(self, event):
        self._apply_resize(width=event.width, height=event.height)
        if self.candles:
            self._apply_resize()
            self._update_candles()
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
            if self._end_in_sight():
                self.tailing = True
                self._start_tail()
            else:
                self.tailing = False

    def toggle_price_view(self, event):
        self.price_view = not self.price_view
    '''

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def end_in_sight(self) -> bool:
        """Determine if last candles are visible in view (or at least close)."""
        pixels_from_end = self.candle_ndx * self.offset
        return pixels_from_end < Const.TAIL_PADDING

    def start_tail(self):
        if not self.tailing or self.tail_lock_set:
            return
        tail_lock = str(uuid4())
        self.tail_lock_set.add(tail_lock)
        self.after(2000, self.tail, tail_lock)

    def tail(self, tail_lock: str):
        if not self.candles or not self.tailing or tail_lock not in self.tail_lock_set:
            if tail_lock in self.tail_lock_set:
                self.tail_lock_set.remove(tail_lock)
            return
        # If other locks, then exit unless our lock is first alphabetically
        if len(self.tail_lock_set) > 1:
            for other_lock in self.tail_lock_set:
                if other_lock < tail_lock:
                    return
        last_candle = self.candles[-1]
        new_candles = self.collector.grab(10)
        found_match = False
        for new_candle in new_candles:
            if found_match:
                self.candles.append(new_candle)
            if new_candle.time == last_candle.time:
                found_match = True
                self.candles[-1] = new_candle
        if found_match:
            # For when the grab of 10 candles did not overlap with the latest candle
            # we already had...we go ahead and do the regular redraw of candles.
            self.update_candles()
            self.apply_resize()
        if self.tailing:
            self.after(2000, self.tail, tail_lock)

    def apply_resize(self, width: Optional[int] = None, height: Optional[int] = None):
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

    def apply_offset(self, offset: CandleOffset):
        """Apply a new offset (candle width) to chart."""
        self.offset = CandleOffset(offset)
        self.apply_resize()
        self.draw_price_grid()
        self.update_candles()

    def update_candles(self):
        self.pull_candles()
        self.find_top_and_bottom()
        self.apply_resize()
        self.draw_mist()
        self.draw_price_grid()
        self.draw_candles()

    def draw_candles(self):
        self.delete(Tag.CANDLE)
        num_to_draw = self.slots - self.missing_history - self.future_slots
        for ndx in range(num_to_draw):
            candle = self.candles[ndx]
            slot = self.missing_history + ndx
            self.draw_candle_at(candle, slot)

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

    def draw_mist(self):
        self.delete(Tag.MIST)
        if self.missing_history:
            x_right = self.missing_history * self.offset
            self.mist_at(0, 0, x_right, self.scroll_height)
        if self.future_slots:
            x_right = self.slots * self.offset
            x_left = x_right - (self.future_slots * self.offset)
            if not self.candles[-1].complete:
                # extend future mist to cover the last candle if its not complete.
                x_left -= self.offset
            self.mist_at(x_left, 0, x_right, self.scroll_height)

    def draw_price_grid(self):
        self.delete(Tag.PRICE_GRID)
        if self.fpp is None or self.fp_bottom is None or self.fp_top is None:
            return
        if self.price_scale is None:
            return
        low, high = get_candle_range(self.candles)
        fp_low = FracPips.from_price(low)
        fp_high = FracPips.from_price(high)
        fp_delta = fp_high - fp_low
        pad = fp_delta * 2
        fp_high += pad
        fp_low -= pad
        for grid_fp in self.price_scale.get_grid_list(self.fp_bottom, self.fp_top):
            if fp_low <= grid_fp <= fp_high:
                y = self.y_fp(grid_fp)
                self.create_line(
                    0, y, self.scroll_width, y, fill=Color.GRID, tag=Tag.PRICE_GRID
                )

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
        fp_pad = 2 * fp_delta
        target_height = self.view_height - (2 * Const.PRICE_VIEW_PAD)
        self.fpp = max((fp_delta / target_height), Const.MIN_FPP)
        self.update_candles()
        pixels_down = self.y_fp(fp_max) - Const.PRICE_VIEW_PAD
        percent_down = float(pixels_down) / float(self.scroll_height)
        self.yview_moveto(percent_down)

    def find_top_and_bottom(self):
        """Set top and bottom price of scrollable area.

        We set them very high and low at top and bottom of what the
        forex_type.Price object considers valid price ranges for either
        Yen quoted pairs or other pairs.
        """
        if self.pair:
            if self.pair.quote == Currency.JPY:
                self.fp_top = FracPips.from_price(Price(Price.NINJA_MAX))
                self.fp_bottom = FracPips.from_price(Price(Price.NINJA_MIN))
            else:
                self.fp_top = FracPips.from_price(Price(Price.MAX))
                self.fp_bottom = FracPips.from_price(Price(Price.MIN))

    def mist_at(self, x1, y1, x2, y2):
        self.create_rectangle(x1, y1, x2, y2, fill=Color.MIST, width=0.0, tag=Tag.MIST)

    def pull_candles(self):
        request_num = self.full_slots + self.candle_ndx  # number of candles to request
        self.candles = self.collector.grab(request_num)  # candles back to first we need
        self.missing_history = request_num - len(self.candles)
        self.future_slots = max(0, self.other_slots - self.candle_ndx)
