import tkinter
import tk_oddbox
from pathlib import Path


class Initializer:

    initialized = False

    @classmethod
    def initialize(cls, tk: tkinter.Tk):
        if not cls.initialized:
            cls.initialized = True
            cls._initialize_images(tk)

    @staticmethod
    def _initialize_images(tk: tkinter.Tk):
        loader = tk_oddbox.ImageLoader(tk)
        image_data_path = Path(__file__).parent.parent.joinpath("image_data")
        loader.load_dir(image_data_path, "*.png")
