import math
from typing import List, Optional, Tuple

from oanda_candles import Candle
from forex_types import FracPips, Price
from time_int import TimeInt

from oanda_chart.geo.candles_element import CandlesElement
from oanda_chart.util.candle_range import get_candle_range
from oanda_chart.geo.candle_offset import CandleOffset

FRAC_PIP_MIN: FracPips = FracPips(0)
FRAC_PIP_MAX: FracPips = FracPips(1_000_000)


class Coords:

    DEFAULT_OFFSET = 15
    DEFAULT_FPP = 10
    DEFAULT_WIDTH = 6000
    DEFAULT_HEIGHT = 3000

    RIGHT_PAD: int = 100  # Pixels to right of most recent candle.
    LEFT_PAD: int = 200  # Pixels to the left of oldest candle.

    def __init__(
        self,
        candles: Optional[CandlesElement] = None,
        offset: int = DEFAULT_OFFSET,
        fpp: int = DEFAULT_FPP,
    ):
        """Initialize coordinate structure for chart canvas.

        Args:
            candles: candles element coords apply to.
            offset: how many pixels between starts of candles
            fpp: number of fractional pips in height of one pixel.
        """
        assert fpp >= 1
        assert offset >= 1
        # Direct independent attributes, set from args.
        self.candles = candles
        self.offset: CandleOffset = CandleOffset(offset)
        self.fpp: int = fpp
        # Derived attributes, set to None for now, will be set by update.
        self.high: Optional[FracPips] = None  # Fractional pip price at top of canvas
        self.low: Optional[FracPips] = None  # Fractional pip price at bottom of canvas
        self.width: Optional[int] = None  # Width of canvas in pixels
        self.height: Optional[int] = None  # Height of canvas in pixels
        # Call update to give derived attributes correct values.
        self._update()

    def report(self):
        lines = [
            f"candles    : {len(self.candles)} candles",
            f"offset     : {self.offset}",
            f"fpp        : {self.fpp}",
            f"high       : {self.high}",
            f"candle_high: {self.candles.high}",
            f"candle_low : {self.candles.low}",
            f"low        : {self.low}",
            f"width      : {self.width}",
            f"height     : {self.height}",
        ]
        return "\n".join(lines)

    def config(
        self,
        candles: Optional[List[Candle]] = None,
        offset: Optional[int] = None,
        fpp: Optional[int] = None,
    ):
        changed = False
        if candles is not None:
            self.candles = candles
            changed = True
        if offset is not None:
            self.offset = CandleOffset(offset)
            changed = True
        if fpp is not None:
            self.fpp = fpp
            changed = True
        if changed:
            self._update()

    def clear(self):
        self.candles = []
        self.height = self.DEFAULT_HEIGHT
        self.width = self.DEFAULT_WIDTH
        self.high = None
        self.low = None

    def ndx_x(self, x: int) -> int:
        """Get candle ndx based on x pixel.

        Note there need not be any candles the calculation is
        based on the candle offset. Also the value might be off
        the actual canvas scroll region.
        """
        return math.floor((x - self.LEFT_PAD) / self.offset)

    def y_fp(self, fp: FracPips) -> int:
        """Get y pixel coord for given FracPips."""
        return round((self.high - fp) / self.fpp)

    def y_price(self, price: Price) -> int:
        """Get y pixel coord for given price."""
        fp = FracPips.from_price(price)
        return self.y_fp(fp)

    def x_ndx(self, ndx: int) -> int:
        """Get x pixel coord for given candle index."""
        return (ndx * self.offset) + self.LEFT_PAD

    def moveto_x(self, x: int) -> float:
        """Get x position in fraction appropriate to Canvas xview_moveto method."""
        return x / self.width

    def moveto_y(self, y: int) -> float:
        """Get x position in fraction appropriate to Canvas xview_moveto method."""
        return y / self.height

    def candle_region(self, ndx_1: int, ndx_2: int) -> Tuple[int, int, int, int]:
        """Find bbox region around candles from one ndx to another."""
        ndx_1 = ndx_1 if ndx_1 > 0 else 0
        candles = self.candles.candles[ndx_1:ndx_2]
        x1 = (ndx_1 * self.offset) + self.LEFT_PAD
        x2 = (ndx_2 * self.offset) + self.LEFT_PAD
        if candles:
            low, high = get_candle_range(candles)
            y1 = self.y_price(high)
            y2 = self.y_price(low)
        else:
            half_height = round(self.height / 2)
            y1 = half_height - 10
            y2 = half_height + 10
        return x1, y1, x2, y2

    # ---------------------------------------------------------------------------
    #  Helper Methods
    # ---------------------------------------------------------------------------

    def _update(self):
        if self.candles:
            self._update_height()
            self._update_width()
        else:
            self.clear()

    def _update_height(self):
        """Updates height, low, and high"""
        fp_delta = self.candles.high - self.candles.low
        pixel_delta = math.ceil(fp_delta / self.fpp)
        if pixel_delta < 1000:
            pixel_pad = math.ceil((3000 - pixel_delta) / 2)
            fp_pad = pixel_pad * self.fpp
            self.height = pixel_delta + (2 * pixel_pad)
            self.high = self.candles.high + fp_pad
            self.low = self.candles.low - fp_pad
        else:
            fp_pad = pixel_delta * self.fpp
            self.height = 3 * pixel_delta
            self.high = self.candles.high + fp_pad
            self.low = self.candles.low - fp_pad

    def _update_width(self):
        """Updates self.width"""
        candle_pixels = len(self.candles) * self.offset
        self.width = candle_pixels + self.RIGHT_PAD + self.LEFT_PAD
