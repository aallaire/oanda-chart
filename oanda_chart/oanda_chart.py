from oanda_candles import CandleSequence, Gran, CandleRequester
from oanda_candles.candle import Candle
from oanda_candles.ohlc import Ohlc
from forex_types import Pair, Price, FracPips
from oanda_candles.quote_kind import QuoteKind
from tkinter import ALL, Canvas, CENTER, Frame, Widget
from typing import Optional
from oanda_chart.syntax_candy import grid
from oanda_chart.fonts import Fonts
from oanda_chart.colors import DarkColors
from magic_kind import MagicKind
from oanda_chart.price_coords import PriceCoords


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

    def __init__(self, parent: Widget):
        Frame.__init__(self, parent)
        self.canvas = Canvas(
            self,
            width=self.WIDTH,
            height=self.HEIGHT,
            background=self.Colors.BACKGROUND,
        )
        self.pair: Optional[Pair] = None
        self.gran: Optional[Gran] = None
        self.quote_kind: Optional[QuoteKind] = None
        self.candles: Optional[CandleSequence] = None
        self.coords: Optional[PriceCoords] = None
        grid(self.canvas, 0, 0)

    def clear(self):
        """Clear away all loaded instance data and elements of canvas."""
        self.canvas.delete(Tags.ALL)
        self.pair = self.gran = self.quote_kind = None
        self.candles = self.coords = None

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

    def load(self, pair: Pair, gran: Gran, quote_kind: QuoteKind):
        """Load candles (requires oanda token to be set already).

        Args:
            pair: forex pair to chart prices for. e.g. Pair.EUR_USD
            gran: granularity/duration of each candle, e.g. Gran.H4
            quote_kind: whether Bid, Mid, or Ask price
        """
        self.pair = pair
        self.gran = gran
        self.quote_kind = quote_kind
        requester = CandleRequester(self._oanda_token, pair, gran)
        self.candles = requester.request(count=self.NUM_CANDLE)
        self.canvas.delete(Tags.ALL)
        self._update_badge()
        if not self.candles:
            return
        self.coords: PriceCoords = PriceCoords.from_candle_sequence(
            self.HEIGHT, self.CANDLE_OFFSET, self.candles
        )
        for num in range(len(self.candles)):
            self._draw_candle(num)

    def update(self, token=None):
        pass

    def _update_badge(self):
        self.canvas.delete(Tags.BADGE)
        kwargs = {
            "fill": self.Colors.BADGE,
            "justify": CENTER,
            "tags": Tags.BADGE,
            "text": f"{self.gran}\n{self.pair.camel()}\n{self.quote_kind}",
        }
        self.canvas.create_text(
            self.MID_X, self.MID_Y, font=Fonts.GIANT, **kwargs,
        )
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
