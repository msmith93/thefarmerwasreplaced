# Iteration 6: Two-Pass Approach
# Pass 1: Scan all tiles, plant companions for bush/tree ones
# Pass 2: Harvest all tiles (polyculture bonus already in place)
# Pass 3: Cleanup - till twice on all companion positions
# Hypothesis: reduces goto overhead because planting is batched
# and companions from different tiles might share positions.

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
    # Pass 1: Scan and plant companions
    # Store companion positions for cleanup
    cleanup_xs = []
    cleanup_ys = []

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
                        goto(px, py)
                        plant(ptype)
                        # Return to sweep pos
                        if going_north:
                            goto(i, j)
                        else:
                            goto(i, SZ1 - j)
                        cleanup_xs = cleanup_xs + [px]
                        cleanup_ys = cleanup_ys + [py]
            if j < SZ1:
                if going_north:
                    move(North)
                else:
                    move(South)
        going_north = not going_north
        if i < SZ1:
            move(East)

    # Pass 2: Harvest all tiles (bonuses in place)
    going_north = True
    for i in range(SIZE):
        for j in range(SIZE):
            if can_harvest():
                harvest()
            if j < SZ1:
                if going_north:
                    move(North)
                else:
                    move(South)
        going_north = not going_north
        if i < SZ1:
            move(East)

    # Pass 3: Cleanup companion positions
    for ci in range(len(cleanup_xs)):
        goto(cleanup_xs[ci], cleanup_ys[ci])
        till()
        till()
