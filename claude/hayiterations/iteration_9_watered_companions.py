# Iteration 9: Permanent Companions + Watering
# Same permanent bush layout as iter 8. Add watering to column 0 tiles
# to speed grass regrowth from 0.5s to ~0.1s (at water level 1.0).
# This allows much faster sweep cycles.
# Water: 256 tanks per 10s = 25.6/s. Each tank adds 0.25 water.
# We get plenty of water passively. Water each tile once per sweep.
# Tradeoff: watering costs 200 ticks/tile = 1,600 extra ticks/sweep.
# But if it cuts grass grow time from 0.5s to 0.1s, cycles are much faster.

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

# Main loop: sweep column 0 with watering
while num_items(Items.Hay) < goal:
    for y in range(SIZE):
        use_item(Items.Water, 4)
        if can_harvest():
            harvest()
        move(North)
