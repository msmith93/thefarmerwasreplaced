# Iteration 18: Smallest Viable World (SIZE 4) + Re-Roll
# 4x4 grid: 4 grass tiles, 12 bush tiles.
# Setup: 28 actions vs 120 on 8x8 = 92 fewer = 18,400 ticks saved (~3s).
# Cycle: 4 tiles × ~1,004 ticks = 4,016 ticks ≈ 0.661s > 0.5s grow time.
# BUT: return time = 3 × ~1,004 = 3,012 ticks ≈ 0.496s -- JUST under 0.5s.
# Risk: when re-rolls are few, grass may not regrow in time.
# Testing to see actual impact. Estimated ~202s if misses are rare, worse if not.

set_world_size(4)
SIZE = get_world_size()
goal = 100000000

# Plant bushes on columns 1 through SIZE-1
move(East)
for x in range(SIZE - 1):
    for y in range(SIZE):
        plant(Entities.Bush)
        move(North)
    move(East)

# Main loop: harvest + re-roll + move
def run():
    while True:
        harvest()
        if num_items(Items.Hay) >= goal:
            return
        companion, comp_pos = get_companion()
        while companion != Entities.Bush or comp_pos[0] == 0:
            harvest()
            companion, comp_pos = get_companion()
        move(North)

run()
