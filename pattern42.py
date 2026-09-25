"""The mandatory "42" pattern, made of fully closed cells.

The pattern is drawn from two 5x7 dot-matrix digits ("4" and "2") separated
by a one-cell gap, preferably centred inside the maze. It does not depend
on any other part of the project: it only computes which (x, y) cells must
stay fully closed.
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
    """Place the "42" near the centre, avoiding forbidden cells.

    Args:
        width: Maze width, in cells.
        height: Maze height, in cells.
        forbidden: Cells that must stay free (typically entry and exit).

    Returns:
        The set of (x, y) cells that must be fully closed to draw the
        "42", or None if the maze is too small for the pattern (including
        its safety margin), or if no placement avoids forbidden cells.
    """
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return None

    top_left_x = (width - PATTERN_WIDTH) // 2
    top_left_y = (height - PATTERN_HEIGHT) // 2

    blocked = set(forbidden)
    # Prefer the original centred position, then the closest alternatives.
    positions = sorted(
        ((x, y)
         for y in range(_MARGIN, height - PATTERN_HEIGHT)
         for x in range(_MARGIN, width - PATTERN_WIDTH)),
        key=lambda pos: (abs(pos[0] - top_left_x)
                         + abs(pos[1] - top_left_y), pos[1], pos[0]),
    )
    for x, y in positions:
        cells = _digit_cells(_FOUR, x, y)
        cells |= _digit_cells(_TWO, x + _DIGIT_WIDTH + _GAP, y)
        if not cells.intersection(blocked):
            return cells
    return None
