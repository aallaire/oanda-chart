"""Coordinate system based on candles position and prices.

Our data comes to us as candle position and price, and we need
to graph it on a canvas in terms of pixels from the upper left.
The PriceCoords class is all about making those conversions.
"""
from typing import Tuple
from forex_types import Price, FracPips
from oanda_candles import CandleSequence
from decimal import Decimal


class PriceCoords:
    def __init__(
        self, height: int, offset: int, num: int, low: FracPips, high: FracPips
    ):
        """initialize price coordinates.

        Args:
            height: height of chart in pixels.
            offset: number of pixels from start of one candle to next.
            num: number of candles in chart
            low: price that bottom of chart represents in fractional pips
            high: price that top of chart represents in fractional pips
        """
        self.height: int = int(height)
        self.num: int = int(num)
        self.offset: int = int(offset)
        self.low: FracPips = FracPips(low)
        self.high: FracPips = FracPips(high)
        self.delta: FracPips = FracPips(high - low)
        self.width: int = self.num * self.offset
        if self.num <= 0:
            raise ValueError("There must be at least one candle")
        elif self.offset <= 0:
            raise ValueError("Candle pixel offset must be at least 1")
        elif self.delta <= 0:
            raise ValueError("high price must be higher than low price")
        elif self.height < 10:
            raise ValueError("chart must be at least 10 pixels high")

    @classmethod
    def from_candle_sequence(
        cls, height: int, offset: int, candles: CandleSequence
    ) -> "PriceCoords":
        if not candles:
            raise ValueError("No candles to find price range of")
        low_price = candles[0].bid.l
        high_price = candles[0].ask.h
        for candle in candles:
            if candle.bid.l < low_price:
                low_price = candle.bid.l
            if candle.ask.h > high_price:
                high_price = candle.ask.h
        delta_pips = high_price.pips - low_price.pips
        pip_pad = max(Decimal("1"), delta_pips / 20)
        low_price = low_price.add_pips(-pip_pad)
        high_price = high_price.add_pips(pip_pad)
        low = FracPips.from_price(low_price)
        high = FracPips.from_price(high_price)
        return cls(height, offset, len(candles), low, high)

    def x(self, num: int) -> int:
        """Get the number of pixels from left to start of specified candle."""
        return num * self.offset

    def y(self, price: Price) -> int:
        """Get the number of pixels from top that best reflects price."""
        fpip = FracPips.from_price(price)
        fpip_from_top = self.high - fpip
        ratio_from_top = fpip_from_top / self.delta
        return round(ratio_from_top * self.height)

    def xy(self, num: int, price: Price) -> Tuple[int, int]:
        """Get xy coords from candle number and price."""
        x = num * self.offset
        y = self.y(price)
        return x, y

    def bbox(
        self, num1: int, price1: Price, num2: int, price2: Price
    ) -> Tuple[int, int, int, int]:
        """Get bounding box coords from candle numbers and prices."""
        x1 = num1 * self.offset
        y1 = self.y(price1)
        x2 = num2 * self.offset
        y2 = self.y(price2)
        return x1, y1, x2, y2
