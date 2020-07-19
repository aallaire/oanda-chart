from typing import Optional

from forex_types import Pair
from tkinter import StringVar


class Linker:
    def __init__(self):
        self.pair_var = StringVar()
        self.charts = []
        self.selectors = []

    def link_chart(self, chart):
        if chart not in self.charts:
            self.charts.append(chart)

    def unlink_chart(self, chart):
        if chart in self.charts:
            self.charts.remove(chart)

    def link_selector(self, selector):
        if selector not in self.selectors:
            self.selectors.append(selector)


class ThemedLinker(Linker):
    # These are set by initializer.initialize() (they can not be set until
    # after the tkinter root is set because they have StringVar objects).
    RED: "ThemedLinker" = None
    ORANGE: "ThemedLinker" = None
    YELLOW: "ThemedLinker" = None
    GREEN: "ThemedLinker" = None
    BLUE: "ThemedLinker" = None

    def __init__(self, color: str):
        Linker.__init__(self)
        self.color = color
