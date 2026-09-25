"""Validation of the maze rules required by the subject.

The validator only needs a grid of cells exposing a ``walls`` dict with the
keys "N", "E", "S", "W" (True means the wall is closed). It does not depend
on any other part of the project.

When pattern coordinates are supplied, only those cells may be fully closed.
For compatibility, callers without pattern coordinates still treat every
fully closed cell as part of the pattern.
"""

from collections import deque
from collections.abc import Sequence
from typing import Protocol

DIRECTIONS: dict[str, tuple[int, int]] = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}
OPPOSITE: dict[str, str] = {"N": "S", "S": "N", "E": "W", "W": "E"}


class CellLike(Protocol):
    """Minimal interface of a maze cell: its four walls."""

    walls: dict[str, bool]


Grid = Sequence[Sequence[CellLike]]


def is_closed(cell: CellLike) -> bool:
    """Tell whether a cell has its four walls closed.

    Args:
        cell: The cell to inspect.

    Returns:
        True if North, East, South and West walls are all closed.
    """
    return all(cell.walls[direction] for direction in DIRECTIONS)


def has_passage(grid: Grid, x: int, y: int, direction: str) -> bool:
    """Tell whether one can walk from (x, y) towards a direction.

    A passage exists only if the neighbour is inside the maze and the wall
    is open on both sides.

    Args:
        grid: The maze, indexed as grid[y][x].
        x: Column of the cell.
        y: Row of the cell.
        direction: One of "N", "E", "S", "W".

    Returns:
        True if the passage is open.
    """
    dx, dy = DIRECTIONS[direction]
    nx, ny = x + dx, y + dy
    if not (0 <= ny < len(grid) and 0 <= nx < len(grid[ny])):
        return False
    return (not grid[y][x].walls[direction]
            and not grid[ny][nx].walls[OPPOSITE[direction]])


def open_neighbours(grid: Grid, x: int, y: int) -> list[tuple[int, int]]:
    """List the cells reachable in one step from (x, y).

    Args:
        grid: The maze, indexed as grid[y][x].
        x: Column of the cell.
        y: Row of the cell.

    Returns:
        The (x, y) coordinates of the neighbours behind an open passage.
    """
    result: list[tuple[int, int]] = []
    for direction, (dx, dy) in DIRECTIONS.items():
        if has_passage(grid, x, y, direction):
            result.append((x + dx, y + dy))
    return result


def check_shape(grid: Grid) -> list[str]:
    """Check that the grid is not empty and is rectangular.

    Args:
        grid: The maze, indexed as grid[y][x].

    Returns:
        A list of error messages (empty if the shape is valid).
    """
    if not grid or not grid[0]:
        return ["The maze is empty"]
    width = len(grid[0])
    for y, row in enumerate(grid):
        if len(row) != width:
            return [f"Row {y} has {len(row)} cells, expected {width}"]
    return []


def check_entry_exit(
    grid: Grid, entry: tuple[int, int], exit_: tuple[int, int]
) -> list[str]:
    """Check that entry and exit exist, are inside the maze and differ.

    Args:
        grid: The maze, indexed as grid[y][x].
        entry: Entry coordinates (x, y).
        exit_: Exit coordinates (x, y).

    Returns:
        A list of error messages (empty if valid).
    """
    errors: list[str] = []
    height, width = len(grid), len(grid[0])
    if entry == exit_:
        errors.append("Entry and exit must be different cells")
    for name, (x, y) in (("Entry", entry), ("Exit", exit_)):
        if not (0 <= x < width and 0 <= y < height):
            errors.append(f"{name} ({x},{y}) is outside the maze")
        elif is_closed(grid[y][x]):
            errors.append(f"{name} ({x},{y}) is a fully closed cell")
    return errors


def check_borders(grid: Grid) -> list[str]:
    """Check that every external border of the maze is a wall.

    Args:
        grid: The maze, indexed as grid[y][x].

    Returns:
        A list of error messages (empty if valid).
    """
    errors: list[str] = []
    height, width = len(grid), len(grid[0])
    for x in range(width):
        if not grid[0][x].walls["N"]:
            errors.append(f"Cell ({x},0) has no north border wall")
        if not grid[height - 1][x].walls["S"]:
            errors.append(f"Cell ({x},{height - 1}) has no south border wall")
    for y in range(height):
        if not grid[y][0].walls["W"]:
            errors.append(f"Cell (0,{y}) has no west border wall")
        if not grid[y][width - 1].walls["E"]:
            errors.append(f"Cell ({width - 1},{y}) has no east border wall")
    return errors


def check_coherence(grid: Grid) -> list[str]:
    """Check that neighbouring cells agree on their shared wall.

    Args:
        grid: The maze, indexed as grid[y][x].

    Returns:
        A list of error messages (empty if valid).
    """
    errors: list[str] = []
    height, width = len(grid), len(grid[0])
    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            if x + 1 < width and cell.walls["E"] != grid[y][x + 1].walls["W"]:
                errors.append(
                    f"Cells ({x},{y}) and ({x + 1},{y}) disagree "
                    "about their shared wall"
                )
            if y + 1 < height and cell.walls["S"] != grid[y + 1][x].walls["N"]:
                errors.append(
                    f"Cells ({x},{y}) and ({x},{y + 1}) disagree "
                    "about their shared wall"
                )
    return errors


def check_connectivity(grid: Grid, entry: tuple[int, int]) -> list[str]:
    """Check that every non-closed cell is reachable from the entry.

    Fully closed cells (the "42" pattern) are allowed to be isolated.

    Args:
        grid: The maze, indexed as grid[y][x].
        entry: Entry coordinates (x, y), assumed to be inside the maze.

    Returns:
        A list of error messages (empty if valid).
    """
    height, width = len(grid), len(grid[0])
    seen = {entry}
    queue = deque([entry])
    while queue:
        x, y = queue.popleft()
        for neighbour in open_neighbours(grid, x, y):
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    unreachable = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in seen and not is_closed(grid[y][x])
    ]
    if not unreachable:
        return []
    shown = ", ".join(f"({x},{y})" for x, y in unreachable[:5])
    suffix = ", ..." if len(unreachable) > 5 else ""
    return [
        f"{len(unreachable)} cell(s) unreachable from the entry: "
        f"{shown}{suffix}"
    ]


def is_open_block(grid: Grid, x: int, y: int, size: int) -> bool:
    """Tell whether a size x size block has no wall inside it.

    Args:
        grid: The maze, indexed as grid[y][x].
        x: Column of the top-left cell of the block.
        y: Row of the top-left cell of the block.
        size: Side of the block, in cells.

    Returns:
        True if every passage between cells of the block is open.
    """
    for j in range(size):
        for i in range(size):
            if i < size - 1 and not has_passage(grid, x + i, y + j, "E"):
                return False
            if j < size - 1 and not has_passage(grid, x + i, y + j, "S"):
                return False
    return True


def check_open_areas(grid: Grid, size: int = 3) -> list[str]:
    """Check that the maze has no open area of size x size (3x3 by default).

    Args:
        grid: The maze, indexed as grid[y][x].
        size: Side of the forbidden open block.

    Returns:
        A list of error messages (empty if valid).
    """
    errors: list[str] = []
    height, width = len(grid), len(grid[0])
    for y in range(height - size + 1):
        for x in range(width - size + 1):
            if is_open_block(grid, x, y, size):
                errors.append(
                    f"Open {size}x{size} area with top-left corner ({x},{y})"
                )
    return errors


def count_graph(grid: Grid) -> tuple[int, int]:
    """Count the open cells and the passages between them.

    Args:
        grid: The maze, indexed as grid[y][x].

    Returns:
        A tuple (number of non-closed cells, number of passages).
    """
    cells = 0
    passages = 0
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if is_closed(cell):
                continue
            cells += 1
            if has_passage(grid, x, y, "E"):
                passages += 1
            if has_passage(grid, x, y, "S"):
                passages += 1
    return cells, passages


def check_perfect(grid: Grid) -> list[str]:
    """Check that the maze is perfect: no loop, a single path anywhere.

    A connected maze is perfect when passages == cells - 1 (a tree).

    Args:
        grid: The maze, indexed as grid[y][x].

    Returns:
        A list of error messages (empty if valid).
    """
    cells, passages = count_graph(grid)
    loops = passages - cells + 1
    if loops > 0:
        return [
            f"PERFECT=True but the maze has {loops} loop(s): "
            "only one path between two cells is allowed"
        ]
    return []


def check_playable(grid: Grid, max_dead_ends: int) -> list[str]:
    """Check the rules of the non-perfect (Pac-Man like) mode.

    The four corners and the centre must be open, there must be at least
    two independent loops, and dead-ends must stay rare.

    Args:
        grid: The maze, indexed as grid[y][x].
        max_dead_ends: Maximum number of dead-ends tolerated.

    Returns:
        A list of error messages (empty if valid).
    """
    errors: list[str] = []
    height, width = len(grid), len(grid[0])

    spots = {
        "corner": [(0, 0), (width - 1, 0), (0, height - 1),
                   (width - 1, height - 1)],
        "centre": [(width // 2, height // 2)],
    }
    for label, coords in spots.items():
        for x, y in coords:
            if is_closed(grid[y][x]):
                errors.append(
                    f"The {label} cell ({x},{y}) must be an open corridor"
                )

    cells, passages = count_graph(grid)
    loops = max(passages - cells + 1, 0)
    if loops < 2:
        errors.append(
            f"PERFECT=False needs at least 2 independent routes "
            f"(loops), found {loops}"
        )

    dead_ends = [
        (x, y)
        for y, row in enumerate(grid)
        for x, cell in enumerate(row)
        if not is_closed(cell) and len(open_neighbours(grid, x, y)) == 1
    ]
    if len(dead_ends) > max_dead_ends:
        shown = ", ".join(f"({x},{y})" for x, y in dead_ends[:5])
        suffix = ", ..." if len(dead_ends) > 5 else ""
        errors.append(
            f"{len(dead_ends)} dead-end(s) found (max allowed: "
            f"{max_dead_ends}): {shown}{suffix}"
        )
    return errors


def validate_maze(
    grid: Grid,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    perfect: bool,
    max_dead_ends: int = 2,
    *,
    pattern_cells: set[tuple[int, int]] | None = None,
) -> list[str]:
    """Check a generated maze against every rule of the subject.

    Rules checked: valid entry/exit, closed external borders, coherent
    shared walls, full connectivity (except the "42" cells), no 3x3 open
    area, and either the perfect-maze rule or the playable-board rules
    depending on ``perfect``.

    Args:
        grid: The maze, indexed as grid[y][x].
        entry: Entry coordinates (x, y).
        exit_: Exit coordinates (x, y).
        perfect: Value of the PERFECT flag.
        max_dead_ends: Dead-ends tolerated when ``perfect`` is False.
        pattern_cells: Actual reserved cells. If supplied, reject closed
            cells outside the pattern and opened cells inside it.

    Returns:
        A list of human-readable errors. Empty means the maze is valid.
    """
    errors = check_shape(grid)
    if errors:
        return errors
    if pattern_cells is not None:
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if (x, y) in pattern_cells and not is_closed(cell):
                    errors.append(f"Pattern cell ({x},{y}) must be closed")
                elif (x, y) not in pattern_cells and is_closed(cell):
                    errors.append(f"Cell ({x},{y}) is isolated outside '42'")
        if errors:
            return errors
    errors = check_entry_exit(grid, entry, exit_)
    if errors:
        return errors

    errors += check_borders(grid)
    errors += check_coherence(grid)
    errors += check_connectivity(grid, entry)
    errors += check_open_areas(grid)
    if perfect:
        errors += check_perfect(grid)
    else:
        errors += check_playable(grid, max_dead_ends)
    return errors
