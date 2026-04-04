# Iteration 13: Unrolled Loop + Skip Column 4 in Setup
# Column 4 is distance 4 from column 0 (never in companion candidates).
# Skip planting there = save 8 plants + 8 moves = 16 actions.
# Unroll inner loop to eliminate range() overhead (1 tick/sweep).
# Also skip column 4 during setup by moving East twice past it.

SIZE = get_world_size()
goal = 100000000

# Setup: plant bushes on columns 1,2,3,5,6,7 (skip col 4)
move(East)
# Col 1
for y in range(SIZE):
    plant(Entities.Bush)
    move(North)
move(East)
# Col 2
for y in range(SIZE):
    plant(Entities.Bush)
    move(North)
move(East)
# Col 3
for y in range(SIZE):
    plant(Entities.Bush)
    move(North)
# Skip col 4: move East twice
move(East)
move(East)
# Col 5
for y in range(SIZE):
    plant(Entities.Bush)
    move(North)
move(East)
# Col 6
for y in range(SIZE):
    plant(Entities.Bush)
    move(North)
move(East)
# Col 7
for y in range(SIZE):
    plant(Entities.Bush)
    move(North)
move(East)
# Now at (0,0)

# Main loop: unrolled for maximum speed
while num_items(Items.Hay) < goal:
    harvest()
    move(North)
    harvest()
    move(North)
    harvest()
    move(North)
    harvest()
    move(North)
    harvest()
    move(North)
    harvest()
    move(North)
    harvest()
    move(North)
    harvest()
    move(North)
