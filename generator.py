import random
<<<<<<< HEAD
from collections import deque
=======
import sys
from typing import Any

from config_parser import ConfigError, read_config

>>>>>>> refs/remotes/origin/main

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
        self.listcel = [self.grid[0][0]]
        while (self.listcel):
            neighbours = self.get_neighbours(self.listcel[-1])
            if not neighbours:
                self.listcel.pop()
            else:
                next = random.choice(neighbours)
                self.listcel[-1].open_path(next)
                next.visited = True
                self.listcel.append(next)
        self.open_border(self.grid[self.entry[1]][self.entry[0]])
        self.open_border(self.grid[self.exit[1]][self.exit[0]])

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

    def open_border(self, cell: "Cell") -> None:
        if cell.x == 0:
            cell.walls["W"] = False
        elif cell.x == self.width - 1:
            cell.walls["E"] = False
        elif cell.y == 0:
            cell.walls["N"] = False
        elif cell.y == self.height - 1:
            cell.walls["S"] = False

<<<<<<< HEAD
    def get_valid_neighbours(self, current : Cell) -> list[Cell]:
            neighbourslist = []
            deslocations = [(0,-1,"N"), (0,1,"S"), (-1,0,"E"), (1,0,"W")]

            for dx, dy, directions in deslocations:
                nx = current.x + dx
                ny = current.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if directions.walls:
                    
                    neighbour = self.grid[ny][nx]
                        neighbourslist.append(neighbour)

            return neighbourslist


    def bfs () ->:
        current : Cell = self.entry
        queue : list[Cell] = {}
        visited : set
        while current != self.exit:
            
            current.visited = True



def read_config (config : str) -> configs : dict[str,int] :
     configs : dict[str,int] = []
     with open(config".txt","r") as file:
            for line in file:
                if line.startswith("WIDTH="):
                    self.width = int(line.split("=")[1])
                    configs["width"] = int(line.split("=")[1]) ## exemplo muito provavelmente vai ficar assim
                if line.startswith("HEIGHT="):
                    self.height = int(line.split("=")[1])
                if line.startswith("ENTRY="):
                    coords = line.split("=")[1].split(",")
                    entry_x = int(coords[0])
                    entry_y = int(coords[1])
                    self.entry = (entry_x, entry_y)
                if line.startswith("EXIT="):
                    coords = line.split("=")[1].split(",")
                    exit_x = int(coords[0])
                    exit_y = int(coords[1])
                    self.exit = (exit_x, exit_y)
                if line.startswith("SEED="):
                    self.seed = int(line.split("=")[1])
        if self.width <= 0 or self.height <= 0 or self.entry is None or self.exit is None:
            raise ValueError("Tamanho inválido")
        if configs["entry"] == configs["exit"]:
            raise ValueError("Entry and exit cant be in the same place!")
        if self.seed is None:
            self.seed = random.randint(0 ,2**32 - 1)

=======
    # MUDANÇA 2: o read_config foi REMOVIDO daqui (agora está no
    # config_parser.py)

>>>>>>> refs/remotes/origin/main

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
    generator.show_maze()


if __name__ == "__main__":
    main()
