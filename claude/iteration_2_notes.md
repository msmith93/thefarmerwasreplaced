# Iteration 2: early_peek

## Strategy
Profile-driven evolution of iteration 1. Phase profiling showed: p1 4.4s (at the 64-plant + 63-move floor), scan 2.0s, watched-verify 1.35s, poll 0.07s, zero rescans, ~13 deaths/cycle, and a growing fertilizer surplus. Two exotic ideas were diagnosed and killed: `swap()` refuses pumpkins outright ("cannot be swapped"), and fert-camping more deads is exactly a wash (1536-pumpkin infection loss ≈ the 0.08s-equivalent it saves).

The winning change: **early peek** — while planting column *i*, a 1-tick `measure(West)` looks at the already-planted column *i−1*; rows old enough to have resolved (~37%) get their corpses fixed immediately (2-move detour + plant). Those early replants are then re-verified for free by the scan's measure checks, shortening the death pipeline by one stage. Also: till checks only on cycle 1, water-before-plant, lean inner loop without the per-tile `j < SZ1` branch.

## Results
| Metric | Value |
|---|---|
| Win rate | 18/18 (100%) |
| Mean time | 405.894s |
| Std dev | 5.245s |
| Best | 396.23s |
| Worst | 415.28s |
| vs. iteration 1 (417.47s) | **−11.6s (2.77% improvement)** |
| vs. baseline open_47 (436.3s) | −30.4s (6.97%) |

## Analysis
- Prediction (~404s) matched outcome (405.9s) — the cost model is now accurate.
- Steady-state cycle ≈ 7.6s. Remaining budget: plant pass ~4.5s (floor ~4.2s + water ops), scan ~1.7s (28 moves fixed + fewer detours now), watched ~0.9s, poll ~0.07s.
- The mandatory move count (~91 plant+scan moves) and 64+~16 plants dominate; everything else is already within ~1s/cycle of optimal for this macro-structure.
- Fertilizer equilibrium: camping only merge-blocking stragglers is optimal; expanding camping loses to infection drag; shrinking it adds serial waits.

## Next Steps
1. Extend the peek: also peek **East across the seam on the last column** (column i=7's East = first column of this cycle, oldest tiles — catches a few more first-gen deaths early). Similarly a **South/North peek within the current column** (tile below was planted 1 step ago — never resolved; useless) — only the seam-East peek has value (~1-2 deads earlier, ~0.05s/cycle).
2. Scan currently re-detours onto tiles p1 already fixed if they re-died (correct behavior, no change).
3. Watched-tour: order already matches scan order; consider ending the tour near the top row to shave the merge-poll goto (~0.1s/cycle).
4. Diminishing returns are close: remaining identified headroom ≈ 0.2-0.4s/cycle (~3-5%). If iteration 3 lands <1%, recommend stopping.
