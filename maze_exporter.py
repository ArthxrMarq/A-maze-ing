"""Write hexadecimal maze walls and the shortest path in subject format."""

import os
from collections.abc import Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile

from maze_solver import CellLike, bfs
from maze_validator import check_borders, check_coherence


def maze_text(grid: Sequence[Sequence[CellLike]],
              entry: tuple[int, int], exit_: tuple[int, int]) -> str:
    """Return encoded rows, a blank line, endpoints and N/E/S/W directions.

    Raise ValueError for malformed walls, open borders or an absent solution.
    """
    path = bfs(grid, entry, exit_)
    errors = check_borders(grid) + check_coherence(grid)
    if errors:
        raise ValueError("Cannot export maze: " + "; ".join(errors))
    if not path:
        raise ValueError("Cannot export maze: no path connects entry and exit")
    lines = []
    for row in grid:
        line = ""
        for cell in row:
            value = 0
            for direction, bit in (("N", 1), ("E", 2), ("S", 4), ("W", 8)):
                if cell.walls[direction]:
                    value += bit
            line += format(value, "X")
        lines.append(line)

    directions = ""
    for index in range(1, len(path)):
        previous = path[index - 1]
        current = path[index]
        if current.x > previous.x:
            directions += "E"
        elif current.x < previous.x:
            directions += "W"
        elif current.y > previous.y:
            directions += "S"
        else:
            directions += "N"
    lines.append("")
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit_[0]},{exit_[1]}")
    lines.append(directions)
    return "\n".join(lines) + "\n"


def write_maze(grid: Sequence[Sequence[CellLike]],
               entry: tuple[int, int], exit_: tuple[int, int],
               filename: str) -> None:
    """Save a complete maze; keep an existing file intact if writing fails.

    A temporary file in the destination directory is replaced only after
    writing succeeds. OSError and ValueError are handled by the caller.
    """
    content = maze_text(grid, entry, exit_)
    destination = Path(filename)
    temporary: str | None = None
    try:
        with NamedTemporaryFile(mode="w", encoding="ascii", newline="\n",
                                dir=destination.parent, prefix=".maze-",
                                delete=False) as file:
            temporary = file.name
            file.write(content)
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)
