from tkinter import Frame, Widget
from typing import Optional

from oanda_candles import Gran, Pair, QuoteKind


from oanda_chart.util.syntax_candy import grid
from oanda_chart.geo.candle_offset import CandleOffset
from oanda_chart.env.link_color import LinkColor
from oanda_chart.env.initializer import Initializer
from oanda_chart.widgets.pair_flags import Geometry
from oanda_chart.chart_widgets.chart_canvas import ChartCanvas
from oanda_chart.env.const import Const, Event, Tag


class OandaChart(Frame):

    _oanda_token: Optional[str] = None

    @classmethod
    def set_oanda_token(cls, token: str):
        """Set access token needed by load and update methods.

        Args:
            token: valid oanda token.
        """
        cls._oanda_token = token

    def __init__(
        self,
        parent: Widget,
        chart_manager,
        pair_color: LinkColor,
        gran_color: LinkColor,
        quote_kind_color: LinkColor,
        flags: bool,
    ):
        """Do NOT initialize directly, use ChartManager.get_chart method"""

        Initializer.initialize(parent.winfo_toplevel())
        Frame.__init__(self, parent)
        self.chart = ChartCanvas(self)
        self.manager = chart_manager
        self.pair_menu = chart_manager.create_pair_menu(self, pair_color)
        if flags:
            self.pair_flags = chart_manager.create_pair_flags(
                self, pair_color, geometry=Geometry.ONE_ROW
            )
        else:
            self.pair_flags = None
        self.gran_menu = chart_manager.create_gran_menu(self, gran_color)
        self.quote_kind_menu = chart_manager.create_quote_kind_menu(
            self, quote_kind_color
        )
        self.pair_color: LinkColor = pair_color
        self.gran_color: LinkColor = gran_color
        self.quote_kind_color: LinkColor = quote_kind_color
        self.pair: Optional[Pair] = None
        self.gran: Optional[Gran] = None
        self.quote_kind: Optional[QuoteKind] = None
        grid(self.pair_menu, 0, 2)
        grid(self.gran_menu, 0, 3)
        grid(self.quote_kind_menu, 0, 4)
        if flags:
            grid(self.pair_flags, 0, 1)
        grid(self.chart, 1, 0, c=5)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    # ---------------------------------------------------------------------------
    # Method for setting pair, gran, and quote_kind in chart
    # ---------------------------------------------------------------------------

    def set_pair_color(self, link_color: LinkColor):
        if self.pair_color != link_color:
            self.pair_color = link_color
            pair = self.manager.get_pair(link_color)
            self.set_pair(pair)

    def set_gran_color(self, link_color: LinkColor):
        if self.gran_color != link_color:
            self.gran_color = link_color
            gran = self.manager.get_gran(link_color)
            self.set_gran(gran)

    def set_quote_kind_color(self, link_color: LinkColor):
        if self.quote_kind_color != link_color:
            self.quote_kind_color = link_color
            quote_kind = self.manager.get_quote_kind(link_color)
            self.set_quote_kind(quote_kind)

    def apply_pair(self, pair: Pair):
        self.manager.set_pair(self.pair_color, pair)
        self.set_pair(pair)

    def apply_gran(self, gran: Gran):
        self.manager.set_gran(self.gran_color, gran)
        self.set_gran(gran)

    def apply_quote_kind(self, quote_kind: QuoteKind):
        self.manager.set_quote_kind(self.quote_kind_color, quote_kind)
        self.set_quote_kind(quote_kind)

    def set_pair(self, pair: Pair):
        """Set the pair and reload data if its new."""
        if pair != self.pair:
            self.pair = pair
            self.load_candles()

    def set_gran(self, gran: Gran):
        """Set the granularity and reload data if its new."""
        if gran != self.gran:
            self.gran = gran
            self.load_candles()

    def set_quote_kind(self, quote_kind: QuoteKind):
        """Set the quote kind and reload data if its new."""
        if quote_kind != self.quote_kind:
            self.quote_kind = quote_kind
            self.load_candles()

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------
    def load_candles(self):
        if self.pair and self.gran and self.quote_kind:
            self.chart.load(self._oanda_token, self.pair, self.gran, self.quote_kind)
            self.apply_bindings()

    def apply_bindings(self):
        self.chart.bind(Event.LEFT_CLICK, self.scroll_start)
        self.chart.bind(Event.LEFT_DRAG, self.scroll_move)
        self.chart.bind(Event.LEFT_RELEASE, self.scroll_release)
        self.chart.bind(Event.RESIZE, self.resize)
        self.chart.bind(Event.MOUSE_WHEEL, self.squeeze_or_expand)
        self.chart.bind(Event.DOUBLE_CLICK, self.toggle_price_view)

    def remove_bindings(self):
        self.chart.unbind(Event.LEFT_CLICK)
        self.chart.unbind(Event.LEFT_DRAG)
        self.chart.unbind(Event.LEFT_RELEASE)
        self.chart.unbind(Event.RESIZE)
        self.chart.unbind(Event.MOUSE_WHEEL)
        self.chart.unbind(Event.DOUBLE_CLICK)

    # --------------------------------------------------------------------------
    # Callbacks
    # --------------------------------------------------------------------------
    def scroll_start(self, event):
        self.chart.marked_x = event.x
        self.chart.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.chart.scan_dragto(event.x, event.y, gain=1)

    def scroll_release(self, event):
        shift = event.x - self.chart.marked_x
        ndx_shift = round(shift / self.chart.offset)
        self.chart.delete(Tag.CANDLE)
        self.chart.candle_ndx += ndx_shift
        if self.chart.candle_ndx < 0:
            self.chart.candle_ndx = 0
        if self.pair is not None:
            self.chart.update_candles()
            if self.chart.price_view:
                self.chart.enforce_price_view()
        self.chart.xview_moveto(Const.ONE_THIRD)
        if self.chart.end_in_sight():
            self.chart.tailing = True
            self.chart.start_tail()
        else:
            self.chart.tailing = False

    def resize(self, event):
        self.chart.apply_resize(width=event.width, height=event.height)
        if self.chart.candles:
            self.chart.apply_resize()
            self.chart.update_candles()
            self.chart.apply_resize()
            if self.chart.price_view:
                self.chart.apply_resize()
                self.chart.enforce_price_view()

    def squeeze_or_expand(self, event):
        """Squeeze candle offset or expand it according to mouse wheel direction."""
        if not self.chart.candles:
            return
        old_offset = self.chart.offset
        if event.delta > 0:
            new_offset = CandleOffset(old_offset + 1)
        elif event.delta < 0:
            new_offset = CandleOffset(old_offset - 1)
        else:
            return
        if new_offset != old_offset:
            self.chart.apply_offset(new_offset)
            if self.chart.price_view:
                self.chart.enforce_price_view()
            if self.chart.end_in_sight():
                self.chart.tailing = True
                self.chart.start_tail()
            else:
                self.chart.tailing = False

    def toggle_price_view(self, event):
        self.chart.price_view = not self.chart.price_view
