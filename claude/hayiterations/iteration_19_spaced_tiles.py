# Iteration 19: Spaced Grass Tiles for Higher P(match)
# 4 grass tiles at (0,0), (0,4), (4,0), (4,4) — Manhattan distance 4 apart.
# All 24 companion candidates land on bush tiles → P(match) = 1/3 = 33.3%.
# Avg 2 re-rolls vs 3 → saves ~201 ticks per harvest.
# BUT: 4 moves between tiles = 800 ticks/harvest vs 200 ticks in column layout.
# Net: +600 move cost - 201 re-roll savings = +399 ticks/harvest. Expect WORSE.
# Testing to confirm the math.

SIZE = get_world_size()
goal = 100000000

# Plant bushes everywhere except the 4 grass tiles
for x in range(SIZE):
    for y in range(SIZE):
        if not ((x == 0 or x == 4) and (y == 0 or y == 4)):
            plant(Entities.Bush)
        move(North)
    move(East)

# Visit pattern: (0,0) → (0,4) → (4,4) → (4,0) → (0,0) ...
# Each leg is 4 moves.
def run():
    while True:
        # (0,0)
        harvest()
        if num_items(Items.Hay) >= goal:
            return
        companion, comp_pos = get_companion()
        while companion != Entities.Bush:
            harvest()
            companion, comp_pos = get_companion()
        for i in range(4):
            move(North)

        # (0,4)
        harvest()
        if num_items(Items.Hay) >= goal:
            return
        companion, comp_pos = get_companion()
        while companion != Entities.Bush:
            harvest()
            companion, comp_pos = get_companion()
        for i in range(4):
            move(East)

        # (4,4)
        harvest()
        if num_items(Items.Hay) >= goal:
            return
        companion, comp_pos = get_companion()
        while companion != Entities.Bush:
            harvest()
            companion, comp_pos = get_companion()
        for i in range(4):
            move(South)

        # (4,0)
        harvest()
        if num_items(Items.Hay) >= goal:
            return
        companion, comp_pos = get_companion()
        while companion != Entities.Bush:
            harvest()
            companion, comp_pos = get_companion()
        for i in range(4):
            move(West)

run()
