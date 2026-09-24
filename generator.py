import random
from collections import deque
import sys
from typing import Any

from config_parser import ConfigError, read_config
from maze_validator import validate_maze
from pattern42 import forty_two_cells


class Cell:

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.walls = {"N": True, "E": True, "S": True, "W": True}
        self.visited = False

    def open_path(self, next: "Cell") -> None:
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

    # MUDANÇA 1: o Generator recebe o config já pronto, não lê arquivo
    def __init__(self, config: dict[str, Any]) -> None:
        self.width: int = config["width"]
        self.height: int = config["height"]
        self.entry: tuple[int, int] = config["entry"]
        self.exit: tuple[int, int] = config["exit"]
        self.seed: int = config["seed"]
        self.perfect: bool = config["perfect"]
        self.output_file: str = config["output_file"]
        self.pattern_cells: set[tuple[int, int]] = set()
        self.pattern_warning: str | None = None

    def generate_maze(self) -> None:
        random.seed(self.seed)
        self.grid: list[list[Cell]]
        self.grid = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                cell = Cell(x, y)
                line.append(cell)
            self.grid.append(line)
        pattern = forty_two_cells(
            self.width, self.height, forbidden=(self.entry, self.exit)
        )
        if pattern is None:
            self.pattern_cells = set()
            self.pattern_warning = (
                "the maze is too small (or entry/exit is in the way) "
                "to draw the '42' pattern"
            )
        else:
            self.pattern_cells = pattern
            self.pattern_warning = None
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
                next = random.choice(neighbours)
                self.listcel[-1].open_path(next)
                next.visited = True
                self.listcel.append(next)

    def get_neighbours(self, current: Cell) -> list[Cell]:
        neighbourslist = []
        deslocations = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in deslocations:
            nx = current.x + dx
            ny = current.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbour = self.grid[ny][nx]
                if not neighbour.visited:
                    neighbourslist.append(neighbour)

        return neighbourslist

    def show_maze(self) -> None:
        for y in range(self.height):
            top_line = ""
            mid_line = ""
            for x in range(self.width):
                cell = self.grid[y][x]
                top_line += "+"
                if cell.walls["N"]:
                    top_line += "---"
                else:
                    top_line += "   "
                if cell.walls["W"]:
                    mid_line += "|"
                else:
                    mid_line += " "
                if (x, y) == self.entry:
                    mid_line += " E "
                elif (x, y) == self.exit:
                    mid_line += " X "
                elif (x, y) in self.pattern_cells:
                    mid_line += " # "
                else:
                    mid_line += "   "
            top_line += "+"
            if self.grid[y][self.width - 1].walls["E"]:
                mid_line += "|"
            else:
                mid_line += " "
            print(top_line)
            print(mid_line)

        under_line = ""
        for x in range(self.width):
            cell = self.grid[self.height - 1][x]
            under_line += "+"
            if cell.walls["S"]:
                under_line += "---"
            else:
                under_line += "   "
        under_line += "+"
        print(under_line)

    def validate(self) -> list[str]:
        """Check the generated maze against the subject rules.

        Returns:
            A list of error messages. Empty means the maze is valid.
        """
        return validate_maze(
            self.grid, self.entry, self.exit, self.perfect
        )


    def open_border(self, cell: "Cell") -> None:
        if cell.x == 0:
            cell.walls["W"] = False
        elif cell.x == self.width - 1:
            cell.walls["E"] = False
        elif cell.y == 0:
            cell.walls["N"] = False
        elif cell.y == self.height - 1:
            cell.walls["S"] = False

    def get_valid_neighbours(self, current : Cell) -> list[Cell]:
            neighbourslist = []
            deslocations = [(0,-1,"N"), (0,1,"S"), (-1,0,"W"), (1,0,"E")]

            for dx, dy, direction in deslocations:
                nx = current.x + dx
                ny = current.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not current.walls[direction]:
                        neighbourslist.append(self.grid[ny][nx])                        

            return neighbourslist


    def bfs (self) -> list[Cell]:
        current : Cell = self.grid[self.entry[1]][self.entry[0]]
        queue : deque[Cell] = deque()
        visited : set[Cell] = set()
        camefrom : dict[Cell, Cell] = {}
        current_start : Cell = current
        queue.append(current)
        visited.add(current)
        camefrom[current] =  None
        found = False
        while queue:
            current = queue.popleft()
            if(current == self.grid[self.exit[1]][self.exit[0]]):
                found = True
                break
            neighbours = self.get_valid_neighbours(current)
            for neighbour in neighbours:
                if neighbour not in visited:
                    visited.add(neighbour)
                    camefrom[neighbour] = current
                    queue.append(neighbour)
            
        if not found:
            return []

        exit_cell = self.grid[self.exit[1]][self.exit[0]]
        path : list[Cell] = [exit_cell]
        while path[-1] != current_start:
            path.append(camefrom[path[-1]])
        path.reverse()
        return path



def main() -> None:
    # MUDANÇA 3: o main lê o config e trata os erros
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)
    try:
        config = read_config(sys.argv[1])
    except ConfigError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    generator = Generator(config)
    generator.generate_maze()
    if generator.pattern_warning:
        print(f"Warning: {generator.pattern_warning}", file=sys.stderr)
    errors = generator.validate()
    if errors:
        print("Warning: the maze breaks the subject rules:",
              file=sys.stderr)
        for message in errors:
            print(f"  - {message}", file=sys.stderr)
    generator.show_maze()


if __name__ == "__main__":
    main()