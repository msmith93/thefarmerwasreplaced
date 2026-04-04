# Iteration 7: Goto-Based Sweep (eliminate return trip after cleanup)
# Instead of move-based serpentine, use goto for each tile.
# After polyculture cleanup at companion position, go directly to
# the next sweep tile instead of returning to current tile first.
# Saves ~1 goto per polyculture harvest = ~466 ticks * ~1222 = ~94s savings.

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
                        # Plant companion
                        goto(px, py)
                        plant(ptype)
                        # Harvest with bonus
                        goto(i, ty)
                        harvest()
                        # Cleanup companion (no return to sweep pos - goto handles it)
                        goto(px, py)
                        till()
                        till()
                        # Next iteration's goto() will move to the next tile
                    else:
                        harvest()
                else:
                    harvest()
