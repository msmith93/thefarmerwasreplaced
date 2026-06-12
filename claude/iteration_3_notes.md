# Iteration 3: seam_polish

## Strategy
Final squeeze of the saturate-scan/early-peek structure:
1. **Seam-East peek**: while planting the last column, `measure(East)` wraps to this cycle's first (oldest) column — its deaths get fixed during the plant pass instead of the scan.
2. **Nearest-edge merge poll**: a seam-crossing ID match at *any* of the four field edges proves the 8x8 mega (an entity spanning rows 0&7 or cols 0&7 must be 8 wide), so poll at the closest edge instead of always walking to the top row.

## Results
| Metric | Value |
|---|---|
| Win rate | 18/18 (100%) |
| Mean time | 404.324s |
| Std dev | 4.928s |
| Best | 393.76s |
| Worst | 412.41s |
| vs. iteration 2 (405.89s) | −1.57s (**0.39% — flat**, under the 1% bar) |
| vs. baseline open_47 (436.3s) | −31.98s (7.33%) |

## Analysis
- Nominal new best, but the gain is within ~1.3 SEM — effectively flat. The structure has hit its floor, as predicted by the tick model:
  - Mandatory per cycle: 64 plants + ~16 replants (16k ticks), 63 plant-pass moves + 28 scan moves (18.2k), harvest (0.2k) ≈ 5.7s/cycle at 6075 ticks/s.
  - Actual steady state ≈ 7.4-7.5s/cycle; the gap is detour moves (mandatory to reach corpses), the watched verification tour, and water ops — all already minimized against each other.
- The fertilizer/infection equilibrium (camp only merge-blocking stragglers) and the deep-water policy are stable optima; perturbing either direction measured or modeled worse.

## Next Steps (open ideas, descending promise)
1. **Cycle-1 ramp** (~+4-6s once per run): till is mandatory, but the first scan could be timed differently for dry growth (2.1s). Maybe 0.5-1% once.
2. **Opportunistic 6x6/7x7 sub-mega pipeline**: eager partial merges are confirmed, per-tile yield is equal for n≥6, but completion detection without the seam trick requires per-tile verification that costs more than it saves (modeled ~20% worse). Only viable if someone finds a cheap sub-square completion signal.
3. **Adjacency-aware watched tour** (measure neighbors on arrival to drop upcoming visits): modeled ≈ +0.05-0.1s/cycle, high complexity.
4. Killed permanently: `swap()` on pumpkins (game refuses), drone parallelism (single-drone board), polyculture (doesn't apply), WS mega-cure (WS income ~0 when needed; infection drag too small to matter anyway).
