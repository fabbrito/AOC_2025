from __future__ import annotations

from pathlib import Path

from aoc.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)


def parse_input(data: list[str]) -> tuple[dict[int, set[tuple[int, int]]], list[dict]]:
  """Parse input into shapes and region queries."""
  shapes: dict[int, set[tuple[int, int]]] = {}
  queries: list[dict] = []

  i = 0
  while i < len(data):
    line = data[i].strip()

    if not line:
      i += 1
      continue

    if ":" in line and "x" not in line:
      # Shape definition
      shape_id = int(line.split(":")[0])
      shape_lines = []
      i += 1

      # Read shape lines
      while i < len(data) and data[i].strip() and "x" not in data[i] and ":" not in data[i]:
        shape_lines.append(data[i])
        i += 1

      # Extract cells from shape lines
      shapes[shape_id] = extract_shape_from_lines(shape_lines)

    elif "x" in line:
      # Region query
      parts = line.split(":")
      dims = parts[0].strip().split("x")
      width, height = int(dims[0]), int(dims[1])
      counts = list(map(int, parts[1].strip().split()))

      queries.append({"width": width, "height": height, "counts": counts})
      i += 1
    else:
      i += 1

  return shapes, queries


def extract_shape_from_lines(lines: list[str]) -> set[tuple[int, int]]:
  """Extract cell coordinates from shape lines."""
  cells = set()
  for r, line in enumerate(lines):
    for c, char in enumerate(line):
      if char == "#":
        cells.add((r, c))

  # Normalize
  if cells:
    min_r = min(r for r, c in cells)
    min_c = min(c for r, c in cells)
    return {(r - min_r, c - min_c) for r, c in cells}
  return set()


def can_fit_by_area(width: int, height: int, present_counts: list[int], shape_sizes: dict[int, int]) -> bool | None:
  """
  Quick check if presents can fit based on area alone.
  Returns True if definitely fits, False if definitely doesn't fit, None if uncertain.
  """
  grid_area = width * height
  total_present_cells = sum(present_counts[i] * shape_sizes.get(i, 0) for i in range(len(present_counts)))

  # Obviously impossible - not enough space
  if total_present_cells > grid_area:
    return False

  # Calculate total number of presents
  total_presents = sum(present_counts)

  # Check if even with wasteful packing (3x3 per present), there's room
  # This uses the loose bound: each present needs at most a 3x3 block
  max_3x3_blocks = (width // 3) * (height // 3)

  if total_presents <= max_3x3_blocks:
    return True

  # Uncertain - need actual packing
  return None


def get_all_orientations(cells: set[tuple[int, int]]) -> list[set[tuple[int, int]]]:
  """Generate all unique orientations (rotations and flips).

  Generates up to 8 distinct orientations: 4 rotations and 4 flipped rotations.
  Uses a set to automatically deduplicate identical shapes (e.g., squares only have 1 unique orientation).
  """

  def rotate_90(coords: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """Rotate 90 degrees clockwise: (r,c) -> (c,-r)"""
    return {(c, -r) for r, c in coords}

  def flip_horizontal(coords: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """Flip horizontally: (r,c) -> (r,-c)"""
    return {(r, -c) for r, c in coords}

  def normalize(coords: set[tuple[int, int]]) -> frozenset[tuple[int, int]]:
    """Normalize to canonical form starting at (0, 0)."""
    if not coords:
      return frozenset()
    min_r = min(r for r, c in coords)
    min_c = min(c for r, c in coords)
    return frozenset((r - min_r, c - min_c) for r, c in coords)

  orientations = set()
  current = cells

  # Generate 4 rotations
  for _ in range(4):
    orientations.add(normalize(current))
    current = rotate_90(current)

  # Generate 4 more rotations from the flipped version
  current = flip_horizontal(cells)
  for _ in range(4):
    orientations.add(normalize(current))
    current = rotate_90(current)

  return [set(o) for o in orientations]


def can_place(grid: list[list[bool]], cells: set[tuple[int, int]], row: int, col: int, width: int, height: int) -> bool:
  """Check if shape can be placed at (row, col)."""
  for r, c in cells:
    nr, nc = row + r, col + c
    if nr < 0 or nr >= height or nc < 0 or nc >= width:
      return False
    if grid[nr][nc]:
      return False
  return True


def place(grid: list[list[bool]], cells: set[tuple[int, int]], row: int, col: int, mark: bool) -> None:
  """Place or remove shape on grid."""
  for r, c in cells:
    grid[row + r][col + c] = mark


def solve_region_backtrack(
  width: int, height: int, present_counts: list[int], all_orientations: dict[int, list[set[tuple[int, int]]]]
) -> bool:
  """Try to fit all presents into the region using backtracking (only for borderline cases).

  Key optimizations:
  - Adjacent-only placement: only try positions adjacent to already-placed shapes (not entire grid)
  - Memoization: cache grid states to avoid redundant exploration
  - Cell counting: prune branches if not enough cells remain for remaining presents
  """
  grid = [[False] * width for _ in range(height)]

  # Build flat list of all presents to place in order
  presents = []
  for shape_id, count in enumerate(present_counts):
    for _ in range(count):
      presents.append(shape_id)

  # Memoization cache: maps (grid_state, present_index) -> bool
  memo: dict[tuple, bool] = {}

  def get_grid_state() -> tuple:
    """Get hashable grid state for memoization."""
    return tuple(tuple(row) for row in grid)

  def count_empty_cells() -> int:
    """Count empty cells in the grid."""
    return sum(1 for row in grid for cell in row if not cell)

  def get_adjacent_positions() -> set[tuple[int, int]]:
    """Get all positions adjacent to filled cells. This is the key optimization.

    Instead of trying all height*width positions, we only try positions that are adjacent
    to already-placed shapes. This drastically reduces the search space.

    For the first present, returns the first empty cell.
    """
    adjacent = set()
    has_placed = False
    for row in range(height):
      for col in range(width):
        if grid[row][col]:
          has_placed = True
          # Add all 4-connected neighbors of this filled cell
          for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < height and 0 <= nc < width and not grid[nr][nc]:
              adjacent.add((nr, nc))

    # If nothing placed yet, return first empty cell to start placement
    if not has_placed:
      for row in range(height):
        for col in range(width):
          if not grid[row][col]:
            return {(row, col)}

    return adjacent

  def backtrack(idx: int) -> bool:
    """Recursively try to place all remaining presents."""
    if idx == len(presents):
      # Successfully placed all presents
      return True

    # Check if this state was already explored
    state = (get_grid_state(), idx)
    if state in memo:
      return memo[state]

    # Pruning: if we need more cells than available, it's impossible
    remaining_presents = len(presents) - idx
    if remaining_presents > count_empty_cells():
      memo[state] = False
      return False

    shape_id = presents[idx]
    adjacent_positions = get_adjacent_positions()

    # Try all orientations of the current shape
    for orientation in all_orientations[shape_id]:
      # Try only adjacent positions (key optimization)
      for row, col in adjacent_positions:
        if can_place(grid, orientation, row, col, width, height):
          # Place the shape
          place(grid, orientation, row, col, True)
          # Recursively try to place remaining presents
          if backtrack(idx + 1):
            memo[state] = True
            return True
          # Backtrack: remove the shape
          place(grid, orientation, row, col, False)

    # No valid placement found for this present
    memo[state] = False
    return False

  return backtrack(0)


def part_1(shapes: dict[int, set[tuple[int, int]]], queries: list[dict]) -> int:
  """Count how many regions can fit all their presents.

  Two-tier strategy:
  1. Fast heuristic checks (area-based) eliminate most cases
  2. Expensive backtracking only for borderline cases
  """
  # Precompute shape sizes for quick checking
  shape_sizes: dict[int, int] = {shape_id: len(cells) for shape_id, cells in shapes.items()}

  # Lazy-load orientations only if backtracking is needed
  all_orientations: dict[int, list[set[tuple[int, int]]]] | None = None

  count = 0
  for query in queries:
    width = query["width"]
    height = query["height"]
    present_counts = query["counts"]

    # Tier 1: Try quick area-based checks first (O(1))
    can_fit = can_fit_by_area(width, height, present_counts, shape_sizes)

    if can_fit is True:
      # Definitely fits based on loose packing estimate
      count += 1
      logger.debug(f"Region {width}x{height}: definitely fits (loose packing)")
    elif can_fit is False:
      # Definitely doesn't fit due to insufficient area
      logger.debug(f"Region {width}x{height}: definitely doesn't fit (area)")
    else:
      # Tier 2: Borderline case requires expensive backtracking
      logger.debug(f"Region {width}x{height}: uncertain, trying backtracking")

      # Lazy initialization: only generate orientations if we actually need backtracking
      if all_orientations is None:
        all_orientations = {}
        for shape_id, cells in shapes.items():
          all_orientations[shape_id] = get_all_orientations(cells)

      if solve_region_backtrack(width, height, present_counts, all_orientations):
        count += 1
        logger.debug(f"Region {width}x{height}: fits (via backtracking)")
      else:
        logger.debug(f"Region {width}x{height}: doesn't fit (via backtracking)")

  return count


if __name__ == "__main__":
  filename: str = "input.txt"
  file_path: Path = Path(__file__).parent / filename
  data: list[str] = simple_txt_parser(file_path)
  shapes, queries = parse_input(data)

  logger.info("Starting Day 12 Solutions")
  logger.info(f"Part 1: {part_1(shapes, queries)}")  # 526
  logger.info("Part 2: Last day does not have a part 2!")
