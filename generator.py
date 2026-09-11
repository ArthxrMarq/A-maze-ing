import random


class Cell:

    def __init__(self, x: int, y:int) -> None:
        self.x = x
        self.y = y
        self.walls = {"N": True, "E": True, "S": True, "W": True}
        self.visited = False

    def open_path(current : str, next : str) -> None:
        if y == "W":
            self.walls = {"N": True, "E": True, "S": True, "W": False}


class Generator:

    def __init__(self) -> None:
        self.seed = None
        with open("config.txt","r") as file:
            for line in file:
                if line.startswith("SEED="):
                    seed = int(line.split("=")[1])
                    break
        if seed is None:
            seed = random.randint(0 ,2**32 - 1)    



    def generate_maze() ->None:
        seed = random.seed(self.seed)

    
