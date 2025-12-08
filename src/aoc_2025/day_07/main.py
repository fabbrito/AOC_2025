from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from aoc_2025.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)

"""Light utility for computing split paths on a simple grid map."""

DIRECTIONS = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}

type Coords = tuple[int, int]


@dataclass
class Grid:
  """Simple 2D grid container for path/split calculations."""

  width: int
  height: int
  cells: list[str]

  @classmethod
  def from_data(cls, data: list[str]) -> Grid:
    """Create a Grid instance from a list of string rows."""
    height = len(data)
    width = len(data[0]) if height > 0 else 0
    return cls(width=width, height=height, cells=data)

  def __str__(self) -> str:
    """Return a printable representation of the grid."""
    return "\n".join(self.cells)

  def is_in_bounds(self, x: int, y: int) -> bool:
    """Return True if the (row=x, col=y) coordinates are inside the grid."""
    return 0 <= x < self.height and 0 <= y < self.width

  def get_start_position(self) -> Coords:
    """Find and return the first cell marked 'S' as (row, col)."""
    for r in range(self.height):
      for c in range(self.width):
        if self.cells[r][c] == "S":
          return (r, c)
    raise ValueError("Start position 'S' not found in grid.")

  def compute_splits(
    self,
    r0: int,
    c0: int,
    direction: Literal["N", "E", "S", "W"],
    visited: set[Coords],
  ) -> int:
    """Recursively count splittings from position (r0, c0) in a direction.

    The function treats r0/c0 as (row, col) coordinates. It will stop when a
    position is out of bounds or already visited. When a branching marker '^'
    is found it counts a split and explores both side branches.
    """
    # Stop if current position is out of bounds or already visited
    if not self.is_in_bounds(r0, c0) or (r0, c0) in visited:
      return 0

    visited.add((r0, c0))

    # Move one step in the requested direction
    delta_r, delta_c = DIRECTIONS[direction]
    r, c = r0 + delta_r, c0 + delta_c

    # If the next location is out of bounds we cannot continue
    if not self.is_in_bounds(r, c):
      return 0

    # '^' represents a fork: count it (1) and explore both side branches
    if self.cells[r][c] == "^":
      return 1 + self.compute_splits(r, c - 1, direction, visited) + self.compute_splits(r, c + 1, direction, visited)

    # Otherwise continue walking in the same direction
    return self.compute_splits(r, c, direction, visited)

  def compute_paths_rec(
    self,
    r0: int,
    c0: int,
    direction: Literal["N", "E", "S", "W"],
    visited: dict[Coords, int],
  ) -> int:
    """Recursively count the number of paths from (r0, c0) moving in the given direction.

    Uses memoization to cache path counts for each cell. A path ends when the next
    move would be out of bounds. At a '^' split, sums paths from both side branches.
    """
    # Base case: out of bounds
    if not self.is_in_bounds(r0, c0):
      return 0

    # Return cached result if already computed
    if (r0, c0) in visited:
      return visited[(r0, c0)]

    # Calculate next position in the direction
    delta_r, delta_c = DIRECTIONS[direction]
    r, c = r0 + delta_r, c0 + delta_c

    # If next position is out of bounds, this is a valid end of path
    if not self.is_in_bounds(r, c):
      paths = 1
    # At a split '^', sum paths from left and right branches
    elif self.cells[r][c] == "^":
      left_paths = self.compute_paths_rec(r, c - 1, direction, visited)
      right_paths = self.compute_paths_rec(r, c + 1, direction, visited)
      paths = left_paths + right_paths
    # Otherwise, continue straight in the same direction
    else:
      paths = self.compute_paths_rec(r, c, direction, visited)

    # Cache the result and return
    visited[(r0, c0)] = paths
    return paths

  def compute_paths_dp(self, r0: int, c0: int, visited: list[list[int]] | None = None) -> int:
    """Iteratively count the number of paths from (r0, c0) moving SOUTH.

    Uses dynamic programming to compute path counts from bottom to top, caching in visited.
    A path ends when the next move would be out of bounds. At a '^' split, sums paths from both side branches.
    """
    if visited is None:
      visited = [[0 for _ in range(self.width)] for _ in range(self.height)]

    # Compute paths for all cells from bottom to top
    for r in range(self.height - 1, -1, -1):
      for c in range(self.width):
        delta_r, delta_c = DIRECTIONS["S"]
        next_r, next_c = r + delta_r, c + delta_c

        if not self.is_in_bounds(next_r, next_c):
          # End of path
          paths = 1
        elif self.cells[next_r][next_c] == "^":
          # Split: sum paths from left and right branches
          left = (next_r, next_c - 1)
          right = (next_r, next_c + 1)
          paths = visited[left[0]][left[1]] + visited[right[0]][right[1]]
        else:
          # Continue straight
          paths = visited[next_r][next_c]

        visited[r][c] = paths

    return visited[r0][c0]


def part_1(data: list[str]) -> int:
  grid = Grid.from_data(data)
  start = grid.get_start_position()
  visited = set()
  splits = grid.compute_splits(start[0], start[1], "S", visited)
  return splits


def part_2(data: list[str]) -> int:
  grid = Grid.from_data(data)
  start = grid.get_start_position()
  # visited: dict[Coords, int] = {}
  # paths = grid.compute_paths_rec(start[0], start[1], "S", visited)
  visited = [[0 for _ in range(grid.width)] for _ in range(grid.height)]
  paths = grid.compute_paths_dp(start[0], start[1], visited)
  return paths


if __name__ == "__main__":
  # Run the solutions for both parts using the input file
  filename: str = "input.txt"
  file_path = Path(__file__).parent / filename
  data = simple_txt_parser(file_path, lambda x: x.strip())

  logger.info(f"Part 1: {part_1(data)}")  # 1594
  logger.info(f"Part 2: {part_2(data)}")  # 15650261281478
