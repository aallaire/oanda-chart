"""xandles stands for x-coordinates and candles.


We need our x-coordinates informed by actual candles, and we need
a way to know where along x coordinate to draw the candles. This
module supplies the Xandles class which combines candles with
the width of the view, the offset width of individual candles,
and the current number of candles the user has panned back in
time, to determine where each candle goes and how many pixels
are to be left blank of candles to the left and right.


Q: But why are specific candles needed for the x-coordinates of
the canvas?

A: Because they are not at regular intervals of time. The forex
market is sometimes closed. Usually only between Friday 5pm
in New York in US and Monday 9am in Sydney Australia. But it
could have been closed other times for other reasons. Or we
could just be missing some candles. Who knows? But we can't
predict mere candle position to time given a granularity given
this uncertainty. We have to have the actual candle's starting
times in order to map x coordinate to time and time to x coordinate.
"""

from math import ceil, floor
from typing import List, Tuple, Optional, Iterable

from forex_types import FracPips
from oanda_candles import Candle

from oanda_chart.geo.candle_offset import CandleOffset
from oanda_chart.geo.scale_time import ScaleTimeManager, ScaleTime


class Xandles:
    """Xandles stands for X coordinate and candles.

    Given a list of candles and some information about the state of the
    chart, determines which candles should be drawn in scrollable area,
    how big the scrollable area is, how many pixels are to left and
    right of the candles to draw in scrollable area, and what x number
    of pixels from left of scrollable area to draw each candle.
    """

    PAD = 50

    def __init__(
        self,
        offset: CandleOffset = CandleOffset.DEFAULT,
        width: Optional[int] = None,
        candles: Optional[List[Candle]] = None,
        ndx: int = 0,
    ):
        # ----------------------------------------------------------------------
        # User set attributes
        # ----------------------------------------------------------------------
        # offset is the width a candle takes in pixels, including gap between.
        self.offset: CandleOffset = offset
        # width is the pixel width of the view (viewing window user sees).
        self.width: Optional[int] = width
        # candles is a list of Candle objects from old ones to latest.
        self.candles: Optional[List[Candle]] = candles
        # ndx is how many candles back from latest candle user has panned.
        self.ndx: int = ndx
        # ----------------------------------------------------------------------
        # Attributes derived from update when user attributes are all set
        # ----------------------------------------------------------------------
        # The width of the scrollable area of canvas.
        self.scroll_width: Optional[int] = None
        # The display_list has both candles plus their pixel offset from left
        # of canvas.
        self.display_list: Optional[List[Tuple[int, Candle]]] = None
        # pixels_left is how many pixels before first candle on left (which
        # happens when candle data does not go back as far as canvas).
        self.pixels_left: Optional[int] = None
        # pixels_right is how many pixels from left of canvas it is to where
        # there are no more candles on the right of canvas. When the user has
        # panned far enough into past, this will be the same as width of canvas.
        self.pixels_right: Optional[int] = None
        # scale_manager figures out where to put time grids.
        self.scale_manager = ScaleTimeManager(candles)
        # grid_list is a list of pixels from start of candle with corresponding
        # ScaleTime for start of candles next to the pixel location.
        self.grid_list: Optional[List[Tuple[int, ScaleTime]]] = None
        # showing_recent should be true when most recent candle is in view
        self.showing_recent: Optional[bool] = None
        # ---------------------------------------------------------------------
        # Update provided we have enough info to.
        # ---------------------------------------------------------------------
        self.update()

    def clear(self):
        self.offset = CandleOffset.DEFAULT
        self.width = None
        self.candles = None
        self.ndx = 0
        self.scroll_width = None
        self.display_list = None
        self.pixels_left = None
        self.pixels_right = None

    def go_home(self):
        self.offset = CandleOffset.DEFAULT
        self.ndx = 0
        self.update()

    def can_resolve(self) -> bool:
        return self.width is not None and self.candles

    def get_candle(self, ndx) -> Optional[Candle]:
        """Get candle by index (where 0 is most recent candle)."""
        num_candle = len(self.display_list)
        if ndx >= num_candle:
            return None
        return self.display_list[num_candle - ndx - 1][1]

    def candle_at_x(self, x: int) -> Optional[Candle]:
        """Get candle that x coordinate falls on, None if not on candle."""
        if x < self.pixels_left or x > self.pixels_right:
            return None
        delta = x - self.pixels_left
        ndx = floor(delta / self.offset)
        return self.display_list[ndx][1]

    def iter_view_candles(self) -> Iterable[Candle]:
        """Iterate through Candle objects in view area"""
        x_start = max(self.width, self.pixels_left)
        x_end = min(self.width * 2, self.pixels_right)
        start_delta = x_start - self.pixels_left
        end_delta = x_end - self.pixels_left
        start_ndx = floor(start_delta / self.offset)
        end_ndx = floor(end_delta / self.offset)
        for _, candle in self.display_list[start_ndx:end_ndx]:
            yield candle

    def find_view_low_high(self) -> Tuple[Optional[FracPips], Optional[FracPips]]:
        """Return the lowest and highest price in view as frac pips.

        If there are no prices in the view, then return None, None instead.
        """
        if not self.candles:
            return None, None
        high = FracPips(0)
        low = FracPips(1_000_000)
        for candle in self.iter_view_candles():
            candle_high = candle.high_fp
            candle_low = candle.low_fp
            if candle_high > high:
                high = candle_high
            if candle_low < low:
                low = candle_low
        if low > high:
            return None, None
        return low, high

    @classmethod
    def calculate_pull_size(cls, width: int, offset: CandleOffset, ndx: int):
        """Determine how many candles to pull given width, offset, and ndx number.

        If this is less than 100, return 100 instead.
        """
        pixels_left = (2 * width) - cls.PAD
        slots_left = ceil(pixels_left / offset)
        needed = ndx + slots_left
        return max(needed, 500)

    def update(
        self,
        offset: Optional[CandleOffset] = None,
        width: Optional[int] = None,
        candles: Optional[List[Candle]] = None,
        ndx: Optional[int] = None,
    ) -> bool:
        """Resolves settings to new attributes (or existing ones).

        Keyword attributes left as None are left as they were. Provided
        after making the requested changes we have enough attributes
        defined to define the Xandles, the remaining attributes are resolved.

        Args:
            offset: candle offset, width of one candle to the next.
            width: width of viewing area in pixels
            candles: list of Candle objects from which we pull the ones we need.
            ndx: how many candles to the past we have panned.
        Returns:
            True iff we had enough attributes to resolve Xandles.
        """
        if offset is not None:
            self.offset = offset
        if width is not None:
            self.width = width
        if candles is not None:
            self.candles = candles
        if ndx is not None:
            self.ndx = ndx
        if not self.can_resolve():
            return False
        self.scroll_width = 3 * self.width
        slots = ceil(self.scroll_width / self.offset)
        right_pixels = self.width + self.PAD
        right_slots = ceil(right_pixels / self.offset)
        left_slots = slots - right_slots
        if right_slots > self.ndx:
            candles_to_right = self.ndx
            empty_slots_to_right = right_slots - self.ndx
            self.pixels_right = self.scroll_width - (empty_slots_to_right * self.offset)
        else:
            candles_to_right = right_slots
            self.pixels_right = self.scroll_width
        total_num = len(self.candles)
        # Find number of candles to go to left of current candle position.
        num_left = min(total_num - self.ndx, left_slots)
        # Find number of candles to go to right of current candle position.
        num_right = min(candles_to_right, total_num)
        # Find starting candle index.
        start_ndx = total_num - num_left - self.ndx
        # Find starting pixel position of first candle
        empty_slots_to_left = left_slots - num_left
        self.pixels_left = empty_slots_to_left * self.offset
        # Find last candle index.
        slots_open = slots - empty_slots_to_left
        tail_length = total_num - start_ndx
        x = self.pixels_left
        self.display_list = []
        if slots_open > tail_length:
            self.showing_recent = True
            for candle in self.candles[start_ndx:]:
                self.display_list.append((x, candle))
                x += self.offset
            self.grid_list = self.scale_manager.get_grid(
                self.candles[start_ndx:], self.offset
            )
        else:
            self.showing_recent = False
            end_ndx = start_ndx + slots_open
            for candle in self.candles[start_ndx:end_ndx]:
                self.display_list.append((x, candle))
                x += self.offset
            self.grid_list = self.scale_manager.get_grid(
                self.candles[start_ndx:end_ndx], self.offset
            )
        return True
