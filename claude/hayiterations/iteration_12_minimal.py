# Iteration 12: Minimal Single Column (no water, no can_harvest)
# Tightest possible loop: harvest() + move(North) on 8 tiles.
# Cycle time: 8 * (200+200) + ~3 overhead = ~3,203 ticks = 0.527s.
# Grass regrows in 0.500s → 0.027s margin. Should work.
# Total actions per sweep: 16 (8 harvest + 8 move).
# Expected: 599 sweeps * 16 = 9,584 actions = ~316s.

SIZE = get_world_size()
goal = 100000000

# Setup: plant bushes on columns 1-7
move(East)
for x in range(SIZE - 1):
    for y in range(SIZE):
        plant(Entities.Bush)
        move(North)
    move(East)

# Main loop: absolute minimal
while num_items(Items.Hay) < goal:
    for y in range(SIZE):
        harvest()
        move(North)
