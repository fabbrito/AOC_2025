from pathlib import Path

from aoc.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)


def find_max_voltage(bank: list[int], n_digits: int) -> int:
  """Find the maximum n-digit voltage from a bank of batteries.

  A voltage is formed by concatenating n charge levels where each subsequent
  digit must appear at a later position than the previous one.
  """
  # Track all positions where each digit (0-9) appears, sorted
  positions: list[list[int]] = [[] for _ in range(10)]
  for j, battery in enumerate(bank):
    positions[battery].append(j)

  logger.debug(f"Positions: {positions}")

  def find_max_recursive(digits_remaining: int, min_pos: int) -> list[int]:
    """Recursively find the max voltage digits starting from min_pos."""
    if digits_remaining == 0:
      return []

    # Try digits from 9 down to 0 (greedy for max value)
    for digit in range(9, -1, -1):
      # Find the first position >= min_pos using binary search
      digit_positions = positions[digit]
      if not digit_positions:
        continue

      # Binary search for first position > min_pos
      left, right = 0, len(digit_positions)
      while left < right:
        mid = (left + right) // 2
        if digit_positions[mid] <= min_pos:
          left = mid + 1
        else:
          right = mid

      if left < len(digit_positions):
        next_pos = digit_positions[left]
        # Recursively find remaining digits
        rest = find_max_recursive(digits_remaining - 1, next_pos)
        if rest is not None and len(rest) == digits_remaining - 1:
          return [digit] + rest

    return []

  digits = find_max_recursive(n_digits, -1)

  if len(digits) == n_digits:
    voltage = int("".join(map(str, digits)))
    logger.debug(f"Max {n_digits}-digit voltage: {voltage}")
    return voltage
  return -1


def solve(banks: list[list[int]], n_digits: int) -> int:
  voltages: list[int] = []
  for i, bank in enumerate(banks):
    logger.debug(f"Processing bank {i}: {bank}")
    max_voltage = find_max_voltage(bank, n_digits)
    logger.info(f"Bank {i}: Max Voltage = {max_voltage}")
    voltages.append(max_voltage)
  logger.debug(f"Voltages: {voltages}")
  return sum(voltages)


def p2(data: list[list[int]]) -> int:
  return 0


if __name__ == "__main__":
  filename: str = "example.txt"
  file_path = Path(__file__).parent / filename
  data = simple_txt_parser(file_path, lambda x: [int(i) for i in x])

  logger.info(f"SUM of 2 digit voltages (p1): {solve(data, 2)}")
  logger.info(f"SUM of 12 digit voltages (p2): {solve(data, 12)}")
