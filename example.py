import tkinter
import os

from oanda_chart import ChartManager
from oanda_chart.util.syntax_candy import grid
from oanda_chart import LinkColor
from oanda_candles import Gran, QuoteKind


class App:

    root = tkinter.Tk()
    manager = ChartManager(os.getenv("OANDA_TOKEN"))

    def __init__(self):
        self.chart = self.manager.create_chart(
            self.root, flags=True, width=700, height=400,
        )
        self.manager.set_gran(LinkColor.ChartDefault, Gran.H1)
        self.manager.set_quote_kind(LinkColor.ChartDefault, QuoteKind.BID)
        grid(self.chart, 0, 0)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)


if __name__ == "__main__":

    app = App()
    app.root.mainloop()
