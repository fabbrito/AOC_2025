from __future__ import annotations

from itertools import combinations_with_replacement
from pathlib import Path

from aoc.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)

type Coords = tuple[int, int]


def area_rectangle(p0: Coords, p1: Coords) -> int:
  """Return the area of the axis-aligned rectangle defined by points p0 and p1."""
  dr = abs(p1[0] - p0[0])
  dc = abs(p1[1] - p0[1])
  return (dr + 1) * (dc + 1)


def parse_coords(raw: list[str]) -> list[Coords]:
  """Convert raw lines (like "r,c") into a list of coordinate tuples."""
  coords: list[Coords] = []
  for line in raw:
    line = line.strip()
    if not line:
      continue
    c, r = map(int, line.split(","))
    coords.append((r, c))
  return coords


def max_rectangle_area(coords: list[Coords]) -> tuple[int, Coords, Coords]:
  """Return the maximum rectangle area and the pair of points that yield it."""
  best_area = -1
  best_pair: tuple[Coords, Coords] = ((0, 0), (0, 0))

  for p0, p1 in combinations_with_replacement(coords, 2):
    a = area_rectangle(p0, p1)
    if a > best_area:
      best_area = a
      best_pair = (p0, p1)

  return best_area, best_pair[0], best_pair[1]


def part_1(raw: list[str]) -> int:
  coords = parse_coords(raw)
  area, p0, p1 = max_rectangle_area(coords)
  logger.debug(f"Max rectangle area found: {area} between points {p0} and {p1}")
  return area


def part_2(raw: list[str]) -> int:
  vertices = parse_coords(raw)
  n = len(vertices)
  # The vertices are given in order around the polygon. We generate the edges by connecting
  # each vertex to the previous one (with wrap-around for the first vertex). Each edge is
  # sorted to ensure consistent (min, max) ordering.
  edges = [sorted([vertices[i], vertices[i - 1]]) for i in range(n)]

  areas: list[tuple[int, Coords, Coords]] = []
  for p0, p1 in combinations_with_replacement(vertices, 2):
    area = area_rectangle(p0, p1)
    v0, v1 = sorted([p0, p1])
    areas.append((area, v0, v1))

  # Sort edges by area descending for efficient lookup
  edges.sort(reverse=True, key=lambda edge: area_rectangle(edge[0], edge[1]))
  areas.sort(reverse=True)
  for area, (r0, c0), (r1, c1) in areas:
    logger.debug(f"Rectangle size {area} between points ({r0}, {c0}) and ({r1}, {c1})")
    # Sort the column coordinates to ensure c0 <= c1, which normalizes the rectangle's orientation
    # without changing its area or validity, allowing consistent edge intersection checks
    c0, c1 = sorted((c0, c1))
    if not any((r3 > r0 and r2 < r1 and c3 > c0 and c2 < c1) for (r2, c2), (r3, c3) in edges):
      logger.debug(f"Found valid rectangle of size {area} between points ({r0}, {c0}) and ({r1}, {c1})")
      return area
    logger.debug(
      f"Rectangle of size {area} between points ({r0}, {c0}) and ({r1}, {c1}) is invalid due to edge intersection"
    )
  raise ValueError("No valid rectangle found")


if __name__ == "__main__":
  # Run the solutions for both parts using the input file
  filename: str = "example.txt"
  file_path = Path(__file__).parent / filename
  data = simple_txt_parser(file_path)

  logger.info("Starting Day 09 Solutions")
  logger.info(f"Part 1: {part_1(data)}")  # 4777824480
  logger.info(f"Part 2: {part_2(data)}")  # 1542119040
