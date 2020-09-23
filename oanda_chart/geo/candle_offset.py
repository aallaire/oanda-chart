from math import ceil

from oanda_chart.env.const import Const

# Map of total candle offset to tuples of:
#   * offset to the wick
#   * offset to far end of candle body
#   * gap between candle bodies
OffsetMap = {
    1: (0, 1, 0),
    2: (0, 2, 0),
    3: (1, 3, 0),
    4: (1, 3, 1),
    5: (2, 5, 0),
    6: (2, 5, 1),
    7: (2, 5, 2),
    8: (3, 7, 1),
    9: (3, 7, 2),
    10: (3, 7, 3),
    11: (4, 9, 2),
    12: (4, 9, 3),
    13: (5, 11, 2),
    14: (5, 11, 3),
    15: (5, 11, 4),
    16: (6, 13, 3),
    17: (6, 13, 4),
    18: (7, 15, 3),
    19: (7, 15, 4),
    20: (8, 17, 3),
    21: (8, 17, 4),
    22: (8, 17, 5),
    23: (9, 19, 4),
    24: (9, 19, 5),
    25: (9, 19, 6),
    26: (10, 21, 5),
    27: (10, 21, 6),
    28: (10, 21, 7),
    29: (11, 23, 6),
    30: (11, 23, 7),
}


class CandleOffset(int):

    MAX = 30
    MIN = 1
    DEFAULT = 10
    REQUIRED_RUN_SIZE = 200.0

    def __new__(cls, value: int):
        if value < cls.MIN:
            value = cls.MIN
        elif value > cls.MAX:
            value = cls.MAX
        return super().__new__(cls, value)

    def wick(self):
        return OffsetMap[self][0]

    def far_side(self):
        return OffsetMap[self][1]

    def gap(self):
        return OffsetMap[self][2]

    def grid_adjust(self):
        return OffsetMap[self][2] // 2

    def min_run(self) -> int:
        return ceil(float(Const.MIN_TIME_GRID_WIDTH) / float(self))


# Cast MIN, MAX, and DEFAULT as CandleOffsets rather than normal ints.
CandleOffset.MIN = CandleOffset(CandleOffset.MIN)
CandleOffset.MAX = CandleOffset(CandleOffset.MAX)
CandleOffset.DEFAULT = CandleOffset(CandleOffset.DEFAULT)
