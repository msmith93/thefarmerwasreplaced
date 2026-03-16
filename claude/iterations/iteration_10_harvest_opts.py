clear()

SIZE = get_world_size()
TARGET = 10000
HALF = SIZE // 2
SZ1 = SIZE - 1

first = True
while num_items(Items.Power) < TARGET:
    ptx = []
    pty = []
    for p in range(16):
        ptx.append([])
        pty.append([])
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
                ptx[p].append(get_pos_x())
                pty[p].append(get_pos_y())
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
    cx = get_pos_x()
    cy = get_pos_y()
    while tp >= 7 and num_items(Items.Power) < TARGET:
        rx = ptx[tp]
        ry = pty[tp]
        rn = len(rx)
        while rn > 0 and num_items(Items.Power) < TARGET and total - harvested > 9:
            bi = 0
            bd = 99
            found = False
            for ti in range(rn):
                if not found:
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
                        if d < 2:
                            found = True
            tx = rx[bi]
            ty = ry[bi]
            gx = (tx - cx) % SIZE
            gy = (ty - cy) % SIZE
            if gx <= HALF:
                for _ in range(gx):
                    move(East)
            else:
                for _ in range(SIZE - gx):
                    move(West)
            if gy <= HALF:
                for _ in range(gy):
                    move(North)
            else:
                for _ in range(SIZE - gy):
                    move(South)
            while not can_harvest():
                use_item(Items.Fertilizer)
            harvest()
            harvested = harvested + 1
            cx = tx
            cy = ty
            rn = rn - 1
            rx[bi] = rx[rn]
            ry[bi] = ry[rn]
        tp = tp - 1
