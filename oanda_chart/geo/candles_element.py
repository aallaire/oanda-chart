from typing import List, Optional

from forex_types import FracPips, Pair
from oanda_candles import CandleMeister, Candle, Gran
from oanda_chart.util.candle_range import get_candle_range


class CandlesElement:

    Tag = "CandlesElement"

    def __init__(self, pair: Pair, gran: Gran, count: int = 500):
        self.pair: Pair = pair
        self.gran: Gran = gran
        self.count: int = count
        self.candles: Optional[List[Candle]] = None
        self.high: FracPips = FracPips(0)
        self.low: FracPips = FracPips(1_000_000)
        self.update()

    def config(
        self,
        pair: Optional[Pair] = None,
        gran: Optional[Gran] = None,
        count: Optional[int] = None,
    ) -> bool:
        """Configure with new values and update candle data.

        Returns:
            True if anything changed.
            False if values were same as you had before and there
                  is no fresh candle data for those values yet.
        """
        attr_change = False
        if pair != self.pair:
            self.pair = pair
            attr_change = True
        if gran != self.gran:
            self.gran = gran
            attr_change = True
        if count != self.count:
            self.count = count
            attr_change = True
        candle_change = self.update()
        return attr_change or candle_change

    def __len__(self):
        return len(self.candles)

    def __iter__(self):
        return self.candles.__iter__()

    def update(self) -> bool:
        """See that candles are up to date.

        Returns:
            True if candle data was updated, False if it remained same.
        """
        candles = CandleMeister.grab(self.pair, self.gran, self.count)
        if (
            candles
            and self.candles
            and len(candles) == len(self.candles)
            and candles[-1] == self.candles[-1]
        ):
            return False
        low, high = get_candle_range(candles)
        self.low = FracPips.from_price(low)
        self.high = FracPips.from_price(high)
        self.candles = candles
