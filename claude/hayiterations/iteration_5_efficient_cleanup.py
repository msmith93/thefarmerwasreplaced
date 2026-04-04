# Iteration 5: Efficient Cleanup (revised)
# Change from iteration 3: skip harvesting companion bush/tree.
# Just till() twice to restore grassland with fresh grass.
# Saves 1 action (200 ticks) per polyculture harvest.
# With ~1,234 poly harvests, saves ~246,800 ticks ≈ 40.6s

SIZE = get_world_size()
SZ1 = SIZE - 1
HALF = SIZE // 2
goal = 100000000

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
    going_north = True
    for i in range(SIZE):
        for j in range(SIZE):
            if can_harvest():
                comp = get_companion()
                if comp != None:
                    ptype = comp[0]
                    pos = comp[1]
                    px = pos[0]
                    py = pos[1]
                    if ptype == Entities.Bush or ptype == Entities.Tree:
                        sx = get_pos_x()
                        sy = get_pos_y()
                        # Plant companion
                        goto(px, py)
                        plant(ptype)
                        # Harvest with bonus
                        goto(sx, sy)
                        harvest()
                        # Cleanup: till twice to restore grass (skip harvesting bush)
                        goto(px, py)
                        till()
                        till()
                        # Return to sweep position
                        goto(sx, sy)
                    else:
                        harvest()
                else:
                    harvest()
            if j < SZ1:
                if going_north:
                    move(North)
                else:
                    move(South)
        going_north = not going_north
        if i < SZ1:
            move(East)
