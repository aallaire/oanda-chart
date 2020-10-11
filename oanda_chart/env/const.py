from pathlib import Path
from typing import Union

from forex_types import FracPips, Pair
from oanda_candles.gran import Gran
from oanda_candles.quote_kind import QuoteKind

import os


SelectType = Union[Gran, Pair, QuoteKind]


class CandleColor:
    BULL: str = "#00FF00"
    BEAR: str = "#FF0000"
    DOJI: str = "#aaaaaa"
    WICK: str = "#999999"


class Color:
    BACKGROUND: str = "#000000"
    BADGE: str = "#101010"
    GRID: str = "#333333"
    MIST: str = "#111111"
    PRICE_BG: str = "#333333"
    TIME_BG: str = "#333333"
    LINK_BG: str = "#333333"
    LINK_TEXT: str = "#A0A0A0"
    TIME_TEXT: str = "#888888"
    TOP_BG: str = "#333333"
    MODE_BG: str = "#333333"
    PRICE_TICK: str = "#FFFFFF"
    TIME_DIVIDER: str = "#FFFFFF"
    SCALE_TEXT: str = "#797979"
    SLASH: str = "#424242"
    DOLLAR_TEXT = "#A0A0A0"
    PIP_TEXT = "#707070"
    FPIP_TEXT = "#505050"


class Const:
    DEFAULT_FPP = 10.0  # initial frac pips per pixel value before data loaded.
    FP_MAX: FracPips = FracPips(1_000_000)
    FP_MIN: FracPips = FracPips(0)
    MIN_FPP = 0.01  # lowest allowed value for fpp
    ONE_THIRD = float(1) / float(3)
    PRICE_PAD: FracPips = FracPips(10_000)
    PRICE_VIEW_PAD = 25
    TAIL_PADDING = 50  # num pixels to pad to right of candles when tailing.
    TIME_CANVAS_HEIGHT = 42
    PRICE_CANVAS_WIDTH = 80  # 110
    MIN_TIME_GRID_WIDTH = 120


class PathConst:
    HOME_DIR = Path.home()
    IS_WIN = os.name == "nt"
    WORK_NAME = "python_oanda_charts_package"
    WORK_DIR = (
        HOME_DIR.joinpath("AppData", "local", WORK_NAME)
        if IS_WIN
        else HOME_DIR.joinpath(f".{WORK_NAME}")
    )


class Tag:
    BADGE = "badge"
    CANDLE = "candle"
    MIST = "mist"
    PRICE_GRID = "pricegrid"
    TIME_GRID = "timegrid"
    PRICE_LABEL = "pricelabel"
    SCALE_ITEM = "scaleitem"
    TIME_TEXT = "timetext"


class UnfinishedCandleColor:
    BULL: str = "#447744"
    BEAR: str = "#774444"
    WICK: str = "#777777"
    DOJI: str = "#aaaaaa"


class Event:
    DOUBLE_CLICK: str = "<Double-Button-1>"
    LEFT_CLICK: str = "<ButtonPress-1>"
    LEFT: str = "<Left>"
    RIGHT: str = "<Right>"
    UP: str = "<Up>"
    DOWN: str = "<Down>"
    RETURN: str = "<Return>"
    RIGHT_CLICK = "<Button-3>"
    LEFT_DRAG: str = "<B1-Motion>"
    LEFT_RELEASE: str = "<ButtonRelease-1>"
    MOUSE_WHEEL: str = "<MouseWheel>"
    RESIZE: str = "<Configure>"
