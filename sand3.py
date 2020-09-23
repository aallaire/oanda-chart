import os

from oanda_candles import CandleMeister, Pair, Gran, QuoteKind
from oanda_chart.geo.candle_offset import CandleOffset
from oanda_chart.geo.scale_time import (
    Year,
    TwoYear,
    ThreeYear,
    FiveYear,
    TenYear,
    Quarter,
    Month,
    Week,
    Day,
    HalfDay,
    QuarterDay,
    Hour,
    HalfHour,
    TenMinute,
    FiveMinute,
    Minute,
    ScaleTimeManager,
)

CandleMeister.init_meister(os.getenv("OANDA_TOKEN"))

candles = CandleMeister.grab(Pair.EUR_USD, Gran.H1, 200)

scale_manager = ScaleTimeManager(candles)
offset = CandleOffset(12)

grid_list = scale_manager.get_grid(candles, offset)

for grid in grid_list:
    print(grid)

print(len(grid_list))
