# Day 12: Polyomino Packing

## Problem

Given a set of polyomino shapes and a series of rectangular regions with required quantities of each shape, determine how many regions can fit all their required presents.

Each region is defined by:

- Dimensions: `WIDTHxHEIGHT`
- Required presents: a list of counts for each shape

Shapes can be placed in any of their 8 orientations (4 rotations + 4 flipped rotations) and may not overlap.

## Solution Approach

This is an NP-hard polyomino packing problem. The solution uses a two-tier strategy:

### Tier 1: Fast Heuristic Checks (O(1))

Before attempting expensive backtracking, two quick checks eliminate most cases:

1. **Area Impossibility Check**: If total cell area of all presents exceeds grid area, it's impossible.
2. **Loose Packing Bound**: Uses a 3×3 wasteful packing estimate. If even with this loose bound all presents fit, answer is definitely yes.

### Tier 2: Backtracking with Optimizations

For borderline cases where heuristics are inconclusive, backtracking explores all valid placements. Three key optimizations make this fast enough:

#### 1. Adjacent-Only Placement (Critical Optimization)

Instead of trying all `height × width` grid positions for each shape, only try positions adjacent to already-placed shapes.

**Impact**: Reduces search space from O(width×height) to O(perimeter of placed shapes), typically 4-6 positions vs 2000+.

This was the game-changer: improved performance from ~30 seconds to ~5 seconds on its own.

```python
def get_adjacent_positions() -> set[tuple[int, int]]:
    adjacent = set()
    for row in range(height):
        for col in range(width):
            if grid[row][col]:  # Found filled cell
                # Add all 4-connected neighbors
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < height and 0 <= nc < width and not grid[nr][nc]:
                        adjacent.add((nr, nc))
    return adjacent
```

#### 2. Memoization via State Caching

Cache visited `(grid_state, present_index)` pairs to avoid redundant exploration. When identical shapes exist or a state proves unsolvable, prevents retrying identical subtrees.

**Impact**: Further reduced runtime to ~2 seconds.

#### 3. Cell Counting Validation

Before attempting placement, check if remaining empty cells ≥ remaining presents. Simple but effective early pruning.

```python
remaining_presents = len(presents) - idx
if remaining_presents > count_empty_cells():
    return False  # Impossible to place all remaining
```

## Algorithm

```
for each region query:
    1. Check area feasibility (fast)
    2. Check loose packing bound (fast)
    3. If still uncertain:
        a. Generate orientations (lazy-loaded)
        b. Use backtracking with adjacent-only placement
        c. Return if all presents fit
```

## Key Insights

- **Two-tier approach**: Most queries are resolved by O(1) heuristics
- **Adjacent-only placement**: The single biggest optimization, reducing search space by orders of magnitude
- **Lazy loading**: Only generate orientations if backtracking is needed
- **Early pruning**: Memoization + cell counting catches impossible cases fast

## Complexity

- **Best case** (heuristics work): O(n) where n = number of queries
- **Worst case** (all borderline): O(n × 8^p × A) where p = presents, A = grid area
- **Typical case**: Dominated by O(n) heuristic checks; backtracking rarely needed

## Files

- `main.py`: Complete solution with detailed comments
- `input.txt`: Puzzle input
- `example.txt`: Small test case

## Running

```bash
# With input.txt
uv run python src/aoc_2025/day_12/main.py

# With example.txt (modify filename in main.py)
# filename: str = "example.txt"
```
