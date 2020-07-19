from tkinter import Widget, StringVar, Menubutton, Menu
from oanda_candles.quote_kind import QuoteKind
from typing import Optional
from functools import partial

from oanda_chart.util.syntax_candy import grid
from oanda_chart.env.fonts import Fonts
from oanda_chart.widgets.selector import QuoteKindSelector


class QuoteKindMenu(QuoteKindSelector):
    def __init__(self, parent: Widget, chart_manager, color):
        QuoteKindSelector.__init__(self, parent, chart_manager, color)
        self.quote_kind_var = StringVar()
        self.quote_kind_var.set(QuoteKind.MID.name)
        self.menubutton = Menubutton(
            self,
            textvariable=self.quote_kind_var,
            font=Fonts.FIXED_14,
            width=4,
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
        self.menu.add_command(
            self.menu.add_command(
                label=QuoteKind.ASK.name,
                command=partial(self.quote_kind_callback, QuoteKind.ASK),
            )
        )
        self.menu.add_command(
            self.menu.add_command(
                label=QuoteKind.MID.name,
                command=partial(self.quote_kind_callback, QuoteKind.MID),
            )
        )
        self.menu.add_command(
            self.menu.add_command(
                label=QuoteKind.BID.name,
                command=partial(self.quote_kind_callback, QuoteKind.BID),
            )
        )
        grid(self.menubutton, 0, 0)
        self.apply_quote_kind(self.quote_kind_var.get())

    def set_quote_kind(self, quote_kind: Optional[QuoteKind]):
        self.quote_kind_var.set(quote_kind)

    def quote_kind_callback(self, quote_kind: QuoteKind):
        self.apply_quote_kind(quote_kind)
