from typing import Optional, List, Tuple
from math import ceil, floor

from forex_types import FracPips, Price

from oanda_chart.geo.price_scale import PriceScale
from oanda_chart.geo.xandles import Xandles


class Yrids:
    def __init__(
        self,
        height: Optional[int] = None,
        mid: Optional[FracPips] = None,
        fpp: float = PriceScale.DEFAULT_FPP,
        scale: PriceScale = PriceScale.DEFAULT,
    ):
        # ----------------------------------------------------------------------
        # User set attributes
        # ----------------------------------------------------------------------
        # the height of the view in pixels
        self.height: Optional[int] = height
        # the middle price in fractional pips
        self.mid: FracPips = None if mid is None else FracPips(mid)
        # fpp is the ratio of fractional pips to vertical pixel.
        self.fpp: float = fpp
        # the grid scale for price (how many fpp between grid lines)
        self.scale: PriceScale = scale
        # ----------------------------------------------------------------------
        # Attributes derived from update when user attributes are all set
        # ----------------------------------------------------------------------
        # The height if the scrollable area of canvas.
        self.scroll_height: Optional[int] = None
        # list of frac pips and pixel locations for grid lines.
        self.grid_list: Optional[List[Tuple[FracPips, int]]] = None
        # the price in fractional pips at top and bottom of viewable area.
        self.top: Optional[FracPips] = None
        self.bot: Optional[FracPips] = None
        # the price in fractional pips at top and bottom of scrollable area.
        self.scroll_top: Optional[FracPips] = None
        self.scroll_bot: Optional[FracPips] = None
        # ----------------------------------------------------------------------
        # Update provided we have enough info to.
        # ----------------------------------------------------------------------
        self.update()

    def clear(self):
        self.height = None
        self.mid = None
        self.fpp = PriceScale.DEFAULT_FPP
        self.scale = PriceScale.DEFAULT
        self.scroll_height = None
        self.grid_list = None
        self.top = None
        self.bot = None
        self.scroll_top = None
        self.scroll_bot = None

    def price_to_y(self, price: Price) -> int:
        """Convert Price to y pixel coordinate."""
        return self.fp_to_y(FracPips.from_price(price))

    def fp_to_y(self, fp: FracPips) -> int:
        """Convert frac pips to y pixel coordinate."""
        return round((self.scroll_top - fp) / self.fpp)

    def y_to_fp(self, y: int) -> FracPips:
        """Convert y pixel coordinate to price in frac pips."""
        return FracPips(self.scroll_top - round(y * self.fpp))

    @classmethod
    def calculate_price_view(
        cls, xandles: Xandles, height: int
    ) -> Tuple[FracPips, float]:
        """Calculate the price_view fp_mid and fpp from Xandles and pixel height.
        
        Args:
            xandles: must be loaded with candles we can get prices from.
            height: height of view area price view will cover.
        Returns:
            frac pip price of mid point of view, Frac pips per pixel ratio
        """
        low, high = xandles.find_view_low_high()
        fp_mid = FracPips(round((high + low) / 2))
        fp_delta = high - low
        fp_pad = ceil(fp_delta / 10)
        fp_height = fp_delta + (2 * fp_pad)
        fpp = fp_height / height
        return fp_mid, fpp

    def can_resolve(self) -> bool:
        return (
            self.height is not None
            and self.height > 0
            and self.mid is not None
            and self.fpp is not None
            and self.fpp > 0.0
        )

    def view_set(self, xandles: Xandles):
        """Set ourselves around the candles in xandles view."""
        # DEPRECATING?....yrids should not need to know about price view.
        if self.height is None or self.scale is None:
            return
        low, high = xandles.find_view_low_high()
        if low is None or high is None:
            return
        fp_delta = high - low
        fp_pad = ceil(fp_delta / 10)
        self.top = FracPips(high + fp_pad)
        self.bot = FracPips(high - fp_pad)
        fp_height = fp_delta + (2 * fp_pad)
        self.fpp = fp_height / self.height
        self.update()

    def update(
        self,
        height: Optional[int] = None,
        mid: Optional[FracPips] = None,
        fpp: Optional[float] = None,
        scale: Optional[PriceScale] = None,
    ) -> bool:
        """Update Yrids with specified values, resolve if possible.

        All the args are optional, and if left as None they will stay the
        same as they already were.

        Args:
            height: height of view in in pixels.
            mid: frac pips price of mid point of view.
            fpp: ratio of frac pips per pixel
            scale: price scale object indicating frac pips between price grid lines.
        """
        if height is not None:
            self.height = height
        if mid is not None:
            self.mid = mid
        if fpp is not None:
            self.fpp = fpp
        if scale is not None:
            self.scale = scale
        if not self.can_resolve():
            return False
        self.scroll_height = self.height * 3
        fp_view_delta = round((self.height / 2) * self.fpp)
        fp_scroll_delta = round((self.height / 2) * self.fpp * 3)
        self.top = FracPips(self.mid + fp_view_delta)
        self.bot = FracPips(self.mid - fp_view_delta)
        self.scroll_top = FracPips(self.mid + fp_scroll_delta)
        self.scroll_bot = FracPips(self.mid - fp_scroll_delta)
        self.grid_list = []
        for fp in self.scale.get_grid_list(self.scroll_bot, self.scroll_top):
            y = self.fp_to_y(fp)
            self.grid_list.append((fp, y))
        return True
