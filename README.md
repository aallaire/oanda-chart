# oanda-chart
Oanda forex candle chart tkinter widget.

# Video Demo
[YouTube demo of chart widget](https://youtu.be/rPa5l9m_QI8)

#### Quick Sample of Usage
This code is a complete script for a working chart provided that:
1. There is a working internet connection.
1. An `OANDA_TOKEN` environmental variable is set to a valid access token.
```python
import tkinter
import os

from oanda_chart import ChartManager

root = tkinter.Tk()
manager = ChartManager(os.getenv("OANDA_TOKEN"))
chart = manager.create_chart(root, flags=True, width=700, height=400)
chart.grid(row=0, column=0, sticky="nsew")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.mainloop()
```

#### Some Background
The charts rely on the [oanda-candles](https://pypi.org/project/oanda-candles/)
package which pulls candles from [Oanda](http://oanda.com) through their
[V20 Restful API](http://developer.oanda.com/rest-live-v20/introduction/) The user must supply a
secret token string that is associated with either a demo or real brokerage account with
Oanda.

### Feature Summary
1. This is strictly for tkinter applications.
1. Only Oanda Forex candles are charted.
1. User must supply a secret access token to their Oanda account.
1. By dragging on chart user can pan about and candles are downloaded automatically as needed.
1. Chart automatically keeps candles up to date with checks for recent prices every 5 seconds.
1. Panning around can be done both in and out of a mode where the candles are adjusted to fit view.
1. Dragging mouse on price scale makes candles taller or shorter. 
1. Dragging mouse on time scale makes them fatter or narrower (and so does mouse wheel).
1. An optional Pair (instrument) selector with flags matching currency is an option for the chart.
1. Pair (instruments) are also selectable from drop down.
1. Granularity of candles (e.g. Monthly, hourly, etc) are limited to certain values supported by Oanda's V20 API.
1. Bid, Mid, or Ask price can be selected for (default is Bid).
1. All the selectors can be linked to one of several colors to enable changing a pair for one chart to also change it for others and such.

### Some Missing Features
Some features a trader might expect of a candle applications but which are presently missing:
1. There are no annotations supported yet (no putting lines, or text, etc in chart).
1. There is not selection mechanism for candles to see stats on them specifically.
1. There is no way to place an order or see your order info.
1. There are no indicators other than the candles.

