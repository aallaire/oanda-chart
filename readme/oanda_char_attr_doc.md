# oanda-chart attribute chart

Attr Name | Type | Description
--- | --- | ---
candle_ndx | int | how many candles have we panned back from the current candle.
collector | CandleCollector | to grab candle data from Oanda for pair and gran.
gran | Gran | for granularity of candle, such as 1 week, 2 hour etc
fp_bottom| FracPips | price at bottom of scrollable area in fractional pips
fp_top| FracPips | price at top of scrollable area in fractional pips
fpp | int | "Fractional Pips per Pixel", each pixel of height represents this many frac pips.
future_slots | int | number of candle slots to leave blank to right of most recent candle.
marked_x | int | pixel coordinate of last left mouse click when panning window.
missing_history | int | number of candle slots to leave blank to left because historical data from Oanda does not go back further.
offset | CandleOffset | pixel width of a candle including gap to start of next.
pair | Pair | the forex pair (instrument) candles are for.
price_view | bool | Option to dynamically adjust prices to fit view.
quote_kind | QuoteKind | whether we should display ask/mid/bid
slots | int | number of candles that can fit in the scroll width.
scroll_height | int | pixel height of scrollable area
scroll_width | int | pixel width of scrollable area
tailing | bool | Option to keep updating chart with more recent candles.
token | str | secret Oanda API access token
view_height | int | pixel height of canvas, same as Canvas.cget("height")
view_width | int | pixel width of canvas, same as Canvas.cget("width")






