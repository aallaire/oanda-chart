from tkinter import ALL, Canvas, CENTER, Frame, Widget, StringVar
from typing import Optional

from oanda_candles import CandleSequence, Gran, CandleRequester
from oanda_candles.ohlc import Ohlc
from oanda_candles.quote_kind import QuoteKind
from oanda_candles.candle import Candle
from forex_types import Pair, Price
from magic_kind import MagicKind

from oanda_chart.util.price_coords import PriceCoords
from oanda_chart.util.price_scale import PriceScale
from oanda_chart.util.syntax_candy import grid
from oanda_chart.env.fonts import Fonts
from oanda_chart.env.colors import DarkColors
from oanda_chart.env.const import SelectType
from oanda_chart.env.link_color import LinkColor
from oanda_chart.env.initializer import Initializer


class Tags(MagicKind):
    ALL = ALL
    BADGE = "badge"
    CANDLE = "candle"
    LINE = "line"
    RECTANGLE = "rectangle"


class OandaChart(Frame):

    Colors = DarkColors

    _oanda_token: Optional[str] = None
    WIDTH: int = 1284
    HEIGHT: int = 720

    MID_X = WIDTH / 2
    MID_Y = HEIGHT / 2

    NUM_CANDLE = 107
    CANDLE_WIDTH = 9
    CANDLE_GAP = 3
    CANDLE_OFFSET = CANDLE_WIDTH + CANDLE_GAP

    TAG_TOP = 60
    TAG_BOTTOM = HEIGHT - TAG_TOP

    TAG_LEFT = 60
    TAG_RIGHT = WIDTH - TAG_LEFT

    PAD = 100  # Fractional pips beyond prices to pad chart with.

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
    ):
        """Do NOT initialize directly, use ChartManager.get_chart method"""

        Initializer.initialize(parent.winfo_toplevel())
        Frame.__init__(self, parent)
        self.canvas = Canvas(
            self,
            width=self.WIDTH,
            height=self.HEIGHT,
            background=self.Colors.BACKGROUND,
        )
        self.manager = chart_manager
        self.candles: Optional[CandleSequence] = None
        self.coords: Optional[PriceCoords] = None
        self.price_scale: Optional[PriceScale] = None
        self.pair_color: LinkColor = pair_color
        self.gran_color: LinkColor = gran_color
        self.quote_kind_color: LinkColor = quote_kind_color
        self.pair: Optional[Pair] = None
        self.gran: Optional[Gran] = None
        self.quote_kind: Optional[QuoteKind] = None
        grid(self.canvas, 0, 0)

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

    # ---------------------------------------------------------------------------
    # Methods for drawing/clearing elements from chart.
    # ---------------------------------------------------------------------------

    def load_candles(self):
        """If the pair, gran, and quote_kind are set, load/reload candles."""
        if self.pair and self.gran and self.quote_kind:
            print(f"pair is {self.pair} of type {type(self.pair)}")
            print(f"gran is {self.gran} of type {type(self.gran)}")
            print(f"quote_kind is {self.quote_kind} of type {type(self.quote_kind)}")
            requester = CandleRequester(self.manager.token, self.pair, self.gran)
            self.candles = requester.request(count=self.NUM_CANDLE)
            self.canvas.delete(Tags.ALL)
            if self.candles:
                self.coords: PriceCoords = PriceCoords.from_candle_sequence(
                    self.HEIGHT, self.CANDLE_OFFSET, self.candles
                )
                self.price_scale = PriceScale(self.pair, self.coords)
                self._draw_items()
        else:
            self.canvas.delete(Tags.ALL)

    def clear(self):
        """Clear away all loaded instance data and elements of canvas."""
        self.canvas.delete(Tags.ALL)
        self.pair = self.gran = self.quote_kind = None
        self.candles = self.coords = self.price_scale = None

    def create_priceline(self, price: Price, **kwargs):
        """Create horizontal line across canvas at given price.

        Args:
            price: Price to draw horizontal line at
            **kwargs: keyword arguments to pass to canvas create_line method
        """
        y = self.coords.y(price)
        self.canvas.create_line(0, y, self.WIDTH, y, tags=Tags.LINE, **kwargs)

    def create_rectangle(
        self, num1: int, price1: Price, num2: int, price2: Price, **kwargs,
    ):
        """Create box based on candle index/price coordinates.

        Args:
            num1: x coordinate based on candles from left.
            price1: y coordinate based on price.
            num2: x coordinate based on candles from left.
            price2: y coordinate based on price.
            **kwargs: keyword arguments to pass to canvas create_rectangle method
        """
        x1, y1, x2, y2 = self.coords.bbox(num1, price1, num2, price2)
        self.canvas.create_rectangle(x1, y1, x2, y2, tags=Tags.RECTANGLE, **kwargs)

    # ---------------------------------------------------------------------------
    # Internal Methods, not for public use.
    # ---------------------------------------------------------------------------

    def _draw_candle(self, num: int):
        """Draw candle body for candle at specified position in sequence."""
        candle: Candle = self.candles[num]
        ohlc: Ohlc = candle.quote(self.quote_kind)
        # Find left, middle, and right coordinates of candle
        left = self.coords.x(num)
        right = left + self.CANDLE_WIDTH
        middle = round((left + right) / 2)
        # Find price coordinates of candle
        y_open = self.coords.y(ohlc.o)
        y_high = self.coords.y(ohlc.h)
        y_low = self.coords.y(ohlc.l)
        y_close = self.coords.y(ohlc.c)
        # Draw candle body as either Bullish, Bearish, or Doji
        pixel_height = y_open - y_close
        if pixel_height > 2:
            self.canvas.create_rectangle(
                left, y_open, right, y_close, tags=Tags.CANDLE, fill=self.Colors.BULL
            )
        elif pixel_height < -2:
            self.canvas.create_rectangle(
                left, y_open, right, y_close, tags=Tags.CANDLE, fill=self.Colors.BEAR
            )
        else:
            y = round((y_open + y_close) / 2)
            self.canvas.create_line(
                left, y, right, y, tags=Tags.CANDLE, fill=self.Colors.DOJI, width=2
            )
        # Draw upper wick
        y_top = min(y_open, y_close)
        self.canvas.create_line(middle, y_top, middle, y_high, fill=self.Colors.WICK)
        # Draw lower wick
        y_bottom = max(y_open, y_close)
        self.canvas.create_line(middle, y_bottom, middle, y_low, fill=self.Colors.WICK)

    def _draw_items(self):
        self.canvas.delete(Tags.ALL)
        # draw text badges with info in corners
        kwargs = {
            "fill": self.Colors.BADGE,
            "justify": CENTER,
            "tags": Tags.BADGE,
            "text": f"{self.pair.camel()}\n{self.gran.name}\n{self.quote_kind}\n{self.price_scale.interval}",
        }
        self.canvas.create_text(
            self.TAG_LEFT, self.TAG_TOP, font=Fonts.TIMES, **kwargs,
        )
        self.canvas.create_text(
            self.TAG_RIGHT, self.TAG_TOP, font=Fonts.TIMES, **kwargs,
        )
        self.canvas.create_text(
            self.TAG_LEFT, self.TAG_BOTTOM, font=Fonts.TIMES, **kwargs,
        )
        self.canvas.create_text(
            self.TAG_RIGHT, self.TAG_BOTTOM, font=Fonts.TIMES, **kwargs,
        )
        # Draw grid lines.
        for price in self.price_scale:
            self.create_priceline(price, fill=self.Colors.GRID)
        # Draw candles
        for num in range(len(self.candles)):
            self._draw_candle(num)
