from typing import List, Tuple
from tkinter import Frame, Widget, Canvas, Button
import math

from oanda_candles import QuoteKind


from oanda_chart.geo.coords import Coords
from oanda_chart.env.colors import DarkColors
from oanda_chart.util.syntax_candy import grid
from oanda_chart.geo.candles_element import CandlesElement
from oanda_chart.geo.candle_offset import CandleOffset


class Tag:
    CANDLE = "candle"


class Color:
    BULL_OUTLINE = "light green"
    BULL_FILL = "green"
    BEAR_OUTLINE = "pink"
    BEAR_FILL = "red"
    DOJI = "gray"
    WICK = "gray"


class GeoFrame(Frame):
    def __init__(self, parent: Widget, width: int = 1200, height: int = 700):
        Frame.__init__(self, parent)
        self.coords = Coords()
        self.width = width
        self.height = height
        region = (0, 0, self.coords.width, self.coords.height)
        self.home_button = Button(self, text="Home", command=self.home_callback)
        self.main = Canvas(
            self,
            width=self.width,
            height=self.height,
            background=DarkColors.BACKGROUND,
            scrollregion=region,
        )
        self.view_price_mode: bool = False
        # self.add_test_grid()
        self.main.bind("<ButtonPress-1>", self.scroll_start)
        self.main.bind("<B1-Motion>", self.scroll_move)
        self.main.bind("<MouseWheel>", self.squeeze_or_expand)
        grid(self.home_button, 0, 0)
        grid(self.main, 1, 0)
        self.grid_rowconfigure(1, weight=1)

    def scroll_start(self, event):
        self.main.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.main.scan_dragto(event.x, event.y, gain=1)
        if self.view_price_mode:
            self.enforce_view_price()

    def squeeze_or_expand(self, event):
        """Squeeze candle offset or expand it according to mouse wheel direction."""
        old_offset = self.coords.offset
        if event.delta > 0:
            new_offset = CandleOffset(old_offset + 1)
        elif event.delta < 0:
            new_offset = CandleOffset(old_offset - 1)
        else:
            return
        if new_offset != old_offset:
            # Find the candle position on right side of view before applying new offset.
            right_ndx = self.coords.ndx_x(self.main.canvasx(self.width))
            self.coords.config(offset=new_offset)
            self.update_scrollregion()
            # Find the pixel position that now matches the candle position.
            right_x = self.coords.x_ndx(right_ndx)
            # And use it to find the where to move view to.
            left_moveto = self.coords.moveto_x(right_x - self.width)
            self.main.xview_moveto(left_moveto)
            self.view_price_mode = True
            self.draw_candles()
            self.enforce_view_price()

    def apply_candles(self, candles: CandlesElement):
        self.coords.config(candles=candles)
        self.main.xview_moveto(1.0)
        self.enforce_view_price()

    def home_callback(self):
        self.coords.config(offset=Coords.DEFAULT_OFFSET)
        self.enforce_view_price()
        self.main.xview_moveto(1.0)
        self.enforce_view_price()

    def view_region(self) -> Tuple[int, int, int, int]:
        """Return coordinates of current view as canvas region"""
        return (
            self.main.canvasx(0),
            self.main.canvasy(0),
            self.main.canvasx(self.width),
            self.main.canvasy(self.height),
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
        fpp_float = (self.coords.fpp * target_height) / self.height
        new_fpp = max(math.ceil(fpp_float), 1)
        self.coords.config(fpp=new_fpp)
        self.draw_candles()
        x1, y1, x2, y2 = self.coords.candle_region(ndx_1, ndx_2)
        self.main.yview_moveto(self.coords.moveto_y(y1 - 15))
        self.view_price_mode = True

    def update_scrollregion(self):
        """Update scrollregion of canvas to match self.coords."""
        region = (0, 0, self.coords.width, self.coords.height)
        self.main.config(scrollregion=region)

    def add_test_grid(self):
        """Add grid line squares at 160 pixels for dev testing."""
        x = y = 0
        while x < self.coords.width:
            x += 100
            box = (x, 0, x, self.coords.height)
            self.main.create_line(box, fill=DarkColors.GRID, width=4)
        while y < self.coords.height:
            y += 100
            box = (0, y, self.coords.width, y)
            self.main.create_line(box, fill=DarkColors.GRID, width=4)

    def draw_candles(self, quote_kind: QuoteKind = QuoteKind.MID):
        self.main.delete(Tag.CANDLE)
        region = (0, 0, self.coords.width, self.coords.height)
        self.main.config(scrollregion=region)
        for ndx, candle in enumerate(self.coords.candles):
            ohlc = candle.quote(quote_kind)
            o = self.coords.y_price(ohlc.o)
            h = self.coords.y_price(ohlc.h)
            l = self.coords.y_price(ohlc.l)
            c = self.coords.y_price(ohlc.c)
            left = self.coords.x_ndx(ndx)
            right = left + self.coords.offset.far_side()
            middle = left + self.coords.offset.wick()
            self.main.create_line(
                middle, l, middle, h, fill=Color.WICK, tags=Tag.CANDLE
            )
            if ohlc.o < ohlc.c:
                self.main.create_rectangle(
                    left,
                    o,
                    right,
                    c,
                    fill=Color.BULL_FILL,
                    tags=Tag.CANDLE,
                    outline=Color.BULL_OUTLINE,
                    width=0.0,
                )
            elif ohlc.o > ohlc.c:
                self.main.create_rectangle(
                    left,
                    c,
                    right,
                    o,
                    fill=Color.BEAR_FILL,
                    tags=Tag.CANDLE,
                    outline=Color.BEAR_OUTLINE,
                    width=0.0,
                )
            else:
                self.main.create_line(
                    left, o, right, o, fill=Color.DOJI, tags=Tag.CANDLE
                )
