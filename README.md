*This project has been created as part of the 42 curriculum by lusampai, armarque.*

# A-Maze-ing

## Description

A Python maze generator with perfect and imperfect modes, a shortest-path
solver, hexadecimal file export and an interactive terminal display.
The maze contains a closed-cell “42” pattern when the configured size allows
it. Borders stay closed, shared walls agree, and all playable cells remain
connected. Open 3×3 areas are forbidden.

The display uses `+`, `---` and `|` for walls, `E` for entry, `X` for exit,
`#` for the pattern and `o` for the solution. No graphical library is needed.

## Instructions

Python 3.10 or later is required. The application itself uses only the
standard library:

```bash
python3 a_maze_ing.py config.txt
```

For development, create and activate an isolated environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
make install
make lint
make run
```

`make install` downloads development tools, so it requires access to a Python
package index. `make debug` starts pdb. `make clean` removes Python and mypy
caches while preserving virtual environments and generated packages.
Use `make run CONFIG=other.txt` for another configuration.

The menu follows the subject:

```text
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit
Choice? (1-4):
```

Option 1 uses a new seed and saves the new maze to `OUTPUT_FILE`. A failed
regeneration or export leaves the previous maze and file available. Option 2
changes only visibility. Option 3 randomly picks a different wall colour,
without a submenu. The solution starts visible. EOF and Ctrl+C leave the
menu. Colour is disabled for redirected output, `TERM=dumb`, or `NO_COLOR`.

## Configuration

Supply exactly one UTF-8 TXT filename as the command-line argument. Each
setting is one `KEY=VALUE` line. Empty lines and lines starting with `#` are
ignored. Keys are uppercase; boolean values are case-insensitive.

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

| Key | Required | Meaning |
| --- | --- | --- |
| `WIDTH` | Yes | Positive number of columns |
| `HEIGHT` | Yes | Positive number of rows |
| `ENTRY` | Yes | Entry as `x,y`, starting at zero |
| `EXIT` | Yes | Exit as `x,y`, different from entry |
| `OUTPUT_FILE` | Yes | Destination path, relative to the working directory |
| `PERFECT` | Yes | `True` for no cycles; `False` for a playable board |
| `SEED` | No | Integer seed; randomly selected when omitted |

Unknown keys, duplicate keys and empty values are rejected. Coordinates must
be inside the grid. `PERFECT` remains mandatory because the subject lists it
as a required key, even though its prose calls imperfect mode the default.
Imperfect mode needs at least 2×3 or 3×2 cells to contain two independent
cycles. The current “42” template needs at least 13×9, including its margin.
Small grids display a warning and omit the pattern. If the pattern cannot
avoid protected entry, exit and center positions, configuration is rejected.
The output must not be the configuration file. Its parent directory must
already exist.

## Algorithms and design choices

Generation starts with iterative depth-first search (DFS), also called
recursive backtracking when implemented recursively. A stack keeps track of
the current branch; a random unvisited neighbour is connected at each step.
This was chosen because the steps are easy to follow and a spanning tree
naturally provides one unique route between any two playable cells. The
iterative form avoids Python recursion depth limits.

In imperfect mode, internal walls are removed to reduce dead ends and create
at least two independent cycles. Openings that create a 3×3 open area are
reverted. The result must have at most two dead ends and accessible center
and corners. If needed, generation retries up to 50 trees using the same
random generator; exhausting retries reports an error. This does not prove
the requested configuration is mathematically impossible.

Breadth-first search (BFS) is implemented separately in `maze_solver.py`.
It uses a queue and predecessor coordinates to find a shortest path in an
unweighted grid. It checks both sides of each shared wall.

## Output format

Each cell becomes one uppercase hexadecimal digit. A closed wall sets its
bit: North=1, East=2, South=4, West=8. Rows are followed by a blank line,
entry coordinates, exit coordinates and the shortest path in `N/E/S/W`.
Every line, including the last, ends with a newline.

For a straight 3×1 maze from `(0,0)` to `(2,0)`:

```text
D57

0,0
2,0
EE
```

Export uses a temporary file in the destination directory, then replaces the
output after the write succeeds. This prevents partial output on an ordinary
write failure. Hiding the displayed path does not remove it from the file.

## Reusable module and build

`Generator` handles generation, while `bfs` and `write_maze` handle solving
and export. These are available from the public `mazegen` module:

```python
from mazegen import Generator, bfs, write_maze

settings = {
    "width": 20, "height": 15,
    "entry": (0, 0), "exit": (19, 14),
    "seed": 42, "perfect": True, "output_file": "maze.txt",
}
maze = Generator(settings)
maze.generate_maze()
print(maze.grid[0][0].walls)
solution = bfs(maze.grid, maze.entry, maze.exit)
write_maze(maze.grid, maze.entry, maze.exit, maze.output_file)
```

Changing the dictionary changes size, seed and mode. `grid[y][x]` provides
cells with `x`, `y` and a `walls` dictionary. BFS returns cells from entry to
exit. The API validates settings and reports `ConfigError`, generation
reports `ValueError`, and export may report `OSError`. Very large grids may
exhaust available memory; callers should also handle `MemoryError`.
Generation through the API does not write files until `write_maze` is called.
The CLI writes the file automatically.

Build the distribution from source after `make install`:

```bash
make build
python3 -m pip install mazegen-1.0.0-py3-none-any.whl
```

The standard Python build frontend uses Poetry Core as its backend. A full
Poetry installation is not required. The wheel is written to the repository
root and includes the reusable modules and this documentation. The package has no runtime dependencies. The MIT license in
[LICENSE.md](LICENSE.md) permits reuse and distribution.

## Team and project management

- **armarque:** maze generation and maze solving.
- **lusampai:** assistance with solving, terminal menu and configuration
  validation.
- **Both:** documentation.

The implementation progressed from core generation and solving to an
external solver, configuration and structural validation, imperfect boards,
interactive controls, export and packaging. The original dated schedule was
not recorded in this repository, so no retrospective deadlines are invented
here. The remaining review work is to rehearse explanations together and
compare exported files with the subject's analyzer when available.

Separating generation, solving, validation and export made changes easier to
test. Regression tests helped catch mismatches between renderer symbols and
test expectations. Improvements include agreeing on display behaviour before
changing it and keeping documentation synchronized with implementation.
Tools used include Python, Git, unittest, mypy, Make, the Python build
frontend and AI-assisted code review. Flake8 and mypy are the required code quality checks.

## Resources

- The supplied A-Maze-ing subject, version 2.3, defines the project rules.
- [Python deque documentation](https://docs.python.org/3/library/collections.html#collections.deque)
  describes the queue used by BFS.
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
  explains distribution builds and package metadata.

AI assistance was used for code review, BFS extraction, explanations of the
pattern code, imperfect generation, menu implementation, export, packaging,
test development and documentation drafts. The team must understand and
review the resulting code and demonstrate it independently at evaluation.
Tests are development aids; the subject says test programs are not submitted
or graded. They are not included in this delivery.

## Verification

Run `make lint` for the required Flake8 and mypy checks. Development tests
were run before preparing the delivery. The subject's `maze_analyzer.py`
is not included in this repository; run it on `OUTPUT_FILE` when available.
