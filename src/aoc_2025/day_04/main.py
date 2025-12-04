from dataclasses import dataclass, field
from pathlib import Path

from aoc_2025.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)

# 8 directions for neighbor checking
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


@dataclass
class BoolGrid:
  """Grid of boolean values with efficient neighbor counting."""

  cells: list[list[bool]]
  width: int = field(init=False)
  height: int = field(init=False)
  prefix: list[list[int]] = field(init=False, repr=False)

  def __post_init__(self) -> None:
    self.height = len(self.cells)
    self.width = len(self.cells[0]) if self.height > 0 else 0

  @classmethod
  def from_data(cls, data: list[str], element: str = "@") -> "BoolGrid":
    """Create a BoolGrid from input data."""
    cells = [[char == element for char in line.strip()] for line in data]
    return cls(cells)


  def build_prefix_sum(self) -> None:
    """Build 2D prefix sum array for efficient range queries."""
    self.prefix = [[0] * (self.width + 1) for _ in range(self.height + 1)]
    for r in range(1, self.height + 1):
      for c in range(1, self.width + 1):
        self.prefix[r][c] = (
          self.prefix[r - 1][c] + self.prefix[r][c - 1] - self.prefix[r - 1][c - 1] + self.cells[r - 1][c - 1]
        )

  def count_neighbors_prefix(self, r: int, c: int) -> int:
    """Count active 8-neighbors using prefix sum (O(1) per query after O(n²) preprocessing)."""
    r1, c1 = max(0, r - 1), max(0, c - 1)
    r2, c2 = min(self.height - 1, r + 1), min(self.width - 1, c + 1)
    total = self.prefix[r2 + 1][c2 + 1] - self.prefix[r2 + 1][c1] - self.prefix[r1][c2 + 1] + self.prefix[r1][c1]
    return total - self.cells[r][c]  # Exclude center cell

  def count_neighbors(self, r: int, c: int) -> int:
    """Count active 8-neighbors by direct iteration (faster for sparse updates)."""
    count = 0
    for dr, dc in DIRECTIONS:
      nr, nc = r + dr, c + dc
      if 0 <= nr < self.height and 0 <= nc < self.width and self.cells[nr][nc]:
        count += 1
    return count


def part_1(data: list[str]) -> int:
  grid = BoolGrid.from_data(data)
  result = sum(
    1
    for r in range(grid.height)  # rows
    for c in range(grid.width)  # columns
    if grid.cells[r][c] and grid.count_neighbors(r, c) < 4
  )
  return result


def part_2(data: list[str]) -> int:
  grid = BoolGrid.from_data(data)
  result = 0

  for _ in range(1000):
    # Find all cells to remove this iteration
    to_remove = [
      (r, c)
      for r in range(grid.height)
      for c in range(grid.width)
      if grid.cells[r][c] and grid.count_neighbors(r, c) < 4
    ]

    if not to_remove:
      break

    # Remove all marked cells
    for r, c in to_remove:
      grid.cells[r][c] = False

    result += len(to_remove)
  else:
    logger.warning("Reached maximum iterations.")

  return result


if __name__ == "__main__":
  filename: str = "input.txt"
  file_path = Path(__file__).parent / filename
  data = simple_txt_parser(file_path)

  logger.info(f"Part 1: {part_1(data)} cells can be accessed.")  # 1491

  logger.info(f"Part 2: {part_2(data)} cells removed.")  # 8722
