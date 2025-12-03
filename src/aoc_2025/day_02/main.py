import math
from pathlib import Path

from aoc_2025.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)


def p1(data: str) -> int:
  invalid_ids: list[int] = []  # List to store the valid repeated numbers
  for token in data.split(","):
    start, end = map(int, token.split("-"))
    logger.debug(f"Range: {start} - {end}")
    len_end = len(str(end))
    # Iterate over possible half-lengths h (since full length must be even)
    for h in range(1, (len_end // 2) + 1):
      factor = 10**h + 1  # Factor to generate repeated number: X * (10^h + 1) = int(str(X) + str(X))
      min_X = 10 ** (h - 1)  # Minimum X for h digits (e.g., 1 for h=1, 10 for h=2)
      max_X = 10**h - 1  # Maximum X for h digits (e.g., 9 for h=1, 99 for h=2)
      # Calculate effective min X where num >= start
      min_X_eff = math.ceil(start / factor)
      # Calculate effective max X where num <= end
      max_X_eff = end // factor
      # Iterate over valid X values within bounds
      for X in range(max(min_X, min_X_eff), min(max_X, max_X_eff) + 1):
        num = X * factor
        if start <= num <= end:  # Double-check the range (though should be covered)
          invalid_ids.append(num)
          logger.debug(f"  Found: {num}")

  return sum(invalid_ids)


def p2(data: str) -> int:
  invalid_ids: list[int] = []  # List to store the invalid repeated numbers
  for token in data.split(","):
    start, end = map(int, token.split("-"))
    logger.debug(f"Range: {start} - {end}")
    len_end = len(str(end))
    # Iterate over possible base lengths b
    for b in range(1, len_end + 1):
      # Iterate over repetition counts k >= 2, such that b * k <= len_end
      max_k = len_end // b
      for k in range(2, max_k + 1):
        # Base number: from 10**(b-1) to 10**b - 1 (no leading zero unless b=1)
        min_base = 10 ** (b - 1)
        max_base = 10**b - 1
        for base in range(min_base, max_base + 1):
          base_str = str(base)
          num_str = base_str * k
          num = int(num_str)
          if start <= num <= end and num not in invalid_ids:
            invalid_ids.append(num)
            logger.debug(f"  Found repeated {k} times: {num} (base: {base_str})")

  return sum(invalid_ids)


if __name__ == "__main__":
  filename: str = "input.txt"
  file_path = Path(__file__).parent / filename
  data = simple_txt_parser(file_path)[0]
  logger.info(f"SUM of invalid IDs (p1): {p1(data)}")
  logger.info(f"SUM of invalid IDs (p2): {p2(data)}")
