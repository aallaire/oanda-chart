"""To make common function calls more concise."""


from tkinter import Widget


def grid(widget: Widget, row: int, column: int, r=1, c=1):
    """Syntax candy for common use of grid geometry management method.

    always has sticky set to "nsew".

    Args:
        widget: the widget to be placed.
        row: row number (0 and up).
        column: column number (0 and up).
        r: optional row span
        c: optional column span
    """
    widget.grid(row=row, column=column, rowspan=r, columnspan=c, sticky="nsew")
