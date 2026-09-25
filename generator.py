"""Maze generation and ASCII display: the reusable part of the project."""

import random
from typing import Any

from config_parser import validate_config
from maze_solver import bfs
from maze_validator import count_graph, is_open_block, validate_maze
from pattern42 import forty_two_cells


class Cell:
    """A grid cell with four reciprocal walls."""

    def __init__(self, x: int, y: int) -> None:
        """Create a cell with all four walls closed."""
        self.x = x
        self.y = y
        self.walls = {"N": True, "E": True, "S": True, "W": True}
        self.visited = False

    def open_path(self, next: "Cell") -> None:
        """Open reciprocal walls between two adjacent cells."""
        if abs(next.x - self.x) + abs(next.y - self.y) != 1:
            raise ValueError("A passage requires orthogonally adjacent cells")
        if next.x - self.x > 0:
            self.walls["E"] = False
            next.walls["W"] = False
        if next.y - self.y > 0:
            self.walls["S"] = False
            next.walls["N"] = False
        if next.x - self.x == -1:
            self.walls["W"] = False
            next.walls["E"] = False
        if next.y - self.y == -1:
            self.walls["N"] = False
            next.walls["S"] = False


class Generator:
    """Generate reproducible perfect mazes or playable boards."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Validate settings and initialize an empty maze."""
        validate_config(config)
        self.width: int = config["width"]
        self.height: int = config["height"]
        self.entry: tuple[int, int] = config["entry"]
        self.exit: tuple[int, int] = config["exit"]
        self.seed: int = config["seed"]
        self.perfect: bool = config["perfect"]
        self.output_file: str = config["output_file"]
        self.grid: list[list[Cell]] = []
        self.pattern_cells: set[tuple[int, int]] = set()
        self.pattern_warning: str | None = None

    def generate_maze(self) -> None:
        """Generate and validate a maze, raising ValueError on failure.

        ``__init__`` already called ``validate_config``, which guarantees
        the requested size, entry/exit and pattern placement are all
        possible, so this method does not need to re-check them.
        """
        rng = random.Random(self.seed)
        forbidden = [self.entry, self.exit]
        if not self.perfect:
            forbidden.append((self.width // 2, self.height // 2))
        pattern = forty_two_cells(self.width, self.height, forbidden)
        self.pattern_cells = pattern if pattern is not None else set()
        self.pattern_warning = (
            "the maze is too small to draw the '42' pattern"
            if pattern is None else None
        )
        # A different tree can avoid dead ends that cannot safely be braided.
        # Keep one RNG across attempts to reproduce the whole process.
        attempts = 1 if self.perfect else 50
        for _ in range(attempts):
            self._generate_tree(rng)
            if not self.perfect:
                self._braid_maze(rng)
            errors = self.validate()
            if not errors:
                return
        raise ValueError(
            f"Could not generate a valid maze after {attempts} attempt(s): "
            + "; ".join(errors)
        )

    def _generate_tree(self, rng: random.Random) -> None:
        """Carve a DFS spanning tree, leaving the pattern cells closed."""
        self.grid = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                cell = Cell(x, y)
                line.append(cell)
            self.grid.append(line)
        for (px, py) in self.pattern_cells:
            self.grid[py][px].visited = True

        start = self.grid[self.entry[1]][self.entry[0]]
        start.visited = True
        self.listcel = [start]
        while (self.listcel):
            neighbours = self.get_neighbours(self.listcel[-1])
            if not neighbours:
                self.listcel.pop()
            else:
                next = rng.choice(neighbours)
                self.listcel[-1].open_path(next)
                next.visited = True
                self.listcel.append(next)

    def _try_open(self, cell: Cell, other: Cell, direction: str,
                  opposite: str) -> bool:
        """Open an internal wall unless it creates an open 3x3 block."""
        cell.open_path(other)
        # Only blocks containing both endpoints can become newly open.
        for y in range(max(0, max(cell.y, other.y) - 2),
                       min(cell.y, other.y, self.height - 3) + 1):
            for x in range(max(0, max(cell.x, other.x) - 2),
                           min(cell.x, other.x, self.width - 3) + 1):
                if is_open_block(self.grid, x, y, 3):
                    cell.walls[direction] = True
                    other.walls[opposite] = True
                    return False
        return True

    def _braid_maze(self, rng: random.Random) -> None:
        """Remove dead ends and create at least two independent cycles."""
        candidates: list[tuple[Cell, Cell, str, str]] = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if (x, y) in self.pattern_cells:
                    continue
                for dx, dy, direction, opposite in (
                    (1, 0, "E", "W"), (0, 1, "S", "N"),
                ):
                    nx, ny = x + dx, y + dy
                    if (nx < self.width and ny < self.height
                            and (nx, ny) not in self.pattern_cells
                            and cell.walls[direction]):
                        candidates.append((cell, self.grid[ny][nx],
                                           direction, opposite))
        rng.shuffle(candidates)
        cells, passages = count_graph(self.grid)
        loops = passages - cells + 1
        # First prioritise walls touching dead ends. Opening a wall only
        # increases degrees, so it never creates new dead ends.
        for cell, other, direction, opposite in candidates:
            if (sum(cell.walls.values()) == 3
                    or sum(other.walls.values()) == 3):
                if self._try_open(cell, other, direction, opposite):
                    loops += 1
        for cell, other, direction, opposite in candidates:
            if loops >= 2:
                break
            if cell.walls[direction]:
                if self._try_open(cell, other, direction, opposite):
                    loops += 1

    def get_neighbours(self, current: Cell) -> list[Cell]:
        """Return unvisited neighbours available for maze generation."""
        neighbourslist = []
        offsets = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in offsets:
            nx = current.x + dx
            ny = current.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbour = self.grid[ny][nx]
                if not neighbour.visited:
                    neighbourslist.append(neighbour)

        return neighbourslist

    def show_maze(self, show_solution: bool = True,
                  wall_color: str = "") -> None:
        """Display ASCII walls and optional dots at solution cell centers."""
        if not self.grid:
            raise ValueError("Generate a maze before displaying it")
        path: set[tuple[int, int]] = set()
        if show_solution:
            solution = bfs(self.grid, self.entry, self.exit)
            for cell in solution:
                path.add((cell.x, cell.y))

        reset = ""
        if wall_color:
            reset = "\033[0m"
        joint = f"{wall_color}+{reset}"
        horizontal = f"{wall_color}---{reset}"
        vertical = f"{wall_color}|{reset}"
        for y in range(self.height):
            top_line = ""
            mid_line = ""
            for x in range(self.width):
                cell = self.grid[y][x]
                top_line += joint
                if cell.walls["N"]:
                    top_line += horizontal
                else:
                    top_line += "   "
                if cell.walls["W"]:
                    mid_line += vertical
                else:
                    mid_line += " "
                if (x, y) == self.entry:
                    mid_line += " E "
                elif (x, y) == self.exit:
                    mid_line += " X "
                elif (x, y) in self.pattern_cells:
                    mid_line += " # "
                elif (x, y) in path:
                    mid_line += " o "
                else:
                    mid_line += "   "
            top_line += joint
            if self.grid[y][self.width - 1].walls["E"]:
                mid_line += vertical
            else:
                mid_line += " "
            print(top_line)
            print(mid_line)

        under_line = ""
        for x in range(self.width):
            cell = self.grid[self.height - 1][x]
            under_line += joint
            if cell.walls["S"]:
                under_line += horizontal
            else:
                under_line += "   "
        under_line += joint
        print(under_line)

    def validate(self) -> list[str]:
        """Check the generated maze against the subject rules.

        Returns:
            A list of error messages. Empty means the maze is valid.
        """
        return validate_maze(
            self.grid, self.entry, self.exit, self.perfect,
            pattern_cells=self.pattern_cells,
        )
