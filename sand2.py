import os
from oanda_chart.geo.xandles import Xandles
from oanda_chart.geo.yrids import Yrids
from oanda_chart.geo.candle_offset import CandleOffset
from oanda_chart.geo.geo_candles import GeoCandles
from forex_types import FracPips, Currency

from oanda_candles import CandleMeister, Pair, Gran

CandleMeister.init_meister(os.getenv("OANDA_TOKEN"))
TOKEN = os.getenv("OANDA_TOKEN")

candles = CandleMeister.grab(Pair.AUD_CAD, Gran.H2, 100)


def play_with_xandles():
    xandles = Xandles(offset=CandleOffset.DEFAULT, width=1000, candles=candles, ndx=2)

    for x, candle in xandles.display_list:
        print(f"{x}  :  {candle}")
    print(f"pixels left  {xandles.pixels_left}")
    print(f"pixels right {xandles.pixels_right}")


def play_with_yrids():
    dollar = FracPips(100_000)
    yrids = Yrids(mid=dollar, height=500, fpp=10)
    print(yrids)
    print(f"scroll_top: {yrids.scroll_top.to_quote_price(Currency.USD)}")
    print(f"top       : {yrids.top.to_quote_price(Currency.USD)}")
    print(f"mid       : {yrids.mid.to_quote_price(Currency.USD)}")
    print(f"bot       : {yrids.bot.to_quote_price(Currency.USD)}")
    print(f"scroll_bot: {yrids.scroll_bot.to_quote_price(Currency.USD)}")


def play_with_gc():
    gc = GeoCandles(TOKEN, pair=Pair.AUD_USD, gran=Gran.M, offset=CandleOffset(5))
    print(gc.get_report())
    gc.update(price_view=True)
    gc.shift(-100, 20)
    print(gc.get_report())


# play_with_xandles()
# play_with_yrids()
play_with_gc()
