import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from aoc_2025.utils import setup_logger, simple_txt_parser

setup_logger()
logger = logging.getLogger(__name__)

ACTION_PATTERN = re.compile(r"^(?P<dir>[RL])(?P<amt>\d+)$", re.IGNORECASE)


@dataclass
class Safe:
  current_position: int = 50
  zeros_at_end: int = 0
  zeros_during: int = 0

  def parse_rotation(self, action: str) -> int:
    match = ACTION_PATTERN.match(action)
    if not match:
      raise ValueError(f"Invalid action: {action}")
    direction = match.group("dir")
    amount = int(match.group("amt"))
    return (1 if direction == "R" else -1) * amount

  def apply_rotation(self, action: str) -> None:
    rotation_delta = self.parse_rotation(action)
    sign = 1 if rotation_delta > 0 else -1
    abs_rotation = abs(rotation_delta)
    start_pos = self.current_position
    first_crossing = (-start_pos * sign) % 100
    if abs_rotation <= 1:
      during_crossings = 0
    else:
      if first_crossing == 0:
        during_crossings = (abs_rotation - 1) // 100
      else:
        if first_crossing <= abs_rotation - 1:
          during_crossings = (abs_rotation - 1 - first_crossing) // 100 + 1
        else:
          during_crossings = 0
    self.zeros_during += during_crossings
    new_position = (self.current_position + rotation_delta) % 100
    if new_position == 0:
      self.zeros_at_end += 1
    logger.debug(
      f"{action} | {self.current_position} {rotation_delta} -> {new_position} | "
      f"during: {during_crossings}, total during: {self.zeros_during}"
    )
    self.current_position = new_position

  def apply_all_rotations(self, actions: List[str]) -> None:
    for action in actions:
      self.apply_rotation(action)


def main(filename: str = "example.txt") -> None:
  lines = simple_txt_parser(Path(__file__).parent / filename)
  safe = Safe()
  safe.apply_all_rotations(lines)
  logger.info(safe)
  logger.info(f"P1: {safe.zeros_at_end}")
  logger.info(f"P2: {safe.zeros_at_end + safe.zeros_during}")


if __name__ == "__main__":
  main("input.txt")
