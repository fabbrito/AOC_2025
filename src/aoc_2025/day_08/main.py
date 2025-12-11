from __future__ import annotations

from pathlib import Path

import networkx as nx

from aoc_2025.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)


def l2_norm(p1: list[int], p2: list[int]) -> int:
  return sum((a - b) ** 2 for a, b in zip(p1, p2, strict=True))


def part_1(data: list[str], max_iterations: int = 10) -> int:
  points = [list(map(int, line.strip().split(","))) for line in data]
  n = len(points)

  # Pre-compute all pairwise distances as (distance, i, j) tuples
  dists = []
  for i in range(n):
    for j in range(i + 1, n):
      dist = l2_norm(points[i], points[j])
      dists.append((dist, i, j))

  # Sort by distance
  dists.sort()

  # Build graph by adding edges in order of distance
  G = nx.Graph()
  G.add_nodes_from(range(n))

  # If max_iterations is None, add all edges
  for k in range(max_iterations or len(dists)):
    _, i, j = dists[k]
    G.add_edge(i, j)

  # Get connected components as clusters
  cluster_sizes = [len(c) for c in sorted(nx.connected_components(G), key=len, reverse=True)]
  # Multiply the 3 largest cluster sizes
  return cluster_sizes[0] * cluster_sizes[1] * cluster_sizes[2]


def part_2(data: list[str]) -> int:
  points = [list(map(int, line.strip().split(","))) for line in data]
  n = len(points)

  # Pre-compute all pairwise distances as (distance, i, j) tuples
  dists = []
  for i in range(n):
    for j in range(i + 1, n):
      dist = l2_norm(points[i], points[j])
      dists.append((dist, i, j))

  # Sort by distance
  dists.sort()

  # Build graph by adding edges in order of distance until all connected
  G = nx.Graph()
  G.add_nodes_from(range(n))

  last_edge: tuple[int, int] | None = None
  for k in range(len(dists)):
    _, i, j = dists[k]
    G.add_edge(i, j)
    last_edge = (i, j)

    # Check if we have exactly 1 connected component
    if nx.number_connected_components(G) == 1:
      break

  # Extract X coordinates from the last edge added
  if last_edge is None:
    return 0
  i, j = last_edge
  x_i = points[i][0]
  x_j = points[j][0]
  result = x_i * x_j

  return result


if __name__ == "__main__":
  # Run the solutions for both parts using the input file
  filename: str = "input.txt"
  file_path = Path(__file__).parent / filename
  data = simple_txt_parser(file_path)

  logger.info("Starting Day 08 Solutions")
  logger.info(f"Part 1: {part_1(data, max_iterations=1000)}")  # 62186
  logger.info(f"Part 2: {part_2(data)}")  # 8420405530
