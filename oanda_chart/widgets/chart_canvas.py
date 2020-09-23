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


from tkinter import Widget, Canvas
from math import floor


from oanda_candles import QuoteKind

from oanda_chart.env.const import (
    CandleColor,
    Color,
    Const,
    Tag,
    UnfinishedCandleColor,
)
from oanda_chart.geo.geo_candles import GeoCandles
from oanda_chart.env.fonts import Fonts


class ChartCanvas(Canvas):
    def __init__(self, parent: Widget, width: int, height: int):
        """Initialize chart canvas.
        
        Args:
            parent: tkinter widget canvas should belong to
            width: pixel width of candle area
            height: pixel height of candle area
        Attributes (not all set upon initialization).
        """
        Canvas.__init__(
            self,
            master=parent,
            background=Color.BACKGROUND,
            borderwidth=0,
            bd=0,
            highlightthickness=0,
            width=width,
            height=height,
        )

    def clear(self):
        self.delete(Tag.BADGE)
        self.delete(Tag.CANDLE)
        self.delete(Tag.TIME_GRID)
        self.delete(Tag.PRICE_GRID)
        self.delete(Tag.MIST)

    def redraw(self, geo):
        self.clear()
        self.config(
            scrollregion=(0, 0, geo.xandles.scroll_width, geo.yrids.scroll_height)
        )
        self.xview_moveto(Const.ONE_THIRD)
        self.yview_moveto(Const.ONE_THIRD)
        self.draw_badge(geo)
        self.draw_mist(geo)
        self.draw_time_grid(geo)
        self.draw_price_grid(geo)
        self.draw_candles(geo)

    def draw_mist(self, geo: GeoCandles):
        y1 = 0
        y2 = geo.yrids.scroll_height
        # Draw future mist
        x1 = geo.xandles.pixels_right
        x2 = geo.xandles.scroll_width
        last_candle = geo.xandles.get_candle(0)
        if last_candle is not None and not last_candle.complete:
            # extend mist to cover incomplete last candle
            x1 -= geo.xandles.offset + floor(geo.xandles.offset / 4)
        if x2 > x1:
            self.create_rectangle(x1, y1, x2, y2, fill=Color.MIST, tags=Tag.MIST)
        # Draw historical mist
        x1 = 0
        x2 = geo.xandles.pixels_left
        if x2 > x1:
            self.create_rectangle(x1, y1, x2, y2, fill=Color.MIST, tags=Tag.MIST)

    def clear_badge(self):
        self.delete(Tag.BADGE)

    def draw_badge(self, geo: GeoCandles):
        self.clear_badge()
        if geo.yrids.height > 820 and geo.xandles.width > 1700:
            font_big = Fonts.TITAN
            font_small = Fonts.GIANT
            y_offset = 200
        elif geo.yrids.height > 500 and geo.xandles.width > 1000:
            font_big = Fonts.GIANT
            font_small = Fonts.HUGE
            y_offset = 100
        elif geo.yrids.height > 200 and geo.xandles.width > 400:
            font_big = Fonts.HUGE
            font_small = Fonts.BIG
            y_offset = 60
        else:
            font_big = Fonts.BIG
            font_small = Fonts.BIG
            y_offset = 30
        view_x = round(geo.xandles.width / 2)
        view_y = round(geo.yrids.height / 2)
        x = self.canvasx(view_x)
        y = self.canvasy(view_y)
        gran_text = geo.gran.name.replace("minute", "min").capitalize()
        quote_text = str(geo.quote_kind).capitalize()
        text_big = f"{geo.pair.camel()}"
        text_small = f"{gran_text}  {quote_text}"
        self.create_text(
            x,
            y - y_offset,
            text=text_big,
            fill=Color.BADGE,
            tags=Tag.BADGE,
            font=font_big,
            justify="center",
        )
        self.create_text(
            x,
            y + y_offset,
            text=text_small,
            fill=Color.BADGE,
            tags=Tag.BADGE,
            font=font_small,
            justify="center",
        )

    def draw_price_grid(self, geo: GeoCandles):
        for fp, y in geo.yrids.grid_list:
            if fp >= 0:
                self.create_line(
                    0,
                    y,
                    geo.xandles.scroll_width,
                    y,
                    fill=Color.GRID,
                    tags=Tag.PRICE_GRID,
                )

    def draw_time_grid(self, geo: GeoCandles):
        first_one = True
        for pixels, scale_time in geo.xandles.grid_list[:-1]:
            if not first_one:
                y = geo.xandles.pixels_left + pixels
                self.create_line(
                    y,
                    0,
                    y,
                    geo.yrids.scroll_height,
                    fill=Color.GRID,
                    tags=Tag.TIME_GRID,
                )
            first_one = False

    def draw_candles(self, geo: GeoCandles):
        for left, candle in geo.xandles.display_list:
            ohlc = candle.quote(geo.quote_kind)
            o = geo.yrids.price_to_y(ohlc.o)
            h = geo.yrids.price_to_y(ohlc.h)
            l = geo.yrids.price_to_y(ohlc.l)
            c = geo.yrids.price_to_y(ohlc.c)
            right = left + geo.xandles.offset.far_side()
            middle = left + geo.xandles.offset.wick()
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
