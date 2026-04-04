# Iteration 11: Two Grass Columns + Watering
# Combine iteration 9 (watering) and iteration 10 (two columns).
# 16 grass tiles on columns 0 and 4 with water for fast regrowth.
# Use 1 water tank per tile (not 4) to conserve water supply.
# Growth rate at water 0.25: 2x → effective grow time 0.25s.

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

# Main loop: sweep columns 0 and 4 with watering
while num_items(Items.Hay) < goal:
    # Column 0
    for y in range(SIZE):
        use_item(Items.Water)
        if can_harvest():
            harvest()
        move(North)
    # Move to column 4
    for k in range(HALF):
        move(East)
    # Column 4
    for y in range(SIZE):
        use_item(Items.Water)
        if can_harvest():
            harvest()
        move(North)
    # Move back to column 0
    for k in range(HALF):
        move(East)
