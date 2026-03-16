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

def wrap_dist(a, b):
    d = (a - b) % SIZE
    r = SIZE - d
    if d < r:
        return d
    return r

# Till all tiles once
for i in range(SIZE):
    for j in range(SIZE):
        till()
        move(North)
    move(East)

# Main batch loop
while num_items(Items.Power) < TARGET:
    # Combined plant + measure + water pass (from known position)
    sx = get_pos_x()
    sy = get_pos_y()
    petal_tiles = []
    for p in range(16):
        petal_tiles.append([])
    total = 0
    for dx in range(SIZE):
        for dy in range(SIZE):
            if get_entity_type() == None:
                plant(Entities.Sunflower)
            use_item(Items.Water, 4)
            p = measure()
            if p != None:
                ax = (sx + dx) % SIZE
                ay = (sy + dy) % SIZE
                petal_tiles[p].append([ax, ay])
                total = total + 1
            move(North)
        move(East)

    # Harvest in descending petal order with nearest-neighbor routing
    harvested = 0
    target_p = 15
    while target_p >= 7 and num_items(Items.Power) < TARGET:
        tiles = petal_tiles[target_p]
        n = len(tiles)
        visited = []
        for vi in range(n):
            visited.append(False)
        remaining = n
        while remaining > 0 and num_items(Items.Power) < TARGET and total - harvested > 10:
            cx = get_pos_x()
            cy = get_pos_y()
            best = -1
            best_d = 999
            for ti in range(n):
                if not visited[ti]:
                    d = wrap_dist(tiles[ti][0], cx) + wrap_dist(tiles[ti][1], cy)
                    if d < best_d:
                        best_d = d
                        best = ti
            if best < 0:
                remaining = 0
            else:
                visited[best] = True
                remaining = remaining - 1
                goto(tiles[best][0], tiles[best][1])
                if get_entity_type() == Entities.Sunflower:
                    while not can_harvest():
                        use_item(Items.Fertilizer)
                    harvest()
                    harvested = harvested + 1
        target_p = target_p - 1
