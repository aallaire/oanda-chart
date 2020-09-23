import tkinter
from typing import Optional

from forex_types import Pair
from oanda_candles import CandleMeister, Gran
from oanda_candles.quote_kind import QuoteKind

from oanda_chart.env.link_color import LinkColor

from oanda_chart.widgets.oanda_chart import OandaChart
from oanda_chart.selectors.gran_menu import GranMenu
from oanda_chart.selectors.pair_menu import PairMenu
from oanda_chart.selectors.pair_flags import Geometry, PairFlags
from oanda_chart.selectors.quote_kind_menu import QuoteKindMenu


class ChartManager:
    def __init__(self, token: str, real: bool = False):
        """Initialize manager.

        Args:
            token: oanda V20 access token used to get candle data
        """
        CandleMeister.init_meister(token, real=real)
        self.charts = set()
        self.pair_selectors = set()
        self.gran_selectors = set()
        self.quote_kind_selectors = set()
        self.pair_data = {}
        self.gran_data = {}
        self.quote_kind_data = {}

    def get_pair(self, color: LinkColor) -> Optional[Pair]:
        return self.pair_data.get(color)

    def get_gran(self, color: LinkColor) -> Optional[Gran]:
        return self.gran_data.get(color)

    def get_quote_kind(self, color: LinkColor) -> Optional[QuoteKind]:
        return self.quote_kind_data.get(color)

    def set_pair(self, color: LinkColor, pair: Optional[Pair]):
        if pair != self.pair_data.get(color):
            self.pair_data[color] = pair
            for chart in self.charts:
                if chart.pair_color == color:
                    chart.set_pair(pair)
            for pair_selector in self.pair_selectors:
                if pair_selector.color == color:
                    pair_selector.set_pair(pair)

    def set_gran(self, color: LinkColor, gran: Optional[Gran]):
        if gran != self.gran_data.get(color):
            self.gran_data[color] = gran
            for chart in self.charts:
                if chart.gran_color == color:
                    chart.set_gran(gran)
            for gran_selector in self.gran_selectors:
                if gran_selector.color == color:
                    gran_selector.set_gran(gran)

    def set_quote_kind(self, color: LinkColor, quote_kind: Optional[QuoteKind]):
        if quote_kind != self.quote_kind_data.get(color):
            self.quote_kind_data[color] = quote_kind
            for chart in self.charts:
                if chart.quote_kind_color == color:
                    chart.set_quote_kind(quote_kind)
            for quote_kind_selector in self.quote_kind_selectors:
                if quote_kind_selector.color == color:
                    quote_kind_selector.set_quote_kind(quote_kind)

    def create_chart(
        self,
        parent: tkinter.Widget,
        pair_color: LinkColor = LinkColor.ChartDefault,
        gran_color: LinkColor = LinkColor.ChartDefault,
        quote_kind_color: LinkColor = LinkColor.ChartDefault,
        flags: bool = False,
        width: int = 0,
        height: int = 0,
    ) -> OandaChart:
        """Create Oanda Chart.

        Note that the width and height are for dimensions of the view area
        that shows candles. The height also pertains to the height of the price
        scale to the right, and the width to the time scale on bottom. The width
        and height of the entire OandaChart frame will be larger since it includes
        more than just the candle area.

        Args:
            parent: tkinter widget that chart will belong to.
            pair_color: LinkColor for pair that is selected
            gran_color: LinkColor for granularity that is selected
            quote_kind_color: LinkColor for quote kind that is selected
            flags: option to include flag icon pair selector in chart.
            width: width of candle area in pixels (chart widget will be larger).
            height: height of candle area in pixels (chart widget will be larger).
        Returns:
            OandaChart Frame
        """
        chart = OandaChart(
            parent, self, pair_color, gran_color, quote_kind_color, flags, width, height
        )
        chart.set_pair(self.get_pair(pair_color))
        chart.set_gran(self.get_gran(gran_color))
        chart.set_quote_kind(self.get_quote_kind(quote_kind_color))
        self.charts.add(chart)
        return chart

    def create_pair_menu(
        self, parent: tkinter.Widget, color: LinkColor = LinkColor.ChartDefault
    ) -> PairMenu:
        pair_menu = PairMenu(parent, self, color)
        pair_menu.set_pair(self.get_pair(color))
        self.pair_selectors.add(pair_menu)
        return pair_menu

    def create_pair_flags(
        self,
        parent: tkinter.Widget,
        color: LinkColor = LinkColor.ChartDefault,
        geometry: Optional[Geometry] = None,
    ) -> PairFlags:
        pair_flags = PairFlags(parent, self, color, geometry)
        pair_flags.set_pair(self.get_pair(color))
        self.pair_selectors.add(pair_flags)
        return pair_flags

    def create_gran_menu(
        self, parent: tkinter.Widget, color: LinkColor = LinkColor.ChartDefault
    ) -> GranMenu:
        gran_menu = GranMenu(parent, self, color)
        gran_menu.set_gran(self.get_gran(color))
        self.gran_selectors.add(gran_menu)
        return gran_menu

    def create_quote_kind_menu(
        self, parent: tkinter.Widget, color: LinkColor = LinkColor.ChartDefault,
    ) -> QuoteKindMenu:
        quote_kind_menu = QuoteKindMenu(parent, self, color)
        quote_kind_menu.set_quote_kind(self.get_quote_kind(color))
        self.quote_kind_selectors.add(quote_kind_menu)
        return quote_kind_menu
