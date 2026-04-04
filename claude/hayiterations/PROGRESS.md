# Hay_Single Leaderboard Optimization Progress

## Goal
Collect 100,000,000 hay as fast as possible on an 8x8 farm with a single drone.

## Key Mechanics
- Grass grows automatically on Grassland in 0.5s (no planting needed)
- Base yield: 512 hay/harvest
- **Polyculture**: 160x multiplier (81,920 hay/harvest) when correct companion planted
  - Each grass tile wants a random companion (Bush, Tree, or Carrot) at a random position within Manhattan distance 3
  - Companion re-rolls on every harvest
  - Bush/Tree are free to plant on Grassland; Carrot requires soil + resources
- Water speeds growth 1x-5x (linear with water level 0-1)
- Fertilizer: reduces grow time by 2s but infects tile (halves yield)
- Actions (move/harvest/plant/till/use_item) cost 200 ticks; checks (can_harvest/get_companion) cost 1 tick
- Powered speed: 6,075 ticks/sec

## Results Summary

| Iter | Name | Mean Time | Win Rate | Key Change | vs Previous |
|------|------|-----------|----------|------------|-------------|
| 1 | Baseline | TIMEOUT | 0/5 | hay_basic.py copy | - |
| 2 | Serpentine + Cache | TIMEOUT | 0/5 | Serpentine traversal, cached SIZE | marginal |
| 3 | Basic Polyculture | 685.9s | 5/5 | Plant companion, harvest with 160x bonus | **first win** |
| 4 | Skip Cleanup | 3037.2s | 4/5 | Don't cleanup companions | **REGRESSION** |
| 5 | Efficient Cleanup | 644.2s | 5/5 | till-only cleanup (skip bush harvest) | +6.1% |
| 6 | Two-Pass | 958.5s | 5/5 | Batch plant/harvest/cleanup passes | **REGRESSION** |
| 7 | Goto-Based Sweep | 616.8s | 5/5 | Eliminate return trip after cleanup | +4.2% |
| 8 | Permanent Companions | 482.2s | 5/5 | Static bush layout, sweep 8 tiles | +22% |
| 9 | + Watering | 408.8s | 5/5 | Water column 0 for fast regrowth | +15% |
| 10 | Two Columns (no water) | 408.3s | 5/5 | 16 grass tiles, 2 columns | ~same |
| 11 | Two Columns + Water | 569.4s | 5/5 | Water overhead not justified | **REGRESSION** |
| **12** | **Minimal Single Column** | **320.7s** | **5/5** | **No can_harvest, no water, 1 col** | **+21%** |
| 13 | Unrolled + Skip Col 4 | 322.3s | 5/5 | Micro-optimizations | ~same |
| 14 | Fertilizer Hybrid | 322.0s | 5/5 | Fertilizer phase + column sweep | ~same |
| 15 | Tight 2-Tile Pair | 722.5s | 5/5 | 2 tiles, higher poly, water | **REGRESSION** |
| **16** | **Companion Re-Roll** | **210.3s** | **5/5** | **Re-roll companion to 100% poly** | **+34%** |
| 17 | Small World SIZE 5 | 234.4s | 5/5 | 5x5 grid, less setup | **REGRESSION** |
| 18 | Smallest World SIZE 4 | 339.3s | 5/5 | 4x4 grid | **REGRESSION** |
| 19 | Spaced Tiles | 288.3s | 5/5 | P(match)=33%, 4 moves/harvest | **REGRESSION** |
| 20 | Optimized Loop | 208.9s | 5/5 | Nested ifs, for-loop | +0.7% |
| 21 | Mixed Col 0 | 230.8s | 5/5 | 6 grass + 2 bush on col 0 | **REGRESSION** |
| **22** | **Tuple Unpack** | **208.6s** | **5/5** | **Avoid Subscript via unpacking** | **+0.8%** |

**Final Best: Iteration 22 at 208.6s mean (min 200.9s)**

## Optimization Journey

### Phase 1: Finding Polyculture (Iters 1-3)
Without polyculture, 512 hay/harvest is too slow to reach 100M. The 160x polyculture multiplier
is the single most important optimization, reducing required harvests from ~195K to ~4,800.

### Phase 2: Optimizing Active Polyculture (Iters 3-7)
Per-harvest companion planting requires: goto companion, plant, goto back, harvest, goto companion,
cleanup (till x2), goto back. At ~11 extra actions per harvest, the overhead is massive.
Best active approach (iter 7): 616.8s.

### Phase 3: Passive Polyculture Breakthrough (Iters 8-12)
Key insight: plant bushes permanently on 56/64 tiles. Grass tiles get ~25% automatic polyculture
bonus with ZERO per-harvest overhead. This eliminated all plant/goto/cleanup actions.
Best passive approach (iter 12): 320.7s — a **2.14x speedup** over best active approach.

### Phase 4: Diminishing Returns (Iters 13-15)
Attempted micro-optimizations (unrolling, fertilizer hybrid, fewer tiles with higher poly rate).
None improved beyond iter 12. The 320s time appeared to be near the theoretical minimum
for the passive polyculture approach (315.6s).

### Phase 5: Re-Roll Breakthrough (Iter 16)
Inspired by the user's human_hay.py script. Key insight: harvesting regrowing grass (before it
finishes growing) costs 200 ticks, yields 0 hay, but **re-rolls the companion**. By repeatedly
harvesting until the companion is Bush at a bush tile, we achieve ~100% polyculture rate (vs 25%
passive). This cuts required productive harvests from ~4,800 to ~1,221. Average ~3 re-roll
attempts per harvest (P(match) = 18/24 × 1/3 = 25%), costing ~600 extra ticks, but this is
far cheaper than 3x more harvests. Result: **210.3s mean — a 34% improvement over iter 12**.

### Phase 6: Micro-Optimizations (Iters 17-22)
Tested several approaches to improve on iter 16:
- **Smaller grids (17-18)**: Less setup but regrowth failures when return time < 0.5s grow time.
  SIZE 5: ~27% miss rate. SIZE 4: systematic failures. Wrapping means P(match)=25% regardless.
- **Spaced tiles (19)**: P(match) rises to 33% but 4 moves/harvest outweighs savings.
- **Mixed column 0 (21)**: Bushes on col 0 improve P(match) to ~28% but skip-moves and fewer tiles hurt.
- **AST tick optimization (20, 22)**: Nested if checks save ~5 ticks/check (short-circuit when type!=Bush).
  Tuple unpacking avoids Subscript cost. For-loop avoids num_items overhead. Total: ~1.7s faster.
Result: **208.6s mean — essentially at the theoretical minimum**.

## Why Iteration 22 Is Best

### Passive Approach Theoretical Minimum: 315.6s

For the passive polyculture approach (iter 12):
- **Harvests needed**: ceil(100,000,000 / (0.25 * 81,920 + 0.75 * 512)) = **4,793**
- **Actions per harvest**: 2 (harvest + move) → **319.5s** with setup
- **Actual (iter 12)**: 320.7s mean — within 1.5% of floor

### Re-Roll Approach (Iter 16): Breaking the Passive Floor

The re-roll trick achieves ~100% polyculture → 81,920 hay per productive harvest:
- **Productive harvests needed**: ceil(100,000,000 / 81,920) = **1,221**
- **Re-roll cost per harvest**: avg 3 re-rolls × (harvest(200) + get_companion(1)) = ~603 ticks
- **Per productive harvest**: harvest(200) + re-rolls(~603) + get_companion(1) + move(200) = ~1,004 ticks
- **Setup**: ~120 actions × 200 = 24,000 ticks
- **Estimated total**: 1,221 × 1,004 + 24,000 = ~1,249,884 ticks
- **Estimated time**: 1,249,884 / 6,075 = **205.7s**
- **Actual (iter 16)**: 210.3s mean — ~4.6s from AST line tick overhead
- **With AST optimization (iter 22)**: 208.6s mean, 200.9s min

**Why re-roll beats passive**: Trading 25% poly rate for 100% poly rate means 4× fewer
productive harvests (1,221 vs 4,793). Each re-roll costs ~600 ticks of overhead, but
eliminating ~3,572 full harvest+move cycles (at 400 ticks each) saves ~1.4M ticks.
Net savings: ~700K ticks = ~115s.

## Lessons Learned

1. **Polyculture is essential** — 160x multiplier reduces harvests from 195K to ~4,800
2. **Passive > Active polyculture** — Permanent companion tiles eliminate all per-harvest overhead
3. **Re-roll > Passive** — Harvesting regrowing grass re-rolls companion; loop until match → 100% poly rate
4. **Minimize actions per harvest** — The 200-tick action cost dominates; every extra action hurts
5. **Match sweep timing to grow time** — 8 tiles at 0.527s cycle perfectly matches 0.5s growth
6. **Water only helps when cycle < grow time** — For 8 tiles, cycle > 0.5s naturally
7. **Cleanup is mandatory** — Leaving companion plants destroys grass permanently
8. **P(match) = 1/3 always** — Entity type mix at companion tiles doesn't affect poly rate
9. **Re-roll math**: P(match per attempt) = 25% → avg 4 attempts (3 re-rolls) at ~200 ticks each. This 600-tick overhead per harvest is far cheaper than 3 extra full harvest+move cycles at 400 ticks each
10. **8 tiles is the sweet spot** — Fewer tiles risk regrowth failures from variance (return time < 0.5s). More tiles waste setup time. 8 gives 1.15s return time with ample margin.
11. **AST ticks matter at the margin** — Nested ifs (short-circuit), tuple unpacking (avoid Subscript), and for-loops (no Compare) save ~10K ticks total
