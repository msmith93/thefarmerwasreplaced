# Iteration 20: Optimized Re-Roll Loop (v2)
# Same layout as iter 16 (8x8, col 0 grass, cols 1-7 bush).
# Optimizations:
# 1. Nested if checks: avg 2.67 ticks/check vs 4 ticks (saves ~5.3 ticks/harvest)
# 2. For loop for first 1221 harvests (0 AST cost) — skip num_items check (saves 3 ticks/harvest)
# 3. Then checked while loop for remaining harvests until 100M reached.
# Total savings: ~8.3 ticks/harvest × 1221 ≈ 10,139 ticks ≈ 1.7s
# Estimated: ~208.5s

SIZE = get_world_size()
goal = 100000000

# Plant bushes on columns 1-7
move(East)
for x in range(SIZE - 1):
    for y in range(SIZE):
        plant(Entities.Bush)
        move(North)
    move(East)

_B = Entities.Bush

def reroll():
    while True:
        harvest()
        companion, comp_pos = get_companion()
        if companion == _B:
            if comp_pos[0]:
                return

def run():
    for _ in range(1221):
        reroll()
        move(North)
    while True:
        reroll()
        if num_items(Items.Hay) >= goal:
            return
        move(North)

run()
