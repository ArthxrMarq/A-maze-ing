import random


class Cell:

    def __init__(self, x: int, y:int) -> None:
        self.x = x
        self.y = y
        self.walls = {"N": True, "E": True, "S": True, "W": True}
        self.visited = False


    def open_path(self, next : "Cell") -> None:
        if next.x - self.x > 0 :
            self.walls["E"] = False 
            next.walls["W"] =  False
        if next.y - self.y > 0:
            self.walls["S"] = False
            next.walls["N"] = False
        if next.x - self.x == -1:
            self.walls["W"] = False 
            next.walls["E"] =  False
        if next.y - self.y == -1:
            self.walls["N"] = False 
            next.walls["S"] =  False


class Generator:

    def __init__(self) -> None:
        self.seed = None
        self.width = None
        self.height = None
        with open("config.txt","r") as file:
            for line in file:
                if line.startswith("WIDTH="):
                    self.width = int(line.split("=")[1])
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
        if self.seed is None:
            self.seed = random.randint(0 ,2**32 - 1)
        

    def generate_maze(self) ->None:
        random.seed(self.seed)
        self.grid : [list[list[Cell]]]
        self.grid = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                cell = Cell(x,y)
                line.append(cell)
            self.grid.append(line)            
        self.listcel = [self.grid[0][0]] 
        while(self.listcel):
            neighbours = self.get_neighbours(self.listcel[-1])
            if not neighbours :
                self.listcel.pop()
            else:
                next = random.choice(neighbours)
                self.listcel[-1].open_path(next)
                next.visited = True
                self.listcel.append(next)
        self.open_border(self.grid[self.entry[1]][self.entry[0]])
        self.open_border(self.grid[self.exit[1]][self.exit[0]])


    def get_neighbours(self, current : Cell) -> list[Cell]:
            neighbourslist = []
            deslocations = [(0,-1), (0,1), (-1,0), (1,0)]
            for dx, dy in deslocations:
                nx = current.x + dx
                ny = current.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbour = self.grid[ny][nx]
                    if neighbour.visited == False:
                        neighbourslist.append(neighbour)

            return neighbourslist

    def show_maze(self) -> None:
        self.grid

        for y in range(self.height):
            top_line = ""
            mid_line = ""
            for x in range(self.width):
                cell = self.grid[y][x]
                top_line += "+"
                if cell.walls["N"] == True: 
                    top_line += "---"
                else:
                    top_line += "   "
                if cell.walls["W"] == True:
                    mid_line += "|"
                else:
                    mid_line += " "
                if (x,y) == self.entry:
                    mid_line += " E "
                elif (x,y) == self.exit:
                    mid_line += " X "
                else: 
                    mid_line += "   "
            top_line += "+"
            if self.grid[y][self.width - 1].walls["E"] == True:
                mid_line += "|"
            else:
                mid_line += " "
            print(top_line)
            print(mid_line)

        under_line = ""
        for x in range(self.width):
            cell = self.grid[self.height-1][x]
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


if __name__ == "__main__":
    gen = Generator()
    gen.generate_maze()

    for y in range(gen.height):
        for x in range(gen.width):
            cell = gen.grid[y][x]
            print(f"({x},{y}) -> {cell.walls}")