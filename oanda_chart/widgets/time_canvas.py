from tkinter import Canvas, Widget
from typing import Tuple, List
from statistics import median

from forex_types import Price, FracPips, Currency


from oanda_chart.env.const import Color, Tag, Const
from oanda_chart.env.fonts import Fonts
from oanda_chart.geo.scale_time import ScaleTime
from oanda_chart.geo.geo_candles import GeoCandles


class TimeCanvas(Canvas):
    HEIGHT = Const.TIME_CANVAS_HEIGHT

    def __init__(self, parent: Widget, width: int):
        Canvas.__init__(
            self,
            master=parent,
            background=Color.TIME_BG,
            width=width,
            borderwidth=0,
            bd=0,
            highlightthickness=0,
            height=self.HEIGHT,
        )

    def clear(self):
        self.delete(Tag.TIME_GRID)
        self.delete(Tag.TIME_TEXT)

    def redraw(self, geo: GeoCandles):
        self.clear()
        scroll_width: int = geo.xandles.scroll_width
        grid_list: List[Tuple[int, ScaleTime]] = geo.xandles.grid_list
        if scroll_width is None or grid_list is None:
            return
        self.configure(
            scrollregion=(0, 0, scroll_width, self.HEIGHT), width=geo.xandles.width,
        )
        pixels_left: int = geo.xandles.pixels_left
        widths = []
        for ndx in range(1, len(grid_list)):
            x_left, scale_time = grid_list[ndx - 1]
            x_right, scale_time_right = grid_list[ndx]
            upper_text, lower_text = scale_time.get_labels()
            x_left += pixels_left
            x_right += pixels_left
            width = x_right - x_left
            widths.append(width)
            x = x_left + (width // 2)
            self.create_text(
                x,
                10,
                fill=Color.TIME_TEXT,
                text=upper_text,
                tags=Tag.TIME_TEXT,
                font=Fonts.REGULAR,
            )
            self.create_text(
                x,
                30,
                fill=Color.TIME_TEXT,
                text=lower_text,
                tags=Tag.TIME_TEXT,
                font=Fonts.REGULAR,
            )
        median_width = median(widths) if widths else Const.MIN_TIME_GRID_WIDTH
        # TODO ----
        self.xview_moveto(Const.ONE_THIRD)
