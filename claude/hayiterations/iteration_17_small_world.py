# Iteration 17: Smaller World (SIZE 5) + Re-Roll
# Same re-roll approach as iter 16, but on a 5x5 grid.
# Setup savings: 45 actions vs 120 on 8x8 = 75 fewer setup actions = 15,000 ticks saved (~2.5s).
# Cycle: 5 tiles × ~1,004 ticks = 5,020 ticks ≈ 0.827s > 0.5s grow time. Safe.
# P(match) = 18/24 × 1/3 = 25% (same as 8x8 due to wrapping).
# Estimated: ~203s.

set_world_size(5)
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
