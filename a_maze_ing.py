"""Command-line entry point required by the A-Maze-ing subject.

This script is the application layer: it wires together the reusable
``mazegen`` classes (config parsing, generation, export, display) into the
CLI described by the subject. It is intentionally kept out of the
``mazegen`` pip package, since a future project reusing the generator has
no use for this project's own launcher or its interactive terminal menu.
"""

import sys

from config_parser import ConfigError, read_config
from generator import Generator
from maze_exporter import write_maze
from terminal_menu import run_menu


def main() -> None:
    """Read the configuration and launch the interactive terminal menu."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)
    try:
        config = read_config(sys.argv[1])
    except ConfigError as error:
        print(f"Error: {error or type(error).__name__}", file=sys.stderr)
        sys.exit(1)
    generator = Generator(config)
    try:
        generator.generate_maze()
        write_maze(generator.grid, generator.entry, generator.exit,
                   generator.output_file)
    except (ValueError, OSError, MemoryError) as error:
        print(f"Error: {error or type(error).__name__}", file=sys.stderr)
        sys.exit(1)
    if generator.pattern_warning:
        print(f"Warning: {generator.pattern_warning}", file=sys.stderr)
    errors = generator.validate()
    if errors:
        print("Warning: the maze breaks the subject rules:",
              file=sys.stderr)
        for message in errors:
            print(f"  - {message}", file=sys.stderr)
    try:
        run_menu(generator, config)
    except OSError as error:
        print(f"Terminal error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
