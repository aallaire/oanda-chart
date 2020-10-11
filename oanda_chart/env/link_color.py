from magic_kind import MagicKind

from .const import Color


class ValidColors(MagicKind):
    BLACK = "black"
    BLUE = "blue"
    BROWN = "saddle brown"
    CYAN = "cyan"
    DARK_GREEN = "dark green"
    GREEN = "green"
    MAGENTA = "magenta2"
    ORANGE = "orange"
    ORANGE_RED = "orange red"
    PINK = "pink"
    PURPLE = "purple2"
    RED = "red"
    WHITE = "white"
    YELLOW = "yellow"
    YELLOW_GREEN = "yellow green"
    DEFAULT = Color.LINK_BG


CONTRAST_COLOR = {
    ValidColors.BLACK: "white",
    ValidColors.BLUE: "white",
    ValidColors.BROWN: "white",
    ValidColors.CYAN: "black",
    ValidColors.DARK_GREEN: "white",
    ValidColors.GREEN: "white",
    ValidColors.MAGENTA: "white",
    ValidColors.ORANGE: "white",
    ValidColors.ORANGE_RED: "white",
    ValidColors.PINK: "black",
    ValidColors.PURPLE: "white",
    ValidColors.RED: "white",
    ValidColors.WHITE: "black",
    ValidColors.YELLOW: "black",
    ValidColors.YELLOW_GREEN: "black",
    ValidColors.DEFAULT: Color.LINK_TEXT,
}


class LinkColor(str):

    BLACK: "LinkColor" = None
    BLUE: "LinkColor" = None
    BROWN: "LinkColor" = None
    CYAN: "LinkColor" = None
    DARK_GREEN: "LinkColor" = None
    GREEN: "LinkColor" = None
    MAGENTA: "LinkColor" = None
    ORANGE: "LinkColor" = None
    ORANGE_RED: "LinkColor" = None
    PINK: "LinkColor" = None
    PURPLE: "LinkColor" = None
    RED: "LinkColor" = None
    WHITE: "LinkColor" = None
    YELLOW: "LinkColor" = None
    YELLOW_GREEN: "LinkColor" = None

    ChartDefault: "LinkColor" = None

    def __new__(cls, value: str):
        if value not in ValidColors:
            raise ValueError(f"Not a valid LinkColor value: {value}")
        self = str.__new__(cls, value)
        self.contrast = CONTRAST_COLOR.get(value, "white")
        return self


LinkColor.BLACK = LinkColor(ValidColors.BLACK)
LinkColor.BLUE = LinkColor(ValidColors.BLUE)
LinkColor.BROWN = LinkColor(ValidColors.BROWN)
LinkColor.CYAN = LinkColor(ValidColors.CYAN)
LinkColor.DARK_GREEN = LinkColor(ValidColors.DARK_GREEN)
LinkColor.GREEN = LinkColor(ValidColors.GREEN)
LinkColor.MAGENTA = LinkColor(ValidColors.MAGENTA)
LinkColor.ORANGE = LinkColor(ValidColors.ORANGE)
LinkColor.ORANGE_RED = LinkColor(ValidColors.ORANGE_RED)
LinkColor.PINK = LinkColor(ValidColors.PINK)
LinkColor.PURPLE = LinkColor(ValidColors.PURPLE)
LinkColor.RED = LinkColor(ValidColors.RED)
LinkColor.WHITE = LinkColor(ValidColors.WHITE)
LinkColor.YELLOW = LinkColor(ValidColors.YELLOW)
LinkColor.YELLOW_GREEN = LinkColor(ValidColors.YELLOW_GREEN)

LinkColor.ChartDefault = LinkColor(ValidColors.DEFAULT)
