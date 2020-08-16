from typing import List

from forex_types import FracPips


class PriceScale:
    """For finding where to put price grid lines on scale."""

    NUM_GRID = 6

    MIN_PIXEL = 100

    # Different numbers of pips we might have between each grid line.
    INTERVALS = (
        FracPips(10),
        FracPips(25),
        FracPips(50),
        FracPips(100),
        FracPips(250),
        FracPips(500),
        FracPips(1000),
        FracPips(2500),
        FracPips(5000),
        FracPips(10_000),
        FracPips(25_000),
        FracPips(50_000),
        FracPips(100_000),
        FracPips(250_000),
        FracPips(500_000),
        FracPips(1_000_000),
        FracPips(2_500_000),
        FracPips(5_000_000),
        FracPips(10_000_000),
        FracPips(25_000_000),
        FracPips(50_000_000),
        FracPips(100_000_000),
        FracPips(250_000_000),
        FracPips(500_000_000),
    )

    def __init__(self, fpp: float):
        """Set up PriceScale based on fractional pips per pixel.

        The self.interval attribute is loaded with the smallest fractional
        pip value from self.INTERVALS which will result in the grid lines
        being at least self.MIN_PIXEL pixels away from each other. If there
        is no such interval we just pick the biggest.

        Args:
            fpp: fractional pips per pixel.
        """
        self.interval: FracPips = self.INTERVALS[-1]
        for interval in self.INTERVALS:
            pixels: float = float(interval) / fpp
            if pixels >= self.MIN_PIXEL:
                self.interval = interval
                break

    def get_grid_list(self, fp_low: FracPips, fp_high: FracPips) -> List[FracPips]:
        """Return list of fractional pips to put grid lines at.

        Args:
            fp_low: lowest price to place grid lines at or above
            fp_high: highest price to place grid lines at or below
        """
        grid_list: List[FracPips] = []
        remainder = fp_low % self.interval
        grid_fp = fp_low - remainder
        while grid_fp <= fp_high:
            grid_list.append(grid_fp)
            grid_fp = FracPips(grid_fp + self.interval)
        return grid_list
