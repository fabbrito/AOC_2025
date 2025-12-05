from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict

from aoc_2025.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)


type Range = tuple[int, int]


@dataclass
class KMS:
  """Represents the Key Management System with fresh ranges and inventory items."""
  fresh_ranges: list[Range]
  inventory: list[int]

  @classmethod
  def from_data(cls, data: list[str]) -> KMS:
    """Parse the input data into fresh ranges and inventory, optimizing ranges."""
    split_idx = cls._find_split_index(data)
    range_lines = data[:split_idx]
    inventory_lines = data[split_idx + 1 :]
    fresh_ranges = cls._parse_ranges(range_lines)
    fresh_ranges = cls._optimize_ranges_without_overlap(fresh_ranges)
    inventory = cls._parse_inventory(inventory_lines)
    return cls(fresh_ranges=fresh_ranges, inventory=inventory)

  @staticmethod
  def _find_split_index(data: list[str]) -> int:
    """Find the index of the empty line separating ranges from inventory."""
    try:
      return next(i for i, line in enumerate(data) if line.strip() == "")
    except StopIteration:
      return len(data)

  @staticmethod
  def _parse_ranges(lines: list[str]) -> list[Range]:
    """Parse lines into list of (start, end) ranges."""
    result = []
    for line in lines:
      stripped = line.strip()
      if stripped:
        parts = stripped.split("-")
        if len(parts) == 2:
          start, end = map(int, parts)
          result.append((start, end))
    return result

  @staticmethod
  def _parse_inventory(lines: list[str]) -> list[int]:
    """Parse lines into list of inventory item IDs."""
    return [int(line.strip()) for line in lines if line.strip()]

  @staticmethod
  def _optimize_ranges_without_overlap(ranges: list[Range]) -> list[Range]:
    """Merge overlapping or adjacent ranges to optimize the list."""
    if not ranges:
      return []
    sorted_ranges = sorted(ranges, key=lambda r: r[0])
    optimized = [sorted_ranges[0]]
    for current in sorted_ranges[1:]:
      last = optimized[-1]
      if current[0] <= last[1] + 1:  # Overlap or adjacent
        optimized[-1] = (last[0], max(last[1], current[1]))
      else:
        optimized.append(current)
    return optimized


def part_1(data: list[str]) -> int:
  """Count how many inventory items fall within any fresh range."""
  kms = KMS.from_data(data)
  count_fresh = 0
  for item in kms.inventory:
    for start, end in kms.fresh_ranges:
      if start <= item <= end:
        count_fresh += 1
        break
  return count_fresh


def part_2(data: list[str]) -> int:
  """Calculate the total number of fresh items by summing range lengths."""
  kms = KMS.from_data(data)
  total_fresh = 0
  for start, end in kms.fresh_ranges:
    total_fresh += end - start + 1
  return total_fresh


if __name__ == "__main__":
  # Run the solutions for both parts using the input file
  filename: str = "input.txt"
  file_path = Path(__file__).parent / filename
  data = simple_txt_parser(file_path)
  logger.info(f"Part 1: {part_1(data)} items are fresh.")  # 567
  logger.info(f"Part 2: {part_2(data)} total fresh items.")  # 354149806372909
