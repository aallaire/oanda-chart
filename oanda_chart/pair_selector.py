from forex_types import Currency, Pair
from magic_kind import MagicKind
from tkinter import Frame, Label, Widget, StringVar, SUNKEN
from tk_oddbox import Images
from typing import Union

from .initializer import Initializer
from .syntax_candy import grid
from .fonts import Fonts
from .colors import SelectorColors


class Event(MagicKind):
    LEFT_CLICK = "<Button-1>"
    RIGHT_CLICK = "<Button-3>"


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
        state: str = State.OFF,
    ):
        """Initialize label with specified currency.

        Args:
            parent: parent widget
            currency: currency that label is for.
            state: select state to start label in
        """
        Initializer.initialize(parent.winfo_toplevel())
        Label.__init__(self, parent)
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
    def __init__(self, parent: Widget, *charts):
        """
            parent: parent widget
            charts: zero or more OandaChart objects selection controls.
        """
        Initializer.initialize(parent.winfo_toplevel())
        Frame.__init__(self, parent)
        self.charts = charts
        self.labels = []
        self.anchor: Currency = None
        self.on: Currency = None
        self.pair_var = StringVar()
        self.pair_var.set("")
        for currency in Currency.get_list():
            label = CurrencyLabel(self, currency)
            self.labels.append(label)
        self.pair_label = Label(
            self,
            textvariable=self.pair_var,
            relief=SUNKEN,
            width=6,
            font=Fonts.FIXED_16,
            bg=SelectorColors.PAIR_BG,
            fg=SelectorColors.PAIR_FG,
        )
        self.place_widgets()

    def place_widgets(self):
        """Override this if you wish widgets to be placed differently."""
        for ndx in 0, 1, 2, 3:
            grid(self.labels[ndx], 0, ndx + 1)
            grid(self.labels[ndx + 4], 1, ndx + 1)
        self.pair_label.config(font=Fonts.FIXED_20)
        grid(self.pair_label, 0, 0, r=2)

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
