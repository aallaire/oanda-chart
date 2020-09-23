# oanda-chart
Oanda forex candle chart tkinter widget.

### Warning:
This package does not yet have all its core features, and even its
current features might change significantly.

It was uploaded to pypi.org early as an experiment to see if the package
could find some "png" after installation...not because it was at
all ready.

### Some Background
This is being built on top of oanda-candles package which is built
on top of the oandaV20 package, which uses the Oanda Restful API.

It provides a tkinter chart widget and associated widgets to select
the instrument pair, granularity, and ask/mid/bid.


### Version Notes

#### 0.1.0
Big rework. Now has price and time scales. Changes include:

1. Price scale, which can be stretched with mouse to make candles appear taller or shorter.
1. Time scale, which can be stretched with the mouse to make candles wider or narrower, similar to mouse wheel.
1. Both time and price grid lines aligning with scales.
1. Badge in background declaring the instrument pair, granularity, and whether its bid, mid, or ask.
1. Panning up or down will take one out of price view mode.
1. When chart is in focus (which it becomes when panning it) user can use arrow keys on keyboard to move in chart.
1. Enter key on keyboard snaps back to price view mode.
1. In bottom right corner the pips between price grid lines and time interval between time grid lines is shown.
1. Clicking this bottom right corner area snaps chart view back to the default way the chart was set when loaded.
1. The user should not be able to tell, but the scrollable canvas area is now only three times bigger than the viewing area in all directions.
1. Candle times are now aligned on UTC (for example monthly candles start right when the month changes in UTC)
1. The time scale and time on the Candle objects are in UTC (and no longer local or New York time)
1. Features have not been greatly tested, and code got a huge rewrite that could be cleaned up.

###### Still Missing features
1. No geometric annotation items like price lines or rectangles etc are implemented yet...but they are what is being looked at next.
1. No configuration of colors is available yet--all colors are just hard coded with a darkish look.

#### 0.0.4
Overall, I think the core functionality is finally taking shape. Still seriously missing parts, particularly price scale on right and time scale on
 bottom. And there are no drawing utilities yet. What I am happy with is that panning around and candle display and such feel reasonably comparable to "real" candle charts used by retail brokers.
 Including niceness users expect without thinking, like scrunching candles with mouse wheel, and the candles following price when panning.
 
These features are currently working (keep warning in mind, things may change):


1. Flag Pair Selector built in to standard chart by default
1. Menu pull down Pair selector also built in.
1. Granularity pull down as well.
1. Quote Kind (bid/mid/ask) pull down as well.
1. Supports making candles fatter or skinnier with mouse wheel.
1. Supports panning around in two modes--to switch modes double-click.
   1. Price View True: pulls back view up or down to current price and fits the current price action to the view size.
   1. Price View False: user can pan anywhere including above and below prices.
1. If panned so that latest candles are in view, will check for updated candle data every 2 seconds.
1. Draws price grid lines behind candles based, but does NOT yet have a price scale telling you what prices they are.
1. Does NOT yet have a time scale.
1. Pair, Gran, and QuoteKind Selector classes have a color theme that links them together and they can be linked in theory to different charts. The idea is to allow changing the Pair in one chart change it in others as well. Also for granularity and quote kind. The color will be visible on the widgets so users know which are linked.



