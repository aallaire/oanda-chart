from typing import List, Tuple, Optional
from tkinter import Widget, Canvas, Button
import math

from oanda_candles import QuoteKind, CandleMeister, Pair, Gran


from oanda_chart.geo.candle_offset import CandleOffset
from oanda_chart.geo.coords import Coords
from oanda_chart.geo.candles_element import CandlesElement


class Event:
    LEFT_CLICK: str = "<ButtonPress-1>"
    LEFT_DRAG: str = "<B1-Motion>"
    RESIZE: str = "<Configure>"


class TestCanvas(Canvas):

    view_height = 200
    scroll_height = 200

    view_width = 400

    scroll_width = 1000

    def __init__(self, parent: Widget):
        region = (0, 0, self.scroll_width, self.scroll_height)
        Canvas.__init__(
            self,
            master=parent,
            background="black",
            height=self.view_height,
            scrollregion=region,
            width=self.view_width,
        )
        self.draw(150, "red")
        self.draw(300, "orange")
        self.draw(450, "yellow")
        self.draw(600, "green")
        self.draw(750, "blue")
        self.draw(900, "purple")

        self.bind(Event.LEFT_CLICK, self.scroll_start)
        self.bind(Event.LEFT_DRAG, self.scroll_move)

    def draw(self, x, color):
        self.create_text(x, 10, text=str(x), fill=color)
        self.create_text(x, 190, text=str(x), fill=color)
        self.create_line(x, 20, x, 180, fill=color)

    def goto_pixel(self, x):
        num_pixels = self.scroll_width
        right = x
        left = max(x - self.view_width, 0)
        fraction = left / num_pixels
        print("- " * 33)
        print(f"num_pixels: {num_pixels}")
        print(f"right     : {right}")
        print(f"left      : {left}")
        print(f"fraction  : {fraction}")
        print("- " * 33)
        self.xview_moveto(fraction)

    def get_height(self):
        return int(self.cget("height"))

    def get_width(self):
        return int(self.cget("width"))

    def scroll_start(self, event):
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)
