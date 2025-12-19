# Advent of Code Solutions

Multi-year scaffold for solving Advent of Code challenges with shared utilities.

## Project Structure

```
src/aoc/
├── __init__.py
├── utils/                    # Shared utilities across all years
│   ├── __init__.py
│   ├── parse_txt.py         # File parsing helpers
│   └── structlog.py         # Structured logging setup
│
└── aoc_2025/                # Year-specific solutions
    ├── __init__.py
    ├── day_01/
    │   ├── main.py          # Solution code
    │   ├── input.txt        # Puzzle input
    │   └── example.txt      # Example/test input
    ├── day_02/
    └── ...
```

## Setup

```bash
# Install project in editable mode
uv sync

# Run a specific day solution
uv run python -m aoc.aoc_2025.day_01.main
```

## Adding a New Year

To add solutions for a new year (e.g., 2024):

1. Create year directory: `src/aoc/year_2024/`
2. Create `__init__.py` in it
3. Create day folders: `src/aoc/year_2024/day_01/`, etc.
4. Use the same import pattern for all years

## Solution Template

```python
from aoc.utils import get_logger, simple_txt_parser
from pathlib import Path

logger = get_logger(__name__)

def part_1(data: list[str]) -> int:
    # Solution
    pass

def part_2(data: list[str]) -> int:
    # Solution
    pass

if __name__ == "__main__":
    file_path = Path(__file__).parent / "input.txt"
    data = simple_txt_parser(file_path)
    logger.info(f"Part 1: {part_1(data)}")
    logger.info(f"Part 2: {part_2(data)}")
```

## Shared Utilities

All years share utilities in `src/aoc/utils/`:

- `simple_txt_parser(path, parser=None)` - Parse input files, optionally apply parser function
- `separator_parser(text, separator=",")` - Split strings by separator, strip whitespace
- `get_logger(name)` - Get structured logger instance

Always import with: `from aoc.utils import get_logger, simple_txt_parser`

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager
- Dependencies listed in `pyproject.toml`