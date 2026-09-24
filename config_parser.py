"""Configuration file parsing for A-Maze-ing."""

import random
from typing import Any

MANDATORY_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")
OPTIONAL_KEYS = ("SEED",)


class ConfigError(Exception):
    """Raised when the configuration file is missing or invalid."""


def parse_int(key: str, value: str) -> int:
    """Convert a string to an integer.

    Args:
        key: Name of the config key (used in error messages).
        value: Raw string value.

    Returns:
        The integer value.

    Raises:
        ConfigError: If the value is not a valid integer.
    """
    try:
        return int(value)
    except ValueError:
        raise ConfigError(
            f"{key} must be an integer, got '{value}'"
        ) from None


def parse_coords(key: str, value: str) -> tuple[int, int]:
    """Convert a 'x,y' string to a (x, y) tuple.

    Args:
        key: Name of the config key (used in error messages).
        value: Raw string value, e.g. '0,0'.

    Returns:
        A tuple (x, y).

    Raises:
        ConfigError: If the format is not 'x,y' with two integers.
    """
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key} must have the format x,y, got '{value}'")
    return (parse_int(key, parts[0].strip()), parse_int(key, parts[1].strip()))


def parse_bool(key: str, value: str) -> bool:
    """Convert 'True' or 'False' (case-insensitive) to a bool.

    Args:
        key: Name of the config key (used in error messages).
        value: Raw string value.

    Returns:
        The boolean value.

    Raises:
        ConfigError: If the value is neither True nor False.
    """
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ConfigError(f"{key} must be True or False, got '{value}'")


def read_raw_config(path: str) -> dict[str, str]:
    """Read KEY=VALUE pairs from a file, without interpreting the values.

    Empty lines and lines starting with '#' are ignored.

    Args:
        path: Path to the configuration file.

    Returns:
        A dict mapping each key to its raw string value.

    Raises:
        ConfigError: If the file cannot be read or a line is malformed.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        raise ConfigError(f"Config file '{path}' not found") from None
    except IsADirectoryError:
        raise ConfigError(f"'{path}' is a directory, not a file") from None
    except PermissionError:
        raise ConfigError(f"No permission to read '{path}'") from None
    except UnicodeDecodeError:
        raise ConfigError(f"'{path}' is not a valid text file") from None
    except OSError as error:
        raise ConfigError(f"Cannot read '{path}': {error}") from None

    raw: dict[str, str] = {}
    for number, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(
                f"Line {number}: expected KEY=VALUE, got '{line}'"
            )
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key not in MANDATORY_KEYS and key not in OPTIONAL_KEYS:
            raise ConfigError(f"Line {number}: unknown key '{key}'")
        if not value:
            raise ConfigError(f"Line {number}: {key} has no value")
        if key in raw:
            raise ConfigError(f"Line {number}: duplicated key '{key}'")
        raw[key] = value
    return raw


def read_config(path: str) -> dict[str, Any]:
    """Read, parse and validate the maze configuration file.

    Args:
        path: Path to the configuration file (e.g. 'config.txt').

    Returns:
        A dict with the keys 'width' (int), 'height' (int),
        'entry' (tuple[int, int]), 'exit' (tuple[int, int]),
        'output_file' (str), 'perfect' (bool) and 'seed' (int).
        If no SEED is given, a random one is generated.

    Raises:
        ConfigError: If the file is missing, malformed, or if the
            parameters are impossible (bad size, entry == exit, etc.).
    """
    raw = read_raw_config(path)

    missing = [key for key in MANDATORY_KEYS if key not in raw]
    if missing:
        raise ConfigError(f"Missing mandatory key(s): {', '.join(missing)}")

    width = parse_int("WIDTH", raw["WIDTH"])
    height = parse_int("HEIGHT", raw["HEIGHT"])
    if width <= 0 or height <= 0:
        raise ConfigError("WIDTH and HEIGHT must be positive integers")

    entry = parse_coords("ENTRY", raw["ENTRY"])
    exit_ = parse_coords("EXIT", raw["EXIT"])
    for name, (x, y) in (("ENTRY", entry), ("EXIT", exit_)):
        if not (0 <= x < width and 0 <= y < height):
            raise ConfigError(
                f"{name} ({x},{y}) is outside the maze "
                f"(x: 0-{width - 1}, y: 0-{height - 1})"
            )
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")

    if "SEED" in raw:
        seed = parse_int("SEED", raw["SEED"])
    else:
        seed = random.randint(0, 2**32 - 1)

    return {
        "width": width,
        "height": height,
        "entry": entry,
        "exit": exit_,
        "output_file": raw["OUTPUT_FILE"],
        "perfect": parse_bool("PERFECT", raw["PERFECT"]),
        "seed": seed,
    }