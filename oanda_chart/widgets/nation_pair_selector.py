"""A pair selector based on selecting two of 8 nation flags.

This pair selector is pretty unusual and might not be for everyone.
But I designed it just the way I thought a pair selector should be,
and hope some others will find it just as nifty. However, there are
no hard feelings if you want to use the more traditional drop down
menu pair selector instead.

A small national flag icon for each of the 8 currencies are arranged
either in one row, two rows, one column, or two columns.

Initially the flags are darkened so that they do not stand out
much, and they have their currency text on them (e.g EUR, USD, NZD etc).

Left mouse clicks select a currency flag and Right mouse clicks de-select it.

When no flags are selected, selecting one makes it the "anchor". It becomes
colorful (rather than darkened out) and is outlined in yellow.

Selecting another flag when there is already  an anchor causes the second
flag to become colorful, and causes a pair to be selected accordingly. For
example if the European Union flag and United States flag are selected
then the EUR/USD is selected. (Note that per forex market convention there
is no USD/EUR. Whether the USD is selected as the anchor or as the second
choice it would be the EUR/USD--with a similar convention with every
other currency pair where one is always before the other).

When a third flag is selected, the second flag is automatically
de-selected, but the anchor flag (the first one selected) is kept.
The idea is that this makes it handy to quickly check any of the eight
currencies against the other 7. It also means there can only be at
most 2 currencies selected at any one time.

If the anchor currency flag is de-selected (with a Right mouse click)
then if a second currency is also selected, it is de-selected as well
(in trials I tried the option of making the second one become the
anchor, but I found this confusing to use--also I wanted to provide
an intuitive way to go back to having nothing selected).
"""


from forex_types import Currency, Pair
from magic_kind import MagicKind
from tkinter import Frame, Label, Widget, StringVar
from tk_oddbox import Images
from typing import Union

from .initializer import Initializer
from .syntax_candy import grid


class Event(MagicKind):
    LEFT_CLICK = "<Button-1>"
    RIGHT_CLICK = "<Button-3>"


class Geometry(MagicKind):
    ONE_COLUMN = "one_column"
    TWO_COLUMNS = "two_columns"
    ONE_ROW = "one_row"
    TWO_ROWS = "two_rows"


class State(MagicKind):
    ANCHOR = "anchor"
    OFF = "off"
    ON = "on"

    @classmethod
    def get_image(cls, state, currency: Currency):
        if state == cls.OFF:
            return Images[f"{currency}_off"]
        elif state == State.ANCHOR:
            return Images[f"{currency}_anchor"]
        elif state == State.ON:
            return Images[f"{currency}_on"]
        else:
            raise ValueError(f"Unknown Selection State: {state}")


class CurrencyLabel(Label):
    def __init__(
        self,
        parent: "PairSelector",
        currency: Union[Currency, str],
        color: str,
        state: str = State.OFF,
    ):
        """Initialize label with specified currency.

        Args:
            parent: parent widget
            currency: currency that label is for.
            color: theme color (visible around edges of flag images)
            state: select state to start label in
        """
        Initializer.initialize(parent.winfo_toplevel())
        Label.__init__(self, parent, padx=0, pady=0, bg=color)
        self.selector = parent
        self.currency = Currency(currency)
        self.state = state
        self.set_state(state)
        self.bind(Event.LEFT_CLICK, self.left_click_callback)
        self.bind(Event.RIGHT_CLICK, self.right_click_callback)

    def set_state(self, state: str):
        image = State.get_image(state, self.currency)
        self.state = state
        self.config(image=image)

    def left_click_callback(self, event):
        if self.selector.anchor is None:
            self.selector.anchor = self.currency
            self.selector.on = None
            self.selector.apply_values()
        elif self.currency not in (self.selector.anchor, self.selector.on):
            self.selector.on = self.currency
            self.selector.apply_values()

    def right_click_callback(self, event):
        if self.currency == self.selector.anchor:
            self.selector.anchor = None
            self.selector.on = None
            self.selector.apply_values()
        elif self.currency == self.selector.on:
            self.selector.on = None
            self.selector.apply_values()


class PairSelector(Frame):
    def __init__(self, parent: Widget, color=None, geometry=None):
        """
            parent: parent widget
            color: theme color, defaults to green
            geometry: arrangement of flags, defaults to one column.
        """
        Initializer.initialize(parent.winfo_toplevel())
        Frame.__init__(self, parent)
        self.color = "green" if color is None else color
        self.geometry = Geometry.ONE_COLUMN if geometry is None else geometry
        self.charts = []
        self.labels = []
        self.anchor: Currency = None
        self.on: Currency = None
        self.pair_var = StringVar()
        for currency in Currency.get_list():
            label = CurrencyLabel(self, currency, color)
            self.labels.append(label)
        self.place_widgets()

    def place_widgets(self):
        """Place widgets according to geometry setting."""
        if self.geometry == Geometry.ONE_COLUMN:
            for ndx, label in enumerate(self.labels):
                grid(label, ndx, 0)
        elif self.geometry == Geometry.ONE_ROW:
            for ndx, label in enumerate(self.labels):
                grid(label, 0, ndx)
        elif self.geometry == Geometry.TWO_COLUMNS:
            for ndx in 0, 1, 2, 3:
                grid(self.labels[ndx], ndx + 1, 0)
                grid(self.labels[ndx + 4], ndx + 1, 1)
        elif self.geometry == Geometry.TWO_ROWS:
            for ndx in 0, 1, 2, 3:
                grid(self.labels[ndx], 0, ndx + 1)
                grid(self.labels[ndx + 4], 1, ndx + 1)

    def apply_values(self):
        """Update everything else based on self.anchor and self.on."""
        # Update state of labels
        for label in self.labels:
            if label.currency == self.anchor:
                label.set_state(State.ANCHOR)
            elif label.currency == self.on:
                label.set_state(State.ON)
            else:
                label.set_state(State.OFF)
        # Set Pair Value
        previous_pair = self.pair_var.get()
        if self.anchor and self.on:
            currencies = sorted([self.anchor, self.on])
            pair = Pair.from_currency(currencies[0], currencies[1])
            if pair != previous_pair:
                self.pair_var.set(pair.camel())
                for chart in self.charts:
                    chart.update_pair(pair)
        else:
            self.pair_var.set("")
            for chart in self.charts:
                chart.clear()
