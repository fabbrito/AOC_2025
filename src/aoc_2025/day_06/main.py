from __future__ import annotations

from functools import reduce
from pathlib import Path

from aoc_2025.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)

OPERATORS = {"+": lambda x, y: x + y, "-": lambda x, y: x - y, "*": lambda x, y: x * y, "/": lambda x, y: x / y}


def part_1(input: list[str]) -> int:
  # Parse input into a 2D list
  data = [line.strip().split() for line in input]
  result = 0
  rows = len(data)
  cols = len(data[0]) if data else 0

  for j in range(cols):  # Process each column directly
    # Extract values (all rows except last) and operator (last row)
    values = [int(data[i][j]) for i in range(rows - 1)]
    operator = data[-1][j]

    if values:
      # Use reduce for left-associative accumulation
      accumulator = reduce(OPERATORS[operator], values)
      result += accumulator

  return result


def part_2(data: list[str]) -> int:
  if not data:
    return 0

  result = 0
  rows = len(data)
  cols = len(data[0])
  values: list[int] = []

  for j in range(cols - 1, -1, -1):
    all_spaces = True
    values.append(0)  # Start building a new number for this column
    for i in range(rows):
      char = data[i][j]
      if char.isdigit():
        values[-1] = values[-1] * 10 + int(char)
        all_spaces = False
      elif char in OPERATORS:
        logger.debug(f"Processing operator '{char}' with values {values}")
        accumulator = reduce(OPERATORS[char], values)
        logger.debug(f"Intermediate result: {accumulator}")
        result += accumulator
        values = []
        all_spaces = False
      # spaces are ignored during iteration

    # If entire column was spaces, reset values (separator between problems)
    if all_spaces:
      values = []

  return result


if __name__ == "__main__":
  # Run the solutions for both parts using the input file
  filename: str = "input.txt"
  file_path = Path(__file__).parent / filename
  data = simple_txt_parser(file_path)
  # Transpose the data matrix

  logger.info(f"Part 1: {part_1(data)}")
  logger.info(f"Part 2: {part_2(data)}")
