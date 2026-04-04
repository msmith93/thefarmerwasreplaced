# Iteration 10: Two Grass Columns (no watering)
# Hypothesis: 16 grass tiles (columns 0 and 4) with 48 companion tiles.
# Columns 0 and 4 are Manhattan distance 4 apart, so they don't appear
# in each other's companion candidates (distance 3 max).
# P(poly) stays at ~25%. More tiles = more hay per sweep.
# No watering to save 200 ticks/tile overhead.
# Grass grows in 0.5s; sweep of 16 tiles takes ~1.06s > 0.5s.

SIZE = get_world_size()
goal = 100000000

# Setup: plant bushes on all columns except 0 and 4
move(East)
for x in range(SIZE - 1):
    col = (x + 1) % SIZE
    for y in range(SIZE):
        if col != 0 and col != 4:
            plant(Entities.Bush)
        move(North)
    move(East)
# Back at (0,0)

# Main loop: sweep columns 0 and 4 in a tight loop
# Column 0: move North 8 times, then goto column 4
# Column 4: move North 8 times, then goto column 0
HALF = SIZE // 2
while num_items(Items.Hay) < goal:
    # Column 0
    for y in range(SIZE):
        if can_harvest():
            harvest()
        move(North)
    # Move to column 4
    for k in range(HALF):
        move(East)
    # Column 4
    for y in range(SIZE):
        if can_harvest():
            harvest()
        move(North)
    # Move back to column 0
    for k in range(HALF):
        move(East)
