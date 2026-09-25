"""Shortest-path search, independent of maze generation and rendering."""

from collections import deque
from collections.abc import Sequence
from typing import Protocol, TypeVar


class CellLike(Protocol):
    """Cell attributes required by the solver, independent of generation."""

    x: int
    y: int
    walls: dict[str, bool]


CellT = TypeVar("CellT", bound=CellLike)
DIRECTIONS = (
    (0, -1, "N", "S"),
    (0, 1, "S", "N"),
    (-1, 0, "W", "E"),
    (1, 0, "E", "W"),
)


def get_valid_neighbours(
    grid: Sequence[Sequence[CellT]], current: CellT,
) -> list[CellT]:
    """Return neighbours with a passage open on both sides."""
    neighbours = []
    for dx, dy, direction, opposite in DIRECTIONS:
        nx, ny = current.x + dx, current.y + dy
        if 0 <= ny < len(grid) and 0 <= nx < len(grid[ny]):
            neighbour = grid[ny][nx]
            if not current.walls[direction] and not neighbour.walls[opposite]:
                neighbours.append(neighbour)
    return neighbours


def bfs(
    grid: Sequence[Sequence[CellT]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> list[CellT]:
    """Return the shortest path (including endpoints), or [] if unreachable.

    Raise ValueError for an empty, malformed grid or out-of-bounds endpoints.
    Neighbours are explored in N, S, W, E order, preserving tie-breaking.
    """
    if not grid or not grid[0]:
        raise ValueError("The maze is empty; generate it before solving")
    width, height = len(grid[0]), len(grid)
    for y, row in enumerate(grid):
        if len(row) != width:
            raise ValueError("The maze must be rectangular")
        for x, cell in enumerate(row):
            if (cell.x, cell.y) != (x, y):
                raise ValueError("Cell coordinates do not match the grid")
            if any(type(cell.walls.get(d)) is not bool for d in "NESW"):
                raise ValueError("Cell walls N, E, S, W must be booleans")
    for name, (x, y) in (("Entry", entry), ("Exit", exit_)):
        if (type(x) is not int or type(y) is not int
                or not (0 <= x < width and 0 <= y < height)):
            raise ValueError(f"{name} must be inside the maze")

    queue = deque([entry])
    parents: dict[tuple[int, int], tuple[int, int] | None] = {entry: None}
    while queue:
        position = queue.popleft()
        if position == exit_:
            return _reconstruct_path(grid, parents, exit_)
        x, y = position
        for neighbour in get_valid_neighbours(grid, grid[y][x]):
            next_position = (neighbour.x, neighbour.y)
            if next_position not in parents:
                parents[next_position] = position
                queue.append(next_position)
    return []


def _reconstruct_path(
    grid: Sequence[Sequence[CellT]],
    parents: dict[tuple[int, int], tuple[int, int] | None],
    target: tuple[int, int],
) -> list[CellT]:
    """Follow BFS parents backwards and return cells in traversal order."""
    path = []
    position: tuple[int, int] | None = target
    while position is not None:
        x, y = position
        path.append(grid[y][x])
        position = parents[position]
    path.reverse()
    return path
