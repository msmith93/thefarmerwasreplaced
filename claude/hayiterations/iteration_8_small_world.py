# Iteration 8: Smaller World Size
# Hypothesis: set_world_size(3) gives 9 tiles. Fewer tiles = faster sweeps,
# shorter goto distances. Tradeoff: fewer tiles harvested per sweep.
# 9 tiles * 81,920 (poly) ≈ 737,280 hay/sweep (if all poly).
# Need ~136 sweeps. Each sweep much faster on 3x3.

SIZE = 3
SZ1 = SIZE - 1
HALF = SIZE // 2
goal = 100000000

set_world_size(SIZE)

def goto(tx, ty):
    cx = get_pos_x()
    cy = get_pos_y()
    dx = (tx - cx) % SIZE
    if dx > HALF:
        for k in range(SIZE - dx):
            move(West)
    else:
        for k in range(dx):
            move(East)
    dy = (ty - cy) % SIZE
    if dy > HALF:
        for k in range(SIZE - dy):
            move(South)
    else:
        for k in range(dy):
            move(North)

while num_items(Items.Hay) < goal:
    for i in range(SIZE):
        going_north = i % 2 == 0
        for j in range(SIZE):
            if going_north:
                ty = j
            else:
                ty = SZ1 - j
            goto(i, ty)
            if can_harvest():
                comp = get_companion()
                if comp != None:
                    ptype = comp[0]
                    pos = comp[1]
                    px = pos[0]
                    py = pos[1]
                    if ptype == Entities.Bush or ptype == Entities.Tree:
                        goto(px, py)
                        plant(ptype)
                        goto(i, ty)
                        harvest()
                        goto(px, py)
                        till()
                        till()
                    else:
                        harvest()
                else:
                    harvest()
