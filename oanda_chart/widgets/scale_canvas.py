from tkinter import Canvas, Widget

from forex_types import FracPips


from oanda_chart.env.const import Color, Tag, Const
from oanda_chart.env.fonts import Fonts
from oanda_chart.geo.geo_candles import GeoCandles


class ScaleCanvas(Canvas):
    HEIGHT = Const.TIME_CANVAS_HEIGHT
    WIDTH = Const.PRICE_CANVAS_WIDTH

    def __init__(self, parent: Widget):
        Canvas.__init__(
            self,
            master=parent,
            background=Color.TIME_BG,
            width=self.WIDTH,
            borderwidth=0,
            bd=0,
            highlightthickness=0,
            height=self.HEIGHT,
        )

    def clear(self):
        self.delete(Tag.SCALE_ITEM)

    def redraw(self, geo: GeoCandles):
        self.delete(Tag.SCALE_ITEM)
        if geo.yrids.scale is None or not geo.xandles.grid_list:
            return
        fp_grid: FracPips = geo.yrids.scale.interval
        if fp_grid % 10:
            pips = round(fp_grid / 10, 1)
        else:
            pips = round(fp_grid / 10)
        pip_text = f"{pips} p"
        time_text = geo.xandles.grid_list[0][1].name
        self.create_line(0, 0, self.WIDTH, 0, fill=Color.SLASH, tags=Tag.SCALE_ITEM)
        self.create_line(0, 0, 0, self.HEIGHT, fill=Color.SLASH, tags=Tag.SCALE_ITEM)
        self.create_line(
            0, 0, self.WIDTH, self.HEIGHT, fill=Color.SLASH, tags=Tag.SCALE_ITEM
        )
        self.create_text(
            57,
            8,
            fill=Color.SCALE_TEXT,
            font=Fonts.FIXED_10,
            text=pip_text,
            tags=Tag.SCALE_ITEM,
        )
        self.create_text(
            29,
            34,
            fill=Color.SCALE_TEXT,
            font=Fonts.FIXED_10,
            text=time_text,
            tags=Tag.SCALE_ITEM,
        )
