# Iteration 15: Tight 2-Tile Pair with Water
# 2 grass tiles at (0,0) and (4,0), with 62 companion tiles.
# P(poly) = 24/24 * 1/3 = 33.3% (all candidates are companions since
# tiles are distance 4 apart and don't appear in each other's candidates).
# With water at max: grass grows in 0.1s.
# Cycle: move 4 East + harvest + move 4 East + harvest + water both =
# ~10 actions + 2 waters = 12 actions per 2 harvests.
# 2,400 ticks per cycle = 0.395s. With water, growth = 0.1s. All ready.
#
# But: 12 actions / 2 harvests = 6 actions per harvest.
# vs iter 12: 16 actions / 8 harvests = 2 actions per harvest.
# Even with higher poly rate (33% vs 25%), the per-harvest cost is 3x worse.
# Expected: worse than iter 12. Testing to confirm.

SIZE = get_world_size()
HALF = SIZE // 2
goal = 100000000

# Setup: plant bushes everywhere except (0,0) and (4,0)
for x in range(SIZE):
    for y in range(SIZE):
        if not (y == 0 and (x == 0 or x == HALF)):
            plant(Entities.Bush)
        move(North)
    move(East)

# Main loop
while num_items(Items.Hay) < goal:
    # At (0,0): water + harvest
    use_item(Items.Water, 4)
    harvest()
    # Move to (4,0)
    for k in range(HALF):
        move(East)
    # At (4,0): water + harvest
    use_item(Items.Water, 4)
    harvest()
    # Move back to (0,0)
    for k in range(HALF):
        move(East)
