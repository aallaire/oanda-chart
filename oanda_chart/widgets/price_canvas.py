from tkinter import Canvas, Widget
from typing import Tuple

from forex_types import Price, FracPips, Currency


from oanda_chart.env.const import Color, Tag, Const
from oanda_chart.env.fonts import Fonts
from oanda_chart.geo.geo_candles import GeoCandles


class PriceCanvas(Canvas):
    WIDTH = Const.PRICE_CANVAS_WIDTH

    def __init__(self, parent: Widget, height: int):
        Canvas.__init__(
            self,
            master=parent,
            background=Color.PRICE_BG,
            width=self.WIDTH,
            borderwidth=0,
            bd=0,
            highlightthickness=0,
            height=height,
        )

    def clear(self):
        self.delete(Tag.PRICE_GRID)
        self.delete(Tag.PRICE_LABEL)

    def redraw(self, geo: GeoCandles):
        self.clear()
        fpp = geo.yrids.fpp
        scroll_height = geo.yrids.scroll_height
        scroll_bot = geo.yrids.scroll_bot
        scroll_top = geo.yrids.scroll_top
        grid_list = geo.yrids.grid_list
        if (
            fpp is None
            or scroll_height is None
            or scroll_bot is None
            or scroll_top is None
            or grid_list is None
        ):
            return
        self.configure(
            scrollregion=(0, 0, self.WIDTH, scroll_height), height=geo.yrids.height,
        )
        for fp, y in grid_list:
            if fp < 0:
                continue
            front, pips, frac_pips = self.price_parse(fp, geo.pair.quote)
            self.create_text(
                4,
                y,
                text=front,
                fill=Color.DOLLAR_TEXT,
                anchor="w",
                font=Fonts.FIXED_12,
                tag=Tag.PRICE_LABEL,
            )
            self.create_text(
                45,
                y,
                text=pips,
                anchor="w",
                fill=Color.PIP_TEXT,
                font=Fonts.FIXED_12,
                tag=Tag.PRICE_LABEL,
            )
            self.create_text(
                66,
                y - 2,
                text=frac_pips,
                fill=Color.FPIP_TEXT,
                anchor="w",
                font=Fonts.FIXED_10,
                tag=Tag.PRICE_LABEL,
            )
            self.yview_moveto(Const.ONE_THIRD)

    def price_parse(self, fp_amount: FracPips, quote: Currency) -> Tuple[str, str, str]:
        digits = f"{fp_amount:07}"
        ninja = quote == Currency.JPY
        frac_pips = digits[6]
        pips = digits[4] + digits[5]
        if ninja:
            front = digits[1] + digits[2] + digits[3] + "."
        else:
            front = digits[1] + "." + digits[2] + digits[3]
        return front, pips, frac_pips
