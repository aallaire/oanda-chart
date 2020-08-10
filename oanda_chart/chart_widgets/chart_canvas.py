from typing import List, Tuple, Optional
from tkinter import Widget, Canvas, Button
import math

from oanda_candles import QuoteKind, CandleMeister, Pair, Gran

from oanda_chart.geo.coords import Coords
from oanda_chart.geo.candles_element import CandlesElement
from oanda_chart.geo.candle_offset import CandleOffset


class Tag:
    CANDLE = "candle"


class Color:
    BACKGROUND: str = "#000000"
    BADGE: str = "#212121"
    GRID: str = "#111111"


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
    MOUSE_WHEEL: str = "<MouseWheel>"
    RESIZE: str = "<Configure>"


class ChartCanvas(Canvas):
    def __init__(self, parent: Widget, width: int = 1200, height: int = 700):
        self.coords = Coords()
        region = (0, 0, self.coords.width, self.coords.height)
        Canvas.__init__(
            self,
            master=parent,
            background=Color.BACKGROUND,
            height=height,
            scrollregion=region,
            width=width,
        )
        self.view_price_mode: bool = False
        self.loaded: bool = False
        self.target_count = 0
        self.max_count = 2000
        self.update_id = 0
        self.pair: Optional[Pair] = None
        self.gran: Optional[Gran] = None
        self.bind(Event.LEFT_CLICK, self.scroll_start)
        self.bind(Event.LEFT_DRAG, self.scroll_move)
        self.bind(Event.MOUSE_WHEEL, self.squeeze_or_expand)
        self.bind(Event.RESIZE, self.resize_callback)

    def get_height(self):
        return int(self.cget("height"))

    def get_width(self):
        return int(self.cget("width"))

    def scroll_start(self, event):
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)
        if self.loaded:
            if self.view_price_mode:
                self.enforce_view_price()

    def squeeze_or_expand(self, event):
        """Squeeze candle offset or expand it according to mouse wheel direction."""
        if not self.loaded:
            return
        old_offset = self.coords.offset
        if event.delta > 0:
            new_offset = CandleOffset(old_offset + 1)
        elif event.delta < 0:
            new_offset = CandleOffset(old_offset - 1)
        else:
            return
        if new_offset != old_offset:
            # Find the candle position on right side of view before applying new offset.
            width = self.get_width()
            right_ndx = self.coords.ndx_x(self.canvasx(width))
            self.coords.config(offset=new_offset)
            self.update_scrollregion()
            # Find the pixel position that now matches the candle position.
            right_x = self.coords.x_ndx(right_ndx)
            # And use it to find the where to move view to.
            left_moveto = self.coords.moveto_x(right_x - width)
            self.xview_moveto(left_moveto)
            self.view_price_mode = True
            self.draw_candles()
            self.enforce_view_price()

    # def apply_candles(self, candles: CandlesElement):
    #    self.coords.config(candles=candles)
    #    self.enforce_view_price()
    #    self.xview_moveto(1.0)
    #    self.enforce_view_price()

    # def start_candle_tracking(self, pair: Pair, gran: Gran):

    def load(self, pair: Pair, gran: Gran):
        self.loaded = True
        self.pair = pair
        self.gran = gran
        self.target_count = 500
        self.view_price_mode = True
        candles = CandlesElement(self.pair, self.gran, self.target_count)
        self.coords.config(candles=candles)
        self.enforce_view_price()
        self.xview_moveto(1.0)
        self.enforce_view_price()
        self.update_id += 1
        self._update(self.update_id)

    def unload(self):
        self.loaded = True
        self.pair = None
        self.gran = None
        self.delete(Tag.CANDLE)

    def _update(self, update_id):
        if update_id == self.update_id and self.loaded:
            left_side = self.canvasx(0)
            if self.target_count < self.max_count and left_side < self.coords.LEFT_PAD:
                print(self.target_count)
                self.target_count += 500
                pixel_position = (500 * self.coords.offset) + left_side
            else:
                pixel_position = None
            candles = CandlesElement(self.pair, self.gran, self.target_count)
            self.coords.config(candles=candles)
            self.draw_candles()
            if self.view_price_mode:
                self.enforce_view_price()
            if pixel_position is not None:
                self.xview_moveto(pixel_position / self.coords.width)
            self.after(1000, self._update, update_id)

    def go_home(self):
        self.coords.config(offset=Coords.DEFAULT_OFFSET)
        self.enforce_view_price()
        self.xview_moveto(1.0)
        self.enforce_view_price()

    def view_region(self) -> Tuple[int, int, int, int]:
        """Return coordinates of current view as canvas region"""
        return (
            self.canvasx(0),
            self.canvasy(0),
            self.canvasx(self.get_width()),
            self.canvasy(self.get_height()),
        )

    def enforce_view_price(self):
        """Adjust so view matches current candle price range.

        The following steps are followed:
            * Figure out what candles are within width of view.
            * Find the high/low price of those candles.
            * Adjust coords.fpp so that range fits height of view.
            * Redraw items in canvas to reflect coords change.
            * Move view up or down to those candles.
        """
        view_x1, view_y1, view_x2, view_y2 = self.view_region()
        ndx_1 = self.coords.ndx_x(view_x1)
        ndx_2 = self.coords.ndx_x(view_x2) + 1
        x1, y1, x2, y2 = self.coords.candle_region(ndx_1, ndx_2)
        target_height = 30 + y2 - y1
        fpp_float = (self.coords.fpp * target_height) / self.get_height()
        new_fpp = max(math.ceil(fpp_float), 1)
        self.coords.config(fpp=new_fpp)
        self.draw_candles()
        x1, y1, x2, y2 = self.coords.candle_region(ndx_1, ndx_2)
        candle_height = y2 - y1
        margin_pixels = self.get_height() - candle_height
        half_margin = round(margin_pixels / 2)
        self.yview_moveto(self.coords.moveto_y(y1 - half_margin))

    def resize_callback(self, event):
        new_height = event.height - 4
        new_width = event.width - 4
        self.config(height=new_height, width=new_width)
        self.update()
        print(f"RESIZE CALLBACK: {event.height} {event.width}")
        print(f"get size: {self.get_height()} {self.get_width()}")

    def update_scrollregion(self):
        """Update scrollregion of canvas to match self.coords."""
        region = (0, 0, self.coords.width, self.coords.height)
        self.config(scrollregion=region)

    def draw_candles(self, quote_kind: QuoteKind = QuoteKind.MID):
        self.delete(Tag.CANDLE)
        region = (0, 0, self.coords.width, self.coords.height)
        self.config(scrollregion=region)
        for ndx, candle in enumerate(self.coords.candles):
            ohlc = candle.quote(quote_kind)
            o = self.coords.y_price(ohlc.o)
            h = self.coords.y_price(ohlc.h)
            l = self.coords.y_price(ohlc.l)
            c = self.coords.y_price(ohlc.c)
            left = self.coords.x_ndx(ndx)
            right = left + self.coords.offset.far_side()
            middle = left + self.coords.offset.wick()
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
