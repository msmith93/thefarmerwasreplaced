# Iteration 12: Skip can_harvest, Minimal Loop
# With 16 tiles and ~1.06s sweep, grass (0.5s) is always ready.
# Skip can_harvest to save 1 tick per tile per sweep.
# Also: tightest possible main loop.
# Risk: on very first sweep, some tiles may not be grown yet.
# Harvesting regrowing grass costs 200 ticks, yields 0, re-rolls companion.
# That's only a one-time cost on the first sweep.

SIZE = get_world_size()
HALF = SIZE // 2
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

# Main loop: harvest + move, no can_harvest check
while num_items(Items.Hay) < goal:
    # Column 0
    for y in range(SIZE):
        harvest()
        move(North)
    # Move to column 4
    for k in range(HALF):
        move(East)
    # Column 4
    for y in range(SIZE):
        harvest()
        move(North)
    # Move back to column 0
    for k in range(HALF):
        move(East)
