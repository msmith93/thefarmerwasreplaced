clear()

SIZE = get_world_size()
TARGET = 10000

def goto(tx, ty):
    cx = get_pos_x()
    cy = get_pos_y()
    dx = (tx - cx) % SIZE
    dy = (ty - cy) % SIZE
    if dx < SIZE - dx:
        for _ in range(dx):
            move(East)
    elif dx > 0:
        for _ in range(SIZE - dx):
            move(West)
    if dy < SIZE - dy:
        for _ in range(dy):
            move(North)
    elif dy > 0:
        for _ in range(SIZE - dy):
            move(South)

# Till all tiles once
for i in range(SIZE):
    for j in range(SIZE):
        till()
        move(North)
    move(East)

# Initial plant + water + measure pass (only needed once)
goto(0, 0)
petal_tiles = []
for p in range(16):
    petal_tiles.append([])
total = 0
for x in range(SIZE):
    for y in range(SIZE):
        plant(Entities.Sunflower)
        use_item(Items.Water, 4)
        p = measure()
        petal_tiles[p].append([x, y])
        total = total + 1
        move(North)
    move(East)

while num_items(Items.Power) < TARGET:
    next_pt = []
    for p in range(16):
        next_pt.append([])
    next_total = 0
    harvested = 0
    target_p = 15
    while target_p >= 7 and num_items(Items.Power) < TARGET:
        tiles = petal_tiles[target_p]
        n = len(tiles)
        vis = []
        for vi in range(n):
            vis.append(False)
        rem = n
        while rem > 0 and num_items(Items.Power) < TARGET and total - harvested > 9:
            cx = get_pos_x()
            cy = get_pos_y()
            best = -1
            best_d = 999
            for ti in range(n):
                if not vis[ti]:
                    tdx = (tiles[ti][0] - cx) % SIZE
                    tdy = (tiles[ti][1] - cy) % SIZE
                    if tdx > SIZE - tdx:
                        tdx = SIZE - tdx
                    if tdy > SIZE - tdy:
                        tdy = SIZE - tdy
                    d = tdx + tdy
                    if d < best_d:
                        best_d = d
                        best = ti
            if best < 0:
                rem = 0
            else:
                vis[best] = True
                rem = rem - 1
                pos = tiles[best]
                goto(pos[0], pos[1])
                while not can_harvest():
                    use_item(Items.Fertilizer)
                harvest()
                harvested = harvested + 1
                plant(Entities.Sunflower)
                use_item(Items.Water, 4)
                new_p = measure()
                next_pt[new_p].append(pos)
                next_total = next_total + 1
        # Carry over unharvested tiles from this group
        for ti in range(n):
            if not vis[ti]:
                next_pt[target_p].append(tiles[ti])
                next_total = next_total + 1
        target_p = target_p - 1
    # Carry over any remaining petal groups not reached
    while target_p >= 7:
        for ti in range(len(petal_tiles[target_p])):
            next_pt[target_p].append(petal_tiles[target_p][ti])
            next_total = next_total + 1
        target_p = target_p - 1
    petal_tiles = next_pt
    total = next_total
