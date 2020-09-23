from math import ceil
from tkinter import Frame, Widget
from typing import Optional
from uuid import uuid4

from oanda_candles import Gran, Pair, QuoteKind

from oanda_chart.env.const import Color
from oanda_chart.env.const import Event
from oanda_chart.env.initializer import Initializer
from oanda_chart.env.link_color import LinkColor
from oanda_chart.geo.candle_offset import CandleOffset
from oanda_chart.geo.geo_candles import GeoCandles
from oanda_chart.selectors.pair_flags import Geometry
from oanda_chart.widgets.chart_canvas import ChartCanvas
from oanda_chart.widgets.price_canvas import PriceCanvas
from oanda_chart.widgets.scale_canvas import ScaleCanvas
from oanda_chart.widgets.time_canvas import TimeCanvas
from oanda_chart.util.syntax_candy import grid


class OandaChart(Frame):
    def __init__(
        self,
        parent: Widget,
        chart_manager,
        pair_color: LinkColor,
        gran_color: LinkColor,
        quote_kind_color: LinkColor,
        flags: bool,
        width: int,
        height: int,
    ):
        """Do NOT initialize directly, use ChartManager.get_chart method"""
        Initializer.initialize(parent.winfo_toplevel())
        # Frame.__init__(self, parent, width=width, height=height)
        Frame.__init__(self, parent)
        self.top = Frame(self, background=Color.TOP_BG)
        self.geo: Optional[GeoCandles] = None
        self.chart = ChartCanvas(self, width, height)
        self.prices = PriceCanvas(self, height)
        self.times = TimeCanvas(self, width)
        self.event_width: int = width
        self.event_height: int = height
        self.scales = ScaleCanvas(self)
        self.manager = chart_manager
        self.pair_menu = chart_manager.create_pair_menu(self.top, pair_color)
        if flags:
            self.pair_flags = chart_manager.create_pair_flags(
                self.top, pair_color, geometry=Geometry.ONE_ROW
            )
        else:
            self.pair_flags = None
        self.gran_menu = chart_manager.create_gran_menu(self.top, gran_color)
        self.quote_kind_menu = chart_manager.create_quote_kind_menu(
            self.top, quote_kind_color
        )
        self.pair_color: LinkColor = pair_color
        self.gran_color: LinkColor = gran_color
        self.quote_kind_color: LinkColor = quote_kind_color
        self.pair: Optional[Pair] = None
        self.gran: Optional[Gran] = None
        self.quote_kind: Optional[QuoteKind] = None
        self.marked_x: Optional[int] = None
        self.marked_y: Optional[int] = None
        self.price_mark: Optional[int] = None
        self.time_mark: Optional[int] = None
        self.time_event_count: Optional[int] = None
        self.run_id: Optional[str] = None
        if flags:
            grid(self.pair_flags, 0, 1)
        grid(self.pair_menu, 0, 2)
        grid(self.gran_menu, 0, 3)
        grid(self.quote_kind_menu, 0, 4)
        self.top.columnconfigure(0, weight=1)
        grid(self.top, 0, 0, c=2)
        grid(self.chart, 1, 0)
        grid(self.prices, 1, 1)
        grid(self.times, 2, 0)
        grid(self.scales, 2, 1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        # This binding needs to be on even when there is no chart data,
        # because otherwise we have no way of knowing the width and height
        # of the chart to draw geometry in.
        self.chart.bind(Event.RESIZE, self.resize)

    def set_pair(self, pair: Pair):
        """Set the pair and reload data if its new."""
        print(f"SET PAIR WITH {pair} when we have {self.pair}")
        if pair != self.pair:
            print(f"Setting pair to {pair}")
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
            if self.geo is None:
                self.load_candles()
            else:
                self.geo.update(quote_kind=quote_kind)
                self.chart.redraw(self.geo)

    def load_candles(self):
        if self.pair and self.gran and self.quote_kind:
            self.remove_bindings()
            if self.geo is None:
                width = self.event_width
                height = self.event_height
            else:
                width = self.geo.xandles.width
                height = self.geo.yrids.height
            self.geo = GeoCandles(
                width=width,
                height=height,
                pair=self.pair,
                gran=self.gran,
                quote_kind=self.quote_kind,
                offset=CandleOffset.DEFAULT,
                ndx=0,
                price_view=True,
            )
            self.chart.redraw(self.geo)
            self.prices.redraw(self.geo)
            self.scales.redraw(self.geo)
            self.times.redraw(self.geo)
            self.apply_bindings()
            self.update_runner()
        else:
            self.remove_bindings()
            self.chart.clear()
            self.prices.clear()
            self.scales.clear()
            self.times.clear()

    def apply_bindings(self):
        self.chart.bind(Event.LEFT_CLICK, self.scroll_start)
        self.chart.bind(Event.LEFT_DRAG, self.scroll_move)
        self.chart.bind(Event.LEFT_RELEASE, self.scroll_release)
        self.chart.bind(Event.MOUSE_WHEEL, self.squeeze_or_expand)
        self.scales.bind(Event.LEFT_CLICK, self.go_home)
        self.prices.bind(Event.LEFT_CLICK, self.prices_scroll_start)
        self.prices.bind(Event.LEFT_DRAG, self.prices_scroll_move)
        self.chart.bind(Event.DOUBLE_CLICK, self.apply_price_view)
        self.prices.bind(Event.DOUBLE_CLICK, self.apply_price_view)
        self.times.bind(Event.LEFT_CLICK, self.times_scroll_start)
        self.times.bind(Event.LEFT_DRAG, self.times_squeeze_or_expand)
        self.times.bind(Event.DOUBLE_CLICK, self.default_squeeze)
        self.chart.bind(Event.LEFT, self.step_left)
        self.chart.bind(Event.RIGHT, self.step_right)
        self.chart.bind(Event.UP, self.step_up)
        self.chart.bind(Event.DOWN, self.step_down)
        self.chart.bind(Event.RETURN, self.apply_price_view)

    def remove_bindings(self):
        self.chart.unbind(Event.LEFT_CLICK)
        self.chart.unbind(Event.LEFT_DRAG)
        self.chart.unbind(Event.LEFT_RELEASE)
        self.chart.unbind(Event.MOUSE_WHEEL)
        self.chart.unbind(Event.DOUBLE_CLICK)
        self.scales.unbind(Event.LEFT_CLICK)
        self.prices.unbind(Event.LEFT_CLICK)
        self.prices.unbind(Event.LEFT_DRAG)
        self.prices.unbind(Event.DOUBLE_CLICK)

    def scroll_start(self, event):
        self.marked_x = event.x
        self.marked_y = event.y
        self.chart.scan_mark(event.x, event.y)
        self.prices.scan_mark(0, event.y)
        self.times.scan_mark(event.x, 0)

    def scroll_move(self, event):
        x_delta = abs(event.x - self.marked_x)
        y_delta = abs(event.y - self.marked_y)
        self.update_runner()
        self.chart.scan_dragto(event.x, event.y, gain=1)
        self.prices.scan_dragto(0, event.y, gain=1)
        self.times.scan_dragto(event.x, 0, gain=1)
        self.chart.draw_badge(self.geo)
        self.chart.draw_price_grid(self.geo)
        self.chart.draw_time_grid(self.geo)
        self.chart.draw_candles(self.geo)

    def step_up(self, event):
        self.geo.update(price_view=False)
        y_shift = -1 * ceil(self.geo.yrids.height / 4)
        self.update_runner()
        self.chart.scan_dragto(0, y_shift)
        self.geo.shift(0, y_shift)
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def step_down(self, event):
        self.geo.update(price_view=False)
        y_shift = ceil(self.geo.yrids.height / 4)
        self.update_runner()
        self.chart.scan_dragto(0, y_shift)
        self.geo.shift(0, y_shift)
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def step_left(self, event):
        x_shift = -1 * ceil(self.geo.xandles.width / 4)
        self.chart.scan_dragto(x_shift, 0)
        self.update_runner()
        self.geo.shift(x_shift, 0)
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def step_right(self, event):
        x_shift = ceil(self.geo.xandles.width / 4)
        self.chart.scan_dragto(x_shift, 0)
        self.geo.shift(x_shift, 0)
        self.update_runner()
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def prices_scroll_start(self, event):
        self.price_mark = event.y

    def times_scroll_start(self, event):
        self.time_mark = event.x
        self.time_event_count = 0

    def prices_scroll_move(self, event):
        sensitivity = 500.0  # lower is more sensitive
        movement = event.y - self.price_mark
        new_fpp = self.geo.yrids.fpp * (float(sensitivity + movement) / sensitivity)
        if (movement > 0 and new_fpp > 175) or (movement < 0 and new_fpp < 0.05):
            # Around 175 or larger even the entire chart of monthly candles are short.
            # and the negative price part of chart is starting to show up. While for
            # fpp's smaller than 0.05, even the lowest time frame candles are too tall
            # to make out. So we disallow changing fpp beyond these limits.
            return
        self.geo.update(fpp=new_fpp)
        self.update_runner()
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.price_mark = event.y

    def scroll_release(self, event):
        self.chart.focus_force()
        shift_x = self.marked_x - event.x
        shift_y = self.marked_y - event.y
        if abs(shift_y) > abs(shift_x) * 2 and abs(shift_y) > 100:
            # User is trying to move vertically, so turn off price_view
            self.geo.update(price_view=False)
        self.chart.scan_dragto(event.x, event.y, gain=1)
        self.geo.shift(shift_x, shift_y)
        self.update_runner()
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def go_home(self, event):
        self.geo.xandles.go_home()
        self.geo.update(price_view=True)
        self.chart.redraw(self.geo)
        self.geo.yrids.view_set(self.geo.xandles)
        self.update_runner()
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def resize(self, event):
        self.event_width = event.width
        self.event_height = event.height
        if self.geo is None:
            return
        self.geo.update(
            width=event.width, height=event.height, price_view=self.geo.price_view
        )
        self.update_runner()
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def squeeze_or_expand(self, event):
        old_offset = self.geo.xandles.offset
        if event.delta > 0:
            new_offset = CandleOffset(old_offset + 1)
        elif event.delta < 0:
            new_offset = CandleOffset(old_offset - 1)
        else:
            return
        self.geo.update(offset=new_offset, price_view=self.geo.price_view)
        self.update_runner()
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def times_squeeze_or_expand(self, event):
        delta = self.time_mark - event.x
        old_offset = self.geo.xandles.offset
        # If we counted every event, mouse movement would be too sensitive, so
        # we enumerate the events and only move one out of 10 of them.
        self.time_event_count += 1
        if self.time_event_count % 10:
            return
        if delta > 0:
            new_offset = CandleOffset(old_offset + 1)
        elif delta < 0:
            new_offset = CandleOffset(old_offset - 1)
        else:
            return
        self.geo.update(offset=new_offset, price_view=self.geo.price_view)
        self.update_runner()
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def default_squeeze(self, event):
        new_offset = CandleOffset.DEFAULT
        self.geo.update(offset=new_offset, price_view=self.geo.price_view)
        self.update_runner()
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)
        self.times.redraw(self.geo)

    def apply_price_view(self, event):
        self.geo.update(price_view=True)
        self.update_runner()
        self.chart.redraw(self.geo)
        self.prices.redraw(self.geo)
        self.scales.redraw(self.geo)

    def update_runner(self):
        if (
            self.run_id is None
            and self.geo.xandles.showing_recent
            and self.pair is not None
        ):
            run_id = self.run_id = str(uuid4())
            self.after(100, self._inner_update_runner, run_id)

    def _inner_update_runner(self, run_id: str):
        print(f"Inner Update Runner, self.pair is {self.pair}")
        if not self.geo.xandles.showing_recent or self.pair is not None:
            self.run_id = None
        if self.run_id == run_id:
            print(f"REFRESHING!!! with self.run_id {self.run_id} and run_id {run_id}")
            self.geo.refresh()
            self.chart.redraw(self.geo)
            self.prices.redraw(self.geo)
            self.scales.redraw(self.geo)
            self.times.redraw(self.geo)
            self.after(5000, self._inner_update_runner, run_id)
