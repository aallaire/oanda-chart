from typing import Iterable, Tuple

from oanda_candles import Candle, Price


def get_candle_range(candles: Iterable[Candle],) -> Tuple[Price, Price]:
    """Find lowest and highest prices in candles as Fractional Pips.

    Args:
        candles: some iterable of candles.
    Returns:
        lowest price, highest price
    Raises:
        AttributeError: if no candles.
    """
    high = None
    low = None
    for candle in candles:
        if candle is None:
            continue
        if high is None or high < candle.ask.h:
            high = candle.ask.h
        if low is None or low > candle.bid.l:
            low = candle.bid.l
    if high is None or low is None:
        raise AttributeError("Need at least one candle to get price range.")
    return low, high
