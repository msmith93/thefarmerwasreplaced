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

# Main batch loop
while num_items(Items.Power) < TARGET:
    goto(0, 0)
    # Build petal bins: petal_tiles[p] = list of [x,y] positions
    petal_tiles = []
    for p in range(16):
        petal_tiles.append([])
    total = 0

    # Combined plant + measure + water pass
    for x in range(SIZE):
        for y in range(SIZE):
            if get_entity_type() == None:
                plant(Entities.Sunflower)
            use_item(Items.Water, 4)
            p = measure()
            if p != None:
                petal_tiles[p].append([x, y])
                total = total + 1
            move(North)
        move(East)

    # Harvest in descending petal order (15 down to 7)
    harvested = 0
    target_p = 15
    while target_p >= 7:
        if num_items(Items.Power) >= TARGET:
            target_p = -1
        else:
            tiles = petal_tiles[target_p]
            idx = 0
            while idx < len(tiles):
                if num_items(Items.Power) >= TARGET:
                    idx = len(tiles)
                    target_p = -1
                elif total - harvested <= 10:
                    idx = len(tiles)
                else:
                    pos = tiles[idx]
                    goto(pos[0], pos[1])
                    if get_entity_type() == Entities.Sunflower:
                        while not can_harvest():
                            use_item(Items.Fertilizer)
                        harvest()
                        harvested = harvested + 1
                    idx = idx + 1
            target_p = target_p - 1
