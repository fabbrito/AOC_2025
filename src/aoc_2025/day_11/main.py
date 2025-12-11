from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from aoc_2025.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)


@dataclass
class Device:
  """Represents a device network with connections."""

  mapping: dict[str, list[str]]
  _memo: dict[tuple[str, tuple[str, ...]], int] = field(default_factory=dict)

  @staticmethod
  def from_data(data: list[str]) -> Device:
    """Parses input data into a Device instance."""
    mapping: dict[str, list[str]] = {}
    for line in data:
      tag, raw_conn = line.split(": ")
      mapping[tag] = raw_conn.split(" ")
    return Device(mapping)

  def traverse_mapping(self, current: str, constraint: tuple[str, ...] = ()) -> int:
    """Counts paths from current to 'out' that visit all in constraint."""
    key = (current, constraint)
    if key in self._memo:
      return self._memo[key]
    if current == "out":
      result = int(len(constraint) == 0)
    else:
      if current in constraint:
        constraint = tuple(x for x in constraint if x != current)
      result = sum(self.traverse_mapping(neighbor, constraint) for neighbor in self.mapping.get(current, []))
    self._memo[key] = result
    return result


def part_1(data: list[str]) -> int:
  """Counts the number of paths from 'you' to 'out'."""
  server: Device = Device.from_data(data)
  return server.traverse_mapping("you")


def part_2(data: list[str]) -> int:
  """Counts paths from 'svr' to 'out' that visit both 'dac' and 'fft'."""
  server: Device = Device.from_data(data)
  return server.traverse_mapping("svr", ("dac", "fft"))


if __name__ == "__main__":
  """Main execution block."""
  # Run the solutions for both parts using the input file
  filename: str = "input.txt"
  file_path: Path = Path(__file__).parent / filename
  data: list[str] = simple_txt_parser(file_path)

  logger.info("Starting Day 11 Solutions")
  logger.info(f"Part 1: {part_1(data)}")  # 640
  logger.info(f"Part 2: {part_2(data)}")  # 367579641755680
