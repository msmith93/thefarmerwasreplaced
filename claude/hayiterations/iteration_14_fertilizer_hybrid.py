# Iteration 14: Fertilizer Hybrid
# Use fertilizer to instantly regrow grass on a SINGLE tile, avoiding 0.5s wait.
# With 1 tile: fertilize → cure with WS → harvest → repeat.
# All 24 companion candidates are companion tiles → P(poly) = 33.3%.
# Cost: 3 actions (fert + WS + harvest) vs 2 (harvest + move) per harvest.
# BUT: only 1 tile needs 0 waiting (vs 8 tiles needing 0.5s stagger).
# Bottleneck: fertilizer supply (0.8/s).
# Phase 1: burn fertilizer (instant harvests, 33% poly rate)
# Phase 2: switch to column sweep (normal 25% poly rate)

SIZE = get_world_size()
goal = 100000000

# Setup: plant bushes on ALL tiles except (3,3) [center, max distance from edges]
# Actually, use (0,0) for simplicity - plant bushes on everything else
for x in range(SIZE):
    for y in range(SIZE):
        if x != 0 or y != 0:
            if x > 0 or y > 0:
                plant(Entities.Bush)
        move(North)
    move(East)
# Now at (0,0)

# Phase 1: Fertilizer-powered rapid harvest
# Use fertilizer to grow instantly, WS to cure, harvest.
# Stop when fertilizer runs out.
while num_items(Items.Fertilizer) >= 1:
    use_item(Items.Fertilizer)
    use_item(Items.Weird_Substance)
    harvest()
    if num_items(Items.Hay) >= goal:
        pass

# Phase 2: Switch to column sweep
# Need to restore column 0 tiles to grass
# (0,0) already has grass. Tiles (0,1)-(0,7) have bushes.
# Restore them: visit each, till twice
for y in range(SIZE - 1):
    move(North)
    till()
    till()
# Back to (0,0) via one more North
move(North)

# Column sweep
while num_items(Items.Hay) < goal:
    for y in range(SIZE):
        harvest()
        move(North)
