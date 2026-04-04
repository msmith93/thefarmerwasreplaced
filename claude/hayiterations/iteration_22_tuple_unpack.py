# Iteration 22: Tuple Unpack Optimization
# Key insight: `comp_pos[0]` costs 1 Subscript tick per check.
# `companion, (cx, cy) = get_companion()` unpacks WITHOUT Subscript.
# Then `if cx:` costs only If(1) = 1 tick vs Subscript(1)+If(1) = 2 ticks.
# Saves 1 tick per check × avg 1.33 (only when Bush matches) × 1221 = ~1,624 ticks ≈ 0.27s.
# Combined with all iter 20 optimizations.

SIZE = get_world_size()
goal = 100000000

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
        companion, (cx, cy) = get_companion()
        if companion == _B:
            if cx:
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
