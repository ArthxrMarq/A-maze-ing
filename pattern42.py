"""The mandatory "42" pattern, made of fully closed cells.

The pattern is drawn from two 5x7 dot-matrix digits ("4" and "2") separated
by a one-cell gap, centred inside the maze. It does not depend on any other
part of the project: it only computes which (x, y) cells must stay fully
closed.
"""

from collections.abc import Iterable

_FOUR: tuple[str, ...] = (
    "X...X",
    "X...X",
    "X...X",
    "XXXXX",
    "....X",
    "....X",
    "....X",
)

_TWO: tuple[str, ...] = (
    "XXXXX",
    "....X",
    "....X",
    "XXXXX",
    "X....",
    "X....",
    "XXXXX",
)

_GAP = 1
_DIGIT_WIDTH = len(_FOUR[0])
_DIGIT_HEIGHT = len(_FOUR)
PATTERN_WIDTH = _DIGIT_WIDTH * 2 + _GAP
PATTERN_HEIGHT = _DIGIT_HEIGHT
# The "4" and "2" strokes enclose small pockets of open cells (e.g. inside
# the top of the "4"). Those pockets only connect to the rest of the maze
# through the row/column just outside the pattern's bounding box, so a
# margin of at least one cell is required on every side.
_MARGIN = 1
MIN_WIDTH = PATTERN_WIDTH + 2 * _MARGIN
MIN_HEIGHT = PATTERN_HEIGHT + 2 * _MARGIN


def _digit_cells(
    bitmap: tuple[str, ...], offset_x: int, offset_y: int
) -> set[tuple[int, int]]:
    """Turn a digit bitmap into absolute (x, y) cells.

    Args:
        bitmap: Rows of the digit, 'X' for a filled cell, any other
            character for an empty one.
        offset_x: X coordinate of the bitmap's top-left corner.
        offset_y: Y coordinate of the bitmap's top-left corner.

    Returns:
        The set of absolute (x, y) cells marked 'X' in the bitmap.
    """
    cells: set[tuple[int, int]] = set()
    for row_index, row in enumerate(bitmap):
        for col_index, char in enumerate(row):
            if char == "X":
                cells.add((offset_x + col_index, offset_y + row_index))
    return cells


def forty_two_cells(
    width: int,
    height: int,
    forbidden: Iterable[tuple[int, int]] = (),
) -> set[tuple[int, int]] | None:
    """Compute the cells of the centred "42" pattern, if it fits.

    Args:
        width: Maze width, in cells.
        height: Maze height, in cells.
        forbidden: Cells that must stay free (typically entry and exit).

    Returns:
        The set of (x, y) cells that must be fully closed to draw the
        "42", or None if the maze is too small for the pattern (including
        its safety margin), or if the pattern would overlap one of the
        forbidden cells.
    """
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return None

    top_left_x = (width - PATTERN_WIDTH) // 2
    top_left_y = (height - PATTERN_HEIGHT) // 2

    cells = _digit_cells(_FOUR, top_left_x, top_left_y)
    cells |= _digit_cells(_TWO, top_left_x + _DIGIT_WIDTH + _GAP, top_left_y)

    if cells.intersection(forbidden):
        return None
    return cells