from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from aoc_2025.utils import get_logger, simple_txt_parser

logger = get_logger(__name__)


@dataclass
class Machine:
  """Represents a machine with indicator lights and buttons.

  The indicator lights are modeled as bits in an integer, where each bit
  represents the state of one light (0=off, 1=on). Buttons are represented
  as lists of indices they affect (for toggling lights or incrementing counters).
  """

  lights: int  # Bitmask of the target light configuration
  buttons: list[list[int]]  # List of lists: indices each button affects
  voltages: list[int]  # Voltage requirements (targets for counters)

  @staticmethod
  def from_data(data: str) -> Machine:
    """Parse a machine line and return a Machine instance.

    Expected input format example:
    [.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}

    - The bracketed segment describes the desired state using '.' (False) and '#' (True).
    - Parentheses groups list actuations for each button in left-to-right order; each group
      contains comma-separated indices that the button toggles.
    - The braces contain comma-separated integer voltages.
    """
    # Extract the desired state from brackets [.##.]
    lights_match = re.search(r"\[([.#]+)\]", data)
    if not lights_match:
      raise ValueError(f"Could not parse desired state from: {data}")
    lights = sum((1 if bit == "#" else 0) << idx for idx, bit in enumerate(lights_match.group(1)))
    size = len(lights_match.group(1))
    logger.debug(f"Desired state: {lights:0{size}b} ({size} bits)")

    # Extract actuator groups from parentheses (indices each button toggles)
    button_matches: list[str] = re.findall(r"\(([0-9,]+)\)", data)
    if not button_matches:
      raise ValueError(f"Could not parse buttons from: {data}")
    buttons: list[list[int]] = []
    for match in button_matches:
      indices = [int(x) for x in match.split(",")]
      buttons.append(indices)
    logger.debug(f"Buttons: {buttons}")

    # Extract voltages from braces {3,5,4,7}
    voltage_match = re.search(r"\{([0-9,]+)\}", data)
    if not voltage_match:
      raise ValueError(f"Could not parse voltages from: {data}")
    voltages = list(map(int, voltage_match.group(1).split(",")))
    logger.debug(f"Voltages: {voltages}")

    return Machine(lights, buttons, voltages)

  def lights_solver(self, start: int = 0) -> int:
    """Solve for the minimum button presses to reach the desired state from start.

    Since pressing a button twice is the same as not pressing it (XOR property),
    we only need to consider pressing each button 0 or 1 time. This reduces the
    problem to finding the smallest subset of buttons whose combined toggles
    (XOR of their bitmasks) transform the start state to the desired state.

    We use brute-force enumeration of all 2^n subsets, where n is the number
    of buttons, which is efficient for small n (typically <= 10-20).
    """
    if start == self.lights:
      return 0

    # Compute bitmasks for buttons
    button_bitmasks = [sum(1 << idx for idx in button) for button in self.buttons]

    n = len(button_bitmasks)
    min_presses: int = n + 1  # Initialize to an impossible value
    for mask in range(1 << n):  # Iterate over all subsets (2^n possibilities)
      xor_state = start
      presses = 0
      for i in range(n):
        if mask & (1 << i):  # If button i is in the subset
          xor_state ^= button_bitmasks[i]  # Apply the button's toggle
          presses += 1
      if xor_state == self.lights:
        min_presses = min(min_presses, presses)

    if min_presses > n:
      raise RuntimeError("No solution found")
    return min_presses

  def voltage_solver(self) -> int:
    """Solve for the minimum button presses to reach the target voltages from all zeros.

    Uses PuLP (integer linear programming) to minimize the total number of button presses
    subject to the constraint that each counter reaches its target value exactly.
    """
    import pulp

    n_buttons = len(self.buttons)
    n_counters = len(self.voltages)

    # Create the LP problem
    problem = pulp.LpProblem("Voltage_Configuration", pulp.LpMinimize)

    # Decision variables: x[j] = number of times button j is pressed (non-negative integer)
    x_vars = [pulp.LpVariable(f"x_{j}", lowBound=0, cat="Integer") for j in range(n_buttons)]

    # Objective: minimize total presses
    problem += pulp.lpSum(x_vars), "Total_Presses"

    # Constraints: for each counter i, sum of presses of buttons affecting i == target[i]
    for i in range(n_counters):
      constraint_expr = pulp.lpSum(x_vars[j] for j in range(n_buttons) if i in self.buttons[j])
      problem += constraint_expr == self.voltages[i], f"Counter_{i}"

    # Solve
    solver = pulp.PULP_CBC_CMD(msg=False)
    problem.solve(solver)

    if pulp.LpStatus[problem.status] != "Optimal":
      raise RuntimeError(f"No optimal solution found: {pulp.LpStatus[problem.status]}")

    return sum(int(pulp.value(var)) for var in x_vars)  # type: ignore[arg-type]


def part_1(raw: list[str]) -> int:
  result = 0
  for line in raw:
    machine = Machine.from_data(line)
    presses = machine.lights_solver()
    result += presses
  return result


def part_2(raw: list[str]) -> int:
  result = 0
  for line in raw:
    machine = Machine.from_data(line)
    presses = machine.voltage_solver()
    result += presses
  return result


if __name__ == "__main__":
  """Main execution block: Load input data and run both parts."""
  # Run the solutions for both parts using the input file
  filename: str = "input.txt"
  file_path = Path(__file__).parent / filename
  data = simple_txt_parser(file_path)

  logger.info("Starting Day 10 Solutions")
  logger.info(f"Part 1: {part_1(data)}")  # 404
  logger.info(f"Part 2: {part_2(data)}")
