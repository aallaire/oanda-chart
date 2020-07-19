"""Module of Parents of Selector classes.

The Selector is meant to be the parent of all Selector classes and
is not meant to be substantiated or used directly.

The PairSelector, GranSelector, and QuoteKindSelector, are intended
to be the parents of the actual usable selectors, and are also
not meant to be substantiated or used directly.
"""


from tkinter import Widget, Frame
from typing import Optional

from forex_types import Pair
from oanda_candles import Gran
from oanda_candles.quote_kind import QuoteKind

from oanda_chart.env.initializer import Initializer
from oanda_chart.env.link_color import LinkColor


class Selector(Frame):

    SELECT_TYPE: type = None

    def __init__(self, parent: Widget, chart_manager, color: LinkColor):
        Initializer.initialize(parent.winfo_toplevel())
        Frame.__init__(self, parent)
        self.manager = chart_manager
        self.color = color


class PairSelector(Selector):
    SELECT_TYPE: type = Pair

    def apply_pair(self, pair: Pair):
        self.manager.set_pair(self.color, pair)

    def get_pair(self):
        return self.manager.get_pair(self.color)

    def set_pair(self, pair: Optional[Pair]):
        raise NotImplemented


class GranSelector(Selector):
    SELECT_TYPE: type = Gran

    def apply_gran(self, gran: Gran):
        self.manager.set_gran(self.color, gran)

    def get_gran(self):
        return self.manager.get_gran(self.color)

    def set_gran(self, gran: Optional[Gran]):
        raise NotImplemented


class QuoteKindSelector(Selector):
    SELECT_TYPE: type = QuoteKind

    def apply_quote_kind(self, quote_kind: QuoteKind):
        self.manager.set_quote_kind(self.color, quote_kind)

    def get_quote_kind(self):
        return self.manager.get_quote_kind(self.color)

    def set_quote_kind(self, quote_kind: Optional[QuoteKind]):
        raise NotImplemented
