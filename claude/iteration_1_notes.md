# Iteration 1: saturate_scan

## Strategy
Improve on the Opus 4.7 baseline (`open_47_pumpkins.py`, benchmarked at **436.3s** mean) using diagnostics-driven design:

- **Yields are ×512** vs docs: an 8x8 mega = 196,608 pumpkins, so only ~51-52 cycles needed for 10M.
- **`measure()` on pumpkins returns an entity ID** (undocumented). Dead pumpkins return `None`, so a neighbor's death is detectable from an adjacent tile in 1 tick. Merged mega tiles share one ID; an ID match across the field's wraparound seam (y=7 vs y=0) proves the mega spans all 8 rows = full 8x8.
- **Water income 256 tanks/10s** — deep-but-rare watering (4 tanks when level <0.4) keeps growth ~4x for only ~6 ops/cycle.
- **Fertilizer income 8/10s** (~6/cycle) — enough to instant-mature only the late stragglers (infection costs 1536 pumpkins/tile, ~2% of cycle yield; worth it).

Cycle structure: snake plant pass (till-check + plant + deep water) → 3-column scan (own tile + `measure(West/East)` death checks, inline replant, record watched coords) → targeted revisit of watched tiles with fertilizer camping → seam-ID poll → `harvest()`.

## Results
| Metric | Value |
|---|---|
| Win rate | 18/18 (100%) |
| Mean time | 417.473s |
| Std dev | 5.685s |
| Best | 408.86s |
| Worst | 433.77s |
| vs. baseline open_47 (436.3s) | **−18.8s (4.32% improvement)** |

## Analysis
- v1 (full-field water saturation every pass + two full 3-column scans) was **441.8s — worse than baseline**. Phase profiling (free `quick_print` timers) showed: p1 4.95s, scan1 2.1s, scan2 1.35s, poll 0.07s, and the merge poll succeeded on the **first try every cycle** — convergence was already solved; the action count was the problem. Water inventory grew +200/cycle unused.
- v2 fixes: deep-rare watering (~6 ops vs 22), targeted watched-list pass instead of a second full scan. Steady-state cycle ≈ 7.7-8.0s vs baseline ≈ 8.55s.
- The game's output Logger keeps only ~100 lines — instrumented runs get tail-truncated; a "missing FINAL_TIME" scare was a flaky read, verified healthy via REP_START/FINAL_TIME marker pairing (18/18).
- Cycle budget now: plant pass ~4.5s (64 plants + 63 moves ≈ mandatory floor 4.2s), scan ~1.9s, watched pass ~1s, poll+harvest ~0.1s.

## Next Steps
Ranked ideas for iteration 2:
1. **Plant scan columns during the scan** (5-column plant pass ~40 moves, scan plants its own 3 columns): cuts ~21 moves/cycle ≈ 0.7s/cycle, but pushes ~5 extra late deaths to the camped phase — fert budget (~6.8/cycle) becomes binding. Worth testing.
2. **Trim scan detour cost**: when a dead neighbor is found West and the next row's West is also dead, handle both in one detour (cluster handling); marginal.
3. **Reduce p1 fixed costs**: skip `get_ground_type()` till-check after cycle 1 with a boolean flag (~0.1s/run); reorder water check before plant.
4. **Tune water threshold** (0.4 → 0.3) and fert camping trigger; measure infection drag (currently ~2.4 tiles/cycle ≈ 1 extra cycle over the run — consider water-spin camps when fert is low instead of skipping).
5. **Wilder: swap()-based spare-pumpkin patching** (7x7 mega + nursery column) modeled at ~3.80 pumpkins/tick — roughly equal to baseline, not obviously better; only revisit if (1) plateaus, and first test whether `swap()` works on pumpkins at all.
