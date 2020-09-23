from tkinter import Widget, StringVar, Menubutton, Menu
from oanda_candles import Gran
from typing import Optional
from functools import partial

from oanda_chart.util.syntax_candy import grid
from oanda_chart.env.fonts import Fonts
from oanda_chart.selectors.selector import GranSelector


class GranMenu(GranSelector):
    def __init__(self, parent: Widget, chart_manager, color):
        GranSelector.__init__(self, parent, chart_manager, color)
        self.gran_var = StringVar()
        self.menubutton = Menubutton(
            self,
            textvariable=self.gran_var,
            font=Fonts.FIXED_14,
            width=10,
            background=color,
            foreground=color.contrast,
        )
        self.menu = Menu(
            self.menubutton,
            background=color,
            foreground=color.contrast,
            font=Fonts.FIXED_14,
            tearoff=False,
        )
        self.menubutton["menu"] = self.menu
        for item in self.MENU_LAYOUT:
            if item is None:
                self.menu.add_separator()
            else:
                self.menu.add_command(
                    label=item.name, command=partial(self.gran_callback, item)
                )
        grid(self.menubutton, 0, 0)

    def set_gran(self, gran: Optional[Gran]):
        if gran is None:
            self.gran_var.set("gran")
            self.menubutton.config(foreground="grey")
        else:
            self.gran_var.set(gran.name)
            self.menubutton.config(foreground=self.color.contrast)

    def gran_callback(self, gran: Gran):
        self.apply_gran(gran)

    MENU_LAYOUT = (
        Gran.M,
        Gran.W,
        Gran.D,
        None,
        Gran.H12,
        Gran.H8,
        Gran.H6,
        Gran.H4,
        Gran.H3,
        Gran.H2,
        Gran.H1,
        None,
        Gran.M30,
        Gran.M15,
        Gran.M10,
        Gran.M5,
        Gran.M4,
        Gran.M2,
        Gran.M1,
    )
    """
        None,
        Gran.S30,
        Gran.S15,
        Gran.S10,
        Gran.S5,
    )
    """
