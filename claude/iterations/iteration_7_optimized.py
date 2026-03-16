clear()

SIZE = get_world_size()
TARGET = 10000
HALF = SIZE // 2

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

# Till all tiles once
for i in range(SIZE):
    for j in range(SIZE):
        till()
        move(North)
    move(East)

while num_items(Items.Power) < TARGET:
    sx = get_pos_x()
    sy = get_pos_y()
    pt = []
    for p in range(16):
        pt.append([])
    total = 0
    for dx in range(SIZE):
        for dy in range(SIZE):
            if get_entity_type() == None:
                plant(Entities.Sunflower)
                use_item(Items.Water, 4)
            p = measure()
            if p != None:
                pt[p].append([(sx + dx) % SIZE, (sy + dy) % SIZE])
                total = total + 1
            move(North)
        move(East)

    harvested = 0
    tp = 15
    while tp >= 7 and num_items(Items.Power) < TARGET:
        tiles = pt[tp]
        n = len(tiles)
        vis = []
        for vi in range(n):
            vis.append(False)
        rem = n
        while rem > 0 and num_items(Items.Power) < TARGET and total - harvested > 9:
            cx = get_pos_x()
            cy = get_pos_y()
            bi = -1
            bd = 99
            for ti in range(n):
                if not vis[ti]:
                    ex = (tiles[ti][0] - cx) % SIZE
                    ey = (tiles[ti][1] - cy) % SIZE
                    if ex > HALF:
                        ex = SIZE - ex
                    if ey > HALF:
                        ey = SIZE - ey
                    d = ex + ey
                    if d < bd:
                        bd = d
                        bi = ti
            if bi < 0:
                rem = 0
            else:
                vis[bi] = True
                rem = rem - 1
                goto(tiles[bi][0], tiles[bi][1])
                while not can_harvest():
                    use_item(Items.Fertilizer)
                harvest()
                harvested = harvested + 1
        tp = tp - 1
