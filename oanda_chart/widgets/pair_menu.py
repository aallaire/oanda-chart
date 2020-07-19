from tkinter import Widget, StringVar, Menubutton, Menu
from forex_types import Pair
from magic_kind import MagicKind
from typing import Optional
from functools import partial

from oanda_chart.util.syntax_candy import grid
from oanda_chart.env.fonts import Fonts
from oanda_chart.widgets.selector import PairSelector


class PairMenu(PairSelector):
    def __init__(self, parent: Widget, chart_manager, color):
        PairSelector.__init__(self, parent, chart_manager, color)
        self.pair_var = StringVar()
        self.menubutton = Menubutton(
            self,
            textvariable=self.pair_var,
            font=Fonts.FIXED_14,
            width=7,
            background=color,
            foreground=color.contrast,
        )
        self.menu = Menu(
            self.menubutton,
            background=color,
            foreground=color.contrast,
            font=Fonts.FIXED_14,
        )
        self.menubutton["menu"] = self.menu
        for pair in Pair.iter_pairs():
            self.menu.add_command(
                label=pair.camel(), command=partial(self.pair_callback, pair)
            )
            if pair in self.SEPARATOR_AFTER:
                self.menu.add_separator()
        grid(self.menubutton, 0, 0)

    def set_pair(self, pair: Optional[Pair]):
        if pair is None:
            self.pair_var.set("")
        else:
            self.pair_var.set(pair.camel())

    def pair_callback(self, pair: Pair):
        self.apply_pair(pair)

    SEPARATOR_AFTER = {
        Pair.EUR_JPY,
        Pair.GBP_JPY,
        Pair.AUD_JPY,
        Pair.NZD_JPY,
        Pair.USD_JPY,
        Pair.CAD_JPY,
    }
