"""A GeoCandles object manages candles and geometry for a chart.

Independent GeoCandles attributes set by user:
    * view    : The width of the view
    * height  : The height of the view
    * pair    : The forex pair to be viewed
    * gran    : The granularity to be viewed
    * ndx     : How many candles back to pan.
    * offset  : The pixel offset (width) of candles to draw.

Semi-Independent GeoCandles attribute, set by user, but subject to change:
   * price_view : Boolean option indicating view should center on candle prices.
                  Automatically becomes False when user sets fp_mid or fpp.
   * fp_mid     : The fractional pip price in the middle of the chart.
                  Subject to automatic change while price_view is True.
   * fpp        : Ratio of fractional pips per pixel of height.
                  Subject to automatic change while price_view is True.

Dependent GeoCandles attributes, subject to change per other attributes:
   * collector  : CandleCollector to request and cache candle from Oanda.
   * xandles    : A Xandles object loaded with candle and x-coordinate data.
   * yrids      : A Yrids object loaded with price scale and y-coordinate data.
"""


from math import ceil
from typing import Optional
from uuid import uuid4

from oanda_candles import CandleCollector, CandleMeister, Gran, QuoteKind
from forex_types import FracPips, Pair

from oanda_chart.geo.price_scale import PriceScale
from oanda_chart.geo.xandles import Xandles
from oanda_chart.geo.yrids import Yrids
from oanda_chart.geo.candle_offset import CandleOffset


class GeoCandleDefaults:
    WIDTH = 640
    HEIGHT = 480
    PAIR = Pair.EUR_USD
    GRAN = Gran.H1
    OFFSET = CandleOffset.DEFAULT
    QUOTE_KIND = QuoteKind.MID
    NDX = 0


class GeoCandles:
    def __init__(
        self,
        width: int = GeoCandleDefaults.WIDTH,
        height: int = GeoCandleDefaults.HEIGHT,
        pair: Pair = GeoCandleDefaults.PAIR,
        gran: Gran = GeoCandleDefaults.GRAN,
        quote_kind: QuoteKind = GeoCandleDefaults.QUOTE_KIND,
        offset: CandleOffset = GeoCandleDefaults.OFFSET,
        ndx: int = GeoCandleDefaults.NDX,
        price_view: bool = True,
    ):
        self.collector: CandleCollector = CandleMeister.get_collector(pair, gran)
        self.pair: Pair = pair
        self.gran: Gran = gran
        self.quote_kind: QuoteKind = quote_kind
        self.price_view: bool = price_view
        self.run_id: Optional[str] = None
        candles = self.collector.grab(Xandles.calculate_pull_size(width, offset, ndx))
        self.xandles: Xandles = Xandles(
            offset=offset, width=width, candles=candles, ndx=ndx
        )
        fp_mid, fpp = Yrids.calculate_price_view(self.xandles, height)
        scale = PriceScale(fpp)
        self.yrids: Yrids = Yrids(height=height, mid=fp_mid, fpp=fpp, scale=scale)

    def get_report(self) -> str:
        """Get human readable report about state of geo candles.
        
        (This method is meant to assist development and debugging).
        """
        lines = list()
        view_candles = [_ for _ in self.xandles.iter_view_candles()]
        lines.append("GeoCandles State:\n")
        lines.append(f"    bot           : {self.yrids.bot}\n")
        lines.append(f"    candles       : list of {len(self.xandles.candles)}\n")
        lines.append(f"    fpp           : {self.yrids.fpp}\n")
        lines.append(f"    gran          : {self.gran}\n")
        lines.append(f"    grid_list     : list of {len(self.yrids.grid_list)}\n")
        lines.append(f"    height        : {self.yrids.height}\n")
        lines.append(f"    mid           : {self.yrids.mid}\n")
        lines.append(f"    ndx           : {self.xandles.ndx}\n")
        lines.append(f"    offset        : {self.xandles.offset}\n")
        lines.append(f"    pair          : {self.pair}\n")
        lines.append(f"    price_view    : {self.price_view}\n")
        lines.append(f"    showing_recent: {self.xandles.showing_recent}\n")
        lines.append(f"    scale         : {self.yrids.scale}\n")
        lines.append(f"    scroll_bot    : {self.yrids.scroll_bot}\n")
        lines.append(f"    scroll_height : {self.yrids.scroll_height}\n")
        lines.append(f"    scroll_top    : {self.yrids.scroll_top}\n")
        lines.append(f"    scroll_width  : {self.xandles.scroll_width}\n")
        lines.append(f"    top           : {self.yrids.top}\n")
        lines.append(f"    width         : {self.xandles.width}\n")
        lines.append(f"    view_candles  : iteration of {len(view_candles)}\n")
        return "".join(lines)

    def refresh(self):
        if self.price_view:
            self.update(
                offset=self.xandles.offset,
                width=self.xandles.width,
                ndx=self.xandles.ndx,
                price_view=True,
            )
        else:
            self.update(
                offset=self.xandles.offset,
                width=self.xandles.width,
                ndx=self.xandles.ndx,
                height=self.yrids.height,
                mid=self.yrids.mid,
                fpp=self.yrids.fpp,
                scale=self.yrids.scale,
            )

    def update(
        self,
        offset: Optional[CandleOffset] = None,
        width: Optional[int] = None,
        ndx: Optional[int] = None,
        height: Optional[int] = None,
        mid: Optional[FracPips] = None,
        quote_kind: Optional[QuoteKind] = None,
        fpp: Optional[float] = None,
        scale: Optional[PriceScale] = None,
        price_view: Optional[bool] = None,
    ):
        """Updates the GeoData attributes and resolves changes.

        Args:
            offset: candle offset, width of one candle to the next.
            width: width of viewing area in pixels
            ndx: how many candles to the past we have panned.
            height: height of view in in pixels.
            mid: frac pips price of mid point of view.
            fpp: ratio of frac pips per pixel
            scale: price scale object indicating frac pips between price grid lines.
            price_view: boolean to switch price_view mode on or off
        Raises:
            AttributeError: if price_view set to True while mid and/or fpp are set.
            AttributeError: if mid or fpp are set when offset, width, candles, or ndx are set.
        """
        candles = None
        if quote_kind is not None:
            self.quote_kind = quote_kind
        if width is not None or offset is not None or ndx is not None:
            w = width if width is not None else self.xandles.width
            o = offset if offset is not None else self.xandles.offset
            n = ndx if ndx is not None else self.xandles.ndx
            if n is not None and w is not None and o is not None:
                pull_size = Xandles.calculate_pull_size(w, o, n)
                candles = self.collector.grab(pull_size)
        self.xandles.update(offset=offset, width=width, candles=candles, ndx=ndx)
        if price_view is not None:
            self.price_view = price_view
        if price_view is True:
            self.yrids.update(height=height, scale=scale)
            if self.xandles.can_resolve() and self.yrids.can_resolve():
                mid, fpp = Yrids.calculate_price_view(self.xandles, self.yrids.height)
                if scale is None:
                    scale = PriceScale(fpp)
                self.yrids.update(mid=mid, fpp=fpp, scale=scale)
        else:
            if mid is not None or fpp is not None:
                self.price_view = False
            if scale is None and fpp is not None:
                scale = PriceScale(fpp)
            self.yrids.update(height=height, mid=mid, fpp=fpp, scale=scale)

    def shift(self, x: int, y: int):
        """Shift GeoCandles data the given amount.

        Args:
            x: horizontal pixels where to the right is positive.
            y: vertical pixels where down is positive.
        """
        candle_slot_shift = ceil(x / self.xandles.offset)
        new_ndx = self.xandles.ndx - candle_slot_shift
        pad_adjust = Xandles.PAD * 4
        min_slots = round((self.xandles.width - pad_adjust) / self.xandles.offset)
        if new_ndx < 0:
            new_ndx = 0
        pull_size = Xandles.calculate_pull_size(
            self.xandles.width, self.xandles.offset, new_ndx
        )
        candles = self.collector.grab(pull_size)
        max_ndx = len(candles) - min_slots
        if max_ndx <= 0:
            max_ndx = 1
        if new_ndx >= max_ndx:
            new_ndx = max_ndx
        self.xandles.update(candles=candles, ndx=new_ndx)
        if self.price_view:
            fp_mid, fpp = Yrids.calculate_price_view(self.xandles, self.yrids.height)
            self.yrids.update(mid=fp_mid, fpp=fpp)
        else:
            fp_shift = round(y * self.yrids.fpp)
            new_mid = FracPips(self.yrids.mid - fp_shift)
            self.yrids.update(mid=new_mid)
        self.refresh()
