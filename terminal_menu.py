"""Interactive terminal controls for maze generation and display."""

import os
import random
import sys
from typing import Any

from generator import Generator
from maze_exporter import write_maze


COLORS = (
    ("Default", "\033[37m"),
    ("Red", "\033[31m"),
    ("Green", "\033[32m"),
    ("Yellow", "\033[33m"),
    ("Blue", "\033[34m"),
    ("Magenta", "\033[35m"),
    ("Cyan", "\033[36m"),
)


def run_menu(generator: Generator, config: dict[str, Any]) -> None:
    """Run controls until exit, EOF or Ctrl+C, preserving display preferences.

    Regeneration uses a new seed and replaces the displayed generator only
    after successful generation. The input configuration file is not edited.
    ANSI colours are omitted for redirected output and unsupported terminals.
    """
    show_solution = True
    color_index = 0
    use_color = sys.stdout.isatty()
    if os.environ.get("TERM") == "dumb" or "NO_COLOR" in os.environ:
        use_color = False
    redraw = True
    try:
        while True:
            if redraw:
                wall_color = ""
                if use_color:
                    wall_color = COLORS[color_index][1]
                generator.show_maze(
                    show_solution=show_solution,
                    wall_color=wall_color,
                )
                redraw = False
            print("\n=== A-Maze-ing ===")
            print("1. Re-generate a new maze")
            print("2. Show / Hide the shortest path")
            print("3. Rotate the wall colours")
            print("4. Quit")
            choice = input("Choice? (1-4): ").strip()
            if choice == "4":
                break
            if choice == "1":
                seed = random.randint(0, 2**32 - 1)
                if seed == generator.seed:
                    seed = (seed + 1) % (2**32)
                # Keep the original configuration unchanged.
                new_config = config.copy()
                new_config["seed"] = seed
                candidate = Generator(new_config)
                try:
                    candidate.generate_maze()
                    write_maze(candidate.grid, candidate.entry, candidate.exit,
                               candidate.output_file)
                except (ValueError, OSError, MemoryError) as error:
                    message = str(error) or type(error).__name__
                    print(f"Failed to generate maze: {message}",
                          file=sys.stderr)
                    continue
                generator = candidate
                redraw = True
            elif choice == "2":
                show_solution = not show_solution
                redraw = True
            elif choice == "3":
                # Exclude the current colour so every change is visible.
                available_colors = []
                for index in range(len(COLORS)):
                    if index != color_index:
                        available_colors.append(index)
                color_index = random.choice(available_colors)
                if not use_color:
                    print("Colours are unavailable for this terminal output.")
                redraw = True
            else:
                print("Invalid choice. Enter a number from 1 to 4.")
    except (EOFError, KeyboardInterrupt):
        print()
    print("Goodbye!")
