from tkinter import ALL
from typing import Tuple, List
from tkinter import Canvas

from forex_types import Price
from magic_kind import MagicKind
from time_int import TimeInt
from typing import Optional

from oanda_chart.env.colors import CommonColors, DarkColors

from oanda_chart.util.price_coords import PriceCoords


class Tags(MagicKind):
    ALL = ALL
    BADGE = "badge"
    CANDLE = "candle"
    PRICE_LINE = "price_line"
    PRICE_RAY = "price_ray"
    ENTRY_LINE = "entry_line"
    GRID_LINE = "grid_line"
    RECTANGLE = "rectangle"
    REGION = "region"


class GeoMiester:
    """Managers GeoItems in a canvas."""

    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.candles: List["GeoCandle"] = []
        self.price_lines: List["PriceLine"] = []
        self.price_rays: List["PriceRay"] = []
        self.grid_lines: List["GridLine"] = []
        self.entry_lines: List["EntryLine"] = []
        self.coords: Optional[PriceCoords] = None

    def add_price_line(
        self, price: Price, color: str = CommonColors.WHITE, width: int = 1
    ):
        self.price_lines.append(PriceLine(self, price, color, width))

    def add_grid_line(self, price: Price):
        self.grid_lines.append(GridLine(self, price))


class GeoItem:

    TAGS: Tuple[str] = tuple()

    def __init__(self, miester: GeoMiester):
        self._miester = miester
        self._num: Optional[int] = None

    def draw(self):
        if self._num is None:
            self._num = self._draw()
        else:
            self._miester.canvas.delete(self._num)
            self._num = self._draw()

    def _draw(self) -> int:
        raise NotImplemented("_draw not implemented for base class GeoItem.")

    def delete(self) -> bool:
        """Delete if it exists, otherwise ignore.

        Returns:
            True iff it had been there to delete, False if already gone.
        """
        if self._num is not None:
            self._miester.canvas.delete(self._num)
            self._num = None
            return True
        return False


class PriceLine(GeoItem):
    """Horizontal line that stretches across entire region at given price."""

    TAGS = (Tags.PRICE_LINE,)

    # Rather than figure out how wide we need to make lines
    # to make them appear infinite, we just use a big
    # number of pixels in both directions.
    X_LEFT = -100_000_000  # how far to left lines go
    X_RIGHT = 100_000_000  # how far to right lines go

    def __init__(self, miester: GeoMiester, price: Price, color: str, width: int):
        super().__init__(miester)
        self.price: Price = price
        self.color: str = color
        self.width: int = width

    def _draw(self) -> int:
        y_price = 21
        return self.canvas.create_line(
            self.X_LEFT,
            y_price,
            self.X_RIGHT,
            y_price,
            tags=self.TAGS,
            fill=self.color,
            width=self.width,
        )


class GridLine(PriceLine):
    def __init__(self, miester: GeoMiester, price: Price):
        super().__init__(miester, price, DarkColors.GRID, 3)


class PriceRay(GeoItem):
    """Horizontal Ray from candle position and continuing right."""

    TAGS = (Tags.PRICE_LINE,)
    KEYS = {"price", "width", "color"}

    TAGS = (Tags.PRICE_RAY,)
    KEYS = {"price", "width", "color"}


class EntryLine(PriceLine):
    def __init__(self, start: TimeInt, price: Price):
        super().__init__(Order.FRONT_MOST, Tags.ENTRY_LINE, Tags.PRICE_LINE)
