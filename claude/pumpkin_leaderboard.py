clear()
SIZE = get_world_size()
SZ1 = SIZE - 1
HALF = SIZE // 2
TARGET = 10000000
WTHRESH = 0.75

def goto(tx, ty):
    cx = get_pos_x()
    cy = get_pos_y()
    dx = (tx - cx) % SIZE
    if dx > HALF:
        for k in range(SIZE - dx):
            move(West)
    elif dx > 0:
        for k in range(dx):
            move(East)
    dy = (ty - cy) % SIZE
    if dy > HALF:
        for k in range(SIZE - dy):
            move(South)
    elif dy > 0:
        for k in range(dy):
            move(North)

def mega_ready():
    x = get_pos_x()
    y = get_pos_y()
    if x == 0:
        if measure() == measure(West):
            return True
    elif x == SZ1:
        if measure() == measure(East):
            return True
    elif y == 0:
        if measure() == measure(South):
            return True
    elif y == SZ1:
        if measure() == measure(North):
            return True
    return False

# Till all tiles
gn = True
for i in range(SIZE):
    for j in range(SIZE):
        if get_ground_type() != Grounds.Soil:
            till()
        if j < SZ1:
            if gn:
                move(North)
            else:
                move(South)
    if i < SZ1:
        move(East)
    gn = not gn

while num_items(Items.Pumpkin) < TARGET:
    # Phase 1: Plant all tiles
    gn = True
    for i in range(SIZE):
        if gn:
            plant(Entities.Pumpkin)
            for j in range(SZ1):
                move(North)
                plant(Entities.Pumpkin)
        else:
            plant(Entities.Pumpkin)
            for j in range(SZ1):
                move(South)
                plant(Entities.Pumpkin)
        if i < SZ1:
            move(East)
        gn = not gn

    # Align Phase 2 to Phase 1 start position
    move(East)

    # Phase 2: Scan + replant dead + conditional water
    chk_x = []
    chk_y = []
    gn = True
    for i in range(SIZE):
        if gn:
            if can_harvest():
                pass
            else:
                plant(Entities.Pumpkin)
                if get_water() < WTHRESH:
                    use_item(Items.Water, 4)
                chk_x.append(get_pos_x())
                chk_y.append(get_pos_y())
            for j in range(SZ1):
                move(North)
                if can_harvest():
                    pass
                else:
                    plant(Entities.Pumpkin)
                    if get_water() < WTHRESH:
                        use_item(Items.Water, 4)
                    chk_x.append(get_pos_x())
                    chk_y.append(get_pos_y())
        else:
            if can_harvest():
                pass
            else:
                plant(Entities.Pumpkin)
                if get_water() < WTHRESH:
                    use_item(Items.Water, 4)
                chk_x.append(get_pos_x())
                chk_y.append(get_pos_y())
            for j in range(SZ1):
                move(South)
                if can_harvest():
                    pass
                else:
                    plant(Entities.Pumpkin)
                    if get_water() < WTHRESH:
                        use_item(Items.Water, 4)
                    chk_x.append(get_pos_x())
                    chk_y.append(get_pos_y())
        if i < SZ1:
            move(East)
        gn = not gn

    # Phase 3: Targeted replant with fertilizer force-growth + measure early harvest
    # Use fertilizer to instantly mature replanted tiles, eliminating multi-pass loops.
    # Use measure() at grid edges to detect mega completion and harvest early.
    idx = 0
    n = len(chk_x)
    while idx < n:
        goto(chk_x[idx], chk_y[idx])
        if can_harvest():
            if mega_ready():
                harvest()
                break
        else:
            if get_entity_type() != Entities.Pumpkin:
                plant(Entities.Pumpkin)
                if get_water() < WTHRESH:
                    use_item(Items.Water, 4)
                # Force-mature with fertilizer if available
                if num_items(Items.Fertilizer) > 0:
                    use_item(Items.Fertilizer)
                    # If pumpkin died from fertilizer maturity, replant + refertilize
                    while get_entity_type() != Entities.Pumpkin:
                        plant(Entities.Pumpkin)
                        if num_items(Items.Fertilizer) > 0:
                            use_item(Items.Fertilizer)
                        else:
                            break
                    if can_harvest():
                        if mega_ready():
                            harvest()
                            break
        idx = idx + 1
    
    harvest()
