from forex_types import Price, FracPips, Pair
from oanda_chart.price_coords import PriceCoords
import math


class PriceScale:
    """For finding where to put price grid lines on scale."""

    NUM_GRID = 6

    # Different numbers of pips we might have between each grid line.
    INTERVALS = (
        FracPips(100_000_000),
        FracPips(50_000_000),
        FracPips(25_000_000),
        FracPips(10_000_000),
        FracPips(5_000_000),
        FracPips(2_500_000),
        FracPips(1_000_000),
        FracPips(500_000),
        FracPips(250_000),
        FracPips(100_000),
        FracPips(50_000),
        FracPips(25_000),
        FracPips(10_000),
        FracPips(5000),
        FracPips(2500),
        FracPips(1000),
        FracPips(500),
        FracPips(250),
        FracPips(100),
        FracPips(50),
        FracPips(25),
        FracPips(10),
    )

    def __init__(self, pair: Pair, coords: PriceCoords):
        self.coords = coords
        self.prices = []
        frac_interval: FracPips = self.INTERVALS[-1]
        interval_limit = coords.delta / self.NUM_GRID
        for interval in self.INTERVALS:
            if interval <= interval_limit:
                frac_interval: FracPips = interval
                break
        self.interval: int = round(frac_interval / 10)
        num_intervals = math.ceil(coords.low / frac_interval)
        price = FracPips(num_intervals * frac_interval).to_pair_price(pair)
        price_cap = self.coords.high.to_pair_price(pair)
        while price < price_cap:
            self.prices.append(price)
            price = price.add_pips(self.interval)

    def __len__(self):
        return len(self.prices)

    def __iter__(self):
        for price in self.prices:
            yield price

    def __getitem__(self, index: int) -> Price:
        return self.prices[index]
