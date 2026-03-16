clear()

SIZE = get_world_size()
TARGET = 10000
HALF = SIZE // 2
SZ1 = SIZE - 1

def goto(tx, ty):
    cx = get_pos_x()
    cy = get_pos_y()
    dx = (tx - cx) % SIZE
    dy = (ty - cy) % SIZE
    if dx <= HALF:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(SIZE - dx):
            move(West)
    if dy <= HALF:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(SIZE - dy):
            move(South)

first = True
while num_items(Items.Power) < TARGET:
    pt = []
    for p in range(16):
        pt.append([])
    total = 0
    gn = True
    for col in range(SIZE):
        for step in range(SIZE):
            if first:
                till()
            if get_entity_type() == None:
                plant(Entities.Sunflower)
                use_item(Items.Water, 4)
            p = measure()
            if p != None:
                pt[p].append([get_pos_x(), get_pos_y()])
                total = total + 1
            if step < SZ1:
                if gn:
                    move(North)
                else:
                    move(South)
        if col < SZ1:
            move(East)
        gn = not gn
    first = False

    harvested = 0
    tp = 15
    while tp >= 7 and num_items(Items.Power) < TARGET:
        tiles = pt[tp]
        n = len(tiles)
        rx = []
        ry = []
        for i in range(n):
            rx.append(tiles[i][0])
            ry.append(tiles[i][1])
        rn = n
        while rn > 0 and num_items(Items.Power) < TARGET and total - harvested > 9:
            cx = get_pos_x()
            cy = get_pos_y()
            bi = 0
            bd = 99
            for ti in range(rn):
                ex = (rx[ti] - cx) % SIZE
                ey = (ry[ti] - cy) % SIZE
                if ex > HALF:
                    ex = SIZE - ex
                if ey > HALF:
                    ey = SIZE - ey
                d = ex + ey
                if d < bd:
                    bd = d
                    bi = ti
            goto(rx[bi], ry[bi])
            while not can_harvest():
                use_item(Items.Fertilizer)
            harvest()
            harvested = harvested + 1
            rn = rn - 1
            rx[bi] = rx[rn]
            ry[bi] = ry[rn]
        tp = tp - 1
