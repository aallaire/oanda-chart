from typing import Iterable, Tuple, Dict, Type, List, Union

from oanda_candles import Candle
from time_int import TimeInt, TimeTruncUnit
from datetime import datetime

from oanda_chart.geo.candle_offset import CandleOffset


class _ApproxTimes:
    MIN = 60
    HOUR = 60 * MIN
    DAY = 24 * HOUR
    WEEK = 7 * DAY
    FAT_MONTH = 31 * DAY
    THIN_MONTH = 28 * DAY
    FAT_YEAR = 370 * DAY
    THIN_YEAR = 360 * DAY


class ScaleTime:
    """This is a parent class of subclasses which represent time intervals.

    The subclasses themselves vary from Minute to TenYear intervals. While
    instances of these subclasses represent specific points along the interval.
    For example the QuarterHour class represents having intervals of 15 minutes,
    while a QuarterHour object represents a specific time that is either on
    an hour or 15, 30, or 45 minutes past the hour.

    To construct an object one supplies a time int value which is rounded down
    to the most recent point that falls on the interval evenly.

    Note the subclasses should just overload unit and num values and overload
    the get_labels method. The rest of the functionality should default to
    this parent class.
    """

    unit: str = TimeTruncUnit.YEAR
    num: int = 1
    name: str = "Unknown"

    @classmethod
    def get_run_size(cls, candles: Iterable[Candle]) -> int:
        """Get the largest number of candles in same interval.

        Args:
            candles: iterable of Candle objects (method makes one pass)
        Returns:
            0 if there are no candles. Otherwise the most in same interval
        """
        counts: Dict[TimeInt, int] = {}
        for candle in candles:
            time = candle.time.trunc(cls.unit, num=cls.num)
            if time in counts:
                counts[time] += 1
            else:
                counts[time] = 1
        longest = 0
        for count in counts.values():
            if count > longest:
                longest = count
        return longest

    def __init__(self, time: TimeInt):
        """Round down time to most recent time that fell evenly on scale."""
        self.time = time.trunc(self.unit, num=self.num)

    def __eq__(self, other: "ScaleTime") -> bool:
        if not isinstance(other, ScaleTime):
            return NotImplemented
        return self.time == other.time

    def __str__(self) -> str:
        return self.time.get_pretty()

    def __hash__(self) -> int:
        return hash(self.time)

    def get_labels(self) -> Tuple[str, str]:
        """Return what to put on the upper and lower label for this time.
        
        The idea is to have an upper line and lower line describing the
        time period to put on time scale part of chart. This returns what
        should go in these labels for a give scale time.
        
        Returns:
            upper label string, lower label string.
        """
        return NotImplemented

    def get_day_string(self):
        """Get string representing the day of self.time.
        
        Returns:
            date string like "May 20" if dt in current year,
            otherwise one formatted like "2018-05-20".
        """
        dt = self.time.get_datetime()
        current = datetime.utcnow()
        if dt.year == current.year:
            month = dt.strftime("%b")
            return f"{month} {dt.day}"
        else:
            return dt.strftime("%Y-%m-%d")

    def get_weekday(self):
        """Get abbreviated weekday name like Sun, Mon etc."""
        dt = self.time.get_datetime()
        return dt.strftime("%a")


class TenYear(ScaleTime):
    unit: str = TimeTruncUnit.YEAR
    num: int = 10
    name: str = "10 Year"

    def get_labels(self):
        tenth_year = TimeInt(self.time + 9 * _ApproxTimes.FAT_YEAR).trunc_year()
        return f"{self.time.get_pretty()}-", tenth_year.get_pretty()


class FiveYear(ScaleTime):
    unit: str = TimeTruncUnit.YEAR
    num: int = 5
    name: str = "5 Year"

    def get_labels(self):
        fifth_year = TimeInt(self.time + 4 * _ApproxTimes.FAT_YEAR).trunc_year()
        return f"{self.time.get_pretty()}-", fifth_year.get_pretty()


class ThreeYear(ScaleTime):
    unit: str = TimeTruncUnit.YEAR
    num: int = 3
    name: str = "3 Year"

    def get_labels(self):
        third_year = TimeInt(self.time + 2 * _ApproxTimes.FAT_YEAR).trunc_year()
        return f"{self.time.get_pretty()}-", third_year.get_pretty()


class TwoYear(ScaleTime):
    unit: str = TimeTruncUnit.YEAR
    num: int = 2
    name: str = "2 Year"

    def get_labels(self):
        second_year = TimeInt(self.time + _ApproxTimes.FAT_YEAR).trunc_year()
        return f"{self.time.get_pretty()}-", second_year.get_pretty()


class Year(ScaleTime):
    unit: str = TimeTruncUnit.YEAR
    num: int = 1
    name: str = "Year"

    def get_labels(self):
        return self.time.get_pretty(), ""


class Quarter(ScaleTime):
    unit: str = TimeTruncUnit.MONTH
    num: int = 3
    name: str = "Quarter"

    def get_labels(self):
        dt = self.time.get_datetime()
        quarter_num = ((dt.month - 1) // 3) + 1
        return f"Q{quarter_num}", f"{dt.year}"


class Month(ScaleTime):
    unit: str = TimeTruncUnit.MONTH
    num: int = 1
    name: str = "Month"

    def get_labels(self):
        dt = self.time.get_datetime()
        return dt.strftime("%B"), dt.strftime("%Y")


class Week(ScaleTime):
    unit: str = TimeTruncUnit.WEEK
    num: int = 1
    name: str = "Week"

    def get_labels(self):
        return "Week of", self.get_day_string()


class Day(ScaleTime):
    unit: str = TimeTruncUnit.DAY
    num: int = 1
    name: str = "Day"

    def get_labels(self):
        return self.get_weekday(), self.get_day_string()


class HalfDay(ScaleTime):
    unit: str = TimeTruncUnit.HOUR
    num: int = 12
    name: str = "12 Hour"

    def get_labels(self):
        dt = self.time.get_datetime()
        top = dt.strftime("%a %p")
        return top, self.get_day_string()


class QuarterDay(ScaleTime):
    unit: str = TimeTruncUnit.HOUR
    num: int = 6
    name: str = "6 Hour"

    def get_labels(self):
        dt = self.time.get_datetime()
        weekday = self.get_weekday()
        if dt.hour < 6:
            top = f"{weekday} Night"
        elif dt.hour < 12:
            top = f"{weekday} Morn"
        elif dt.hour < 18:
            top = f"{weekday} After"
        else:
            top = f"{weekday} Eve"
        return top, self.get_day_string()


class Hour(ScaleTime):
    unit: str = TimeTruncUnit.HOUR
    num: int = 1
    name: str = "Hour"

    def get_labels(self):
        dt = self.time.get_datetime()
        if dt.hour == 0:
            top = "12 Midnight"
        elif dt.hour == 12:
            top = "12 Noon"
        else:
            top = dt.strftime("%I%p").lower()
            top = top[1:] if top.startswith("0") else top
        return top, self.get_day_string()


class HalfHour(ScaleTime):
    unit: str = TimeTruncUnit.MINUTE
    num: int = 30
    name: str = "30 Min"

    def get_labels(self):
        dt = self.time.get_datetime()
        top = dt.strftime("%I:%M%p").lower()
        top = top[1:] if top.startswith("0") else top
        return top, self.get_day_string()


class QuarterHour(HalfHour):
    num: int = 15
    name: str = "15 Min"


class TenMinute(HalfHour):
    num: int = 10
    name: str = "10 Min"


class FiveMinute(HalfHour):
    num: int = 5
    name: str = "5 Min"


class Minute(HalfHour):
    num: int = 1
    name: str = "Minute"


class ScaleTimeManager:

    SCALES = (
        Minute,
        FiveMinute,
        TenMinute,
        QuarterHour,
        HalfHour,
        Hour,
        QuarterDay,
        HalfDay,
        Day,
        Week,
        Month,
        Quarter,
        Year,
        ThreeYear,
        FiveYear,
        TenYear,
    )

    def __init__(self, candles: Iterable[Candle]):
        self.offset_to_scale: Dict[CandleOffset, Type[ScaleTime]] = {}
        run_sizes: List[Tuple[int, Type[ScaleTime]]] = []
        for scale in self.SCALES:
            run_size = scale.get_run_size(candles)
            run_sizes.append((run_size, scale))
        for width in range(CandleOffset.MIN, CandleOffset.MAX + 1):
            offset = CandleOffset(width)
            min_run = offset.min_run()
            for run_size, scale in run_sizes:
                if run_size >= min_run:
                    self.offset_to_scale[offset] = scale
                    break

    def get_grid(
        self, candles: Iterable[Candle], offset: CandleOffset
    ) -> List[Tuple[int, ScaleTime]]:
        """Get list of pixel offset and Scale times for time grid."""
        grid_list = []
        if candles:
            grid_adjust = offset.grid_adjust()
            scale_time_cls: Type[ScaleTime] = self.offset_to_scale[offset]
            prev_scale_time: ScaleTime = scale_time_cls(candles[0].time)
            grid_list.append((-grid_adjust, prev_scale_time))
            gap_left = False
            for ndx, candle in enumerate(candles[1:]):
                scale_time = scale_time_cls(candle.time)
                if scale_time != prev_scale_time:
                    pixels = ((ndx + 1) * offset) - grid_adjust
                    grid_list.append((pixels, scale_time))
                    prev_scale_time = scale_time
                    gap_left = False
                else:
                    gap_left = True
            if gap_left:
                pixels = ((ndx + 1) * offset) - grid_adjust
                grid_list.append((pixels, scale_time))
        return grid_list
