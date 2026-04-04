# Iteration 8: Permanent Companion Tiles
# Plant bushes on columns 1-7 permanently. Keep column 0 (8 tiles) as grass.
# Sweep only column 0 in a tight loop.
# ~75% of companion positions land on bush tiles (18/24 neighbors are companions).
# With 1/3 chance of Bush type → ~25% polyculture rate per harvest.
# Expected: 25% * 81920 + 75% * 512 = 20,864 hay/harvest.
# NO planting/cleanup overhead during main loop!

SIZE = get_world_size()
goal = 100000000

# Setup: plant bushes on columns 1-7
move(East)
for x in range(SIZE - 1):
    for y in range(SIZE):
        plant(Entities.Bush)
        move(North)
    move(East)
# Now back at (0,0)

# Main loop: tight sweep of column 0
# Add slight delay to ensure grass regrows between visits (0.5s grow time)
while num_items(Items.Hay) < goal:
    for y in range(SIZE):
        if can_harvest():
            harvest()
        move(North)
