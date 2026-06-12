# Iteration 2: early_peek
# v2 (saturate_scan) plus: during the plant pass, peek West at the previous
# column and fix deaths that already resolved (1-tick measure, ~37% of deaths
# handled one stage early). Till only on the first cycle; water before plant.
clear()
SIZE = get_world_size()
SZ1 = SIZE - 1
HALF = SIZE // 2
TARGET = 10000000

def goto(tx, ty):
    dx = (tx - get_pos_x()) % SIZE
    if dx > HALF:
        for k in range(SIZE - dx):
            move(West)
    elif dx > 0:
        for k in range(dx):
            move(East)
    dy = (ty - get_pos_y()) % SIZE
    if dy > HALF:
        for k in range(SIZE - dy):
            move(South)
    elif dy > 0:
        for k in range(dy):
            move(North)

def water_up():
    if get_water() < 0.4:
        a = num_items(Items.Water)
        if a >= 4:
            use_item(Items.Water, 4)
        elif a >= 1:
            use_item(Items.Water, 1)

def fix_camp():
    # at a dead/growing tile: ensure planted, force-mature with fertilizer
    g = 0
    while not can_harvest():
        if get_entity_type() != Entities.Pumpkin:
            plant(Entities.Pumpkin)
            water_up()
        if num_items(Items.Fertilizer) >= 1:
            use_item(Items.Fertilizer)
        g = g + 1
        if g > 5000:
            break

# watched replant positions (rebuilt every cycle)
wx = []
wy = []

def check_side(d, back):
    # neighbor measure None means dead (field is fully planted)
    if measure(d) == None:
        move(d)
        if get_entity_type() != Entities.Pumpkin:
            plant(Entities.Pumpkin)
            water_up()
            wx.append(get_pos_x())
            wy.append(get_pos_y())
        move(back)

def fix_west_dead():
    # during plant pass: previous column's same-row tile is dead; fix in place
    move(West)
    if get_entity_type() != Entities.Pumpkin:
        plant(Entities.Pumpkin)
        water_up()
    move(East)

def scan_round():
    # scan 3 columns (entry column, +3, +6), checking own + West + East
    vdir = North
    vopp = South
    for c in range(3):
        for r in range(SIZE):
            if not can_harvest():
                if get_entity_type() != Entities.Pumpkin:
                    plant(Entities.Pumpkin)
                    water_up()
                    wx.append(get_pos_x())
                    wy.append(get_pos_y())
            check_side(West, East)
            check_side(East, West)
            if r < SZ1:
                move(vdir)
        if c < 2:
            move(East)
            move(East)
            move(East)
        t = vdir
        vdir = vopp
        vopp = t

def merge_poll():
    # stand on absolute top row; seam-crossing ID equality proves 8x8 mega
    goto(get_pos_x(), SZ1)
    if not can_harvest():
        fix_camp()
    g = 0
    while g < 650:
        a = measure()
        if a != None:
            if a == measure(North):
                return True
        g = g + 1
    return False

first = True
while num_items(Items.Pumpkin) < TARGET:
    # Pass 1: snake plant + deep watering + West peek at previous column
    vdir = North
    vopp = South
    for i in range(SIZE):
        for j in range(SZ1):
            if first:
                if get_ground_type() != Grounds.Soil:
                    till()
            water_up()
            plant(Entities.Pumpkin)
            if i > 0:
                if measure(West) == None:
                    fix_west_dead()
            move(vdir)
        if first:
            if get_ground_type() != Grounds.Soil:
                till()
        water_up()
        plant(Entities.Pumpkin)
        if i > 0:
            if measure(West) == None:
                fix_west_dead()
        if i < SZ1:
            move(East)
        t = vdir
        vdir = vopp
        vopp = t
    first = False
    # Scan: catch remaining deaths, record replants
    wx = []
    wy = []
    move(East)
    move(East)
    scan_round()
    # Targeted second pass: camp watched tiles that aren't mature yet
    for i in range(len(wx)):
        goto(wx[i], wy[i])
        if not can_harvest():
            fix_camp()
    # Poll seam for full-field merge; rescan if stragglers remain
    while not merge_poll():
        wx = []
        wy = []
        move(East)
        move(East)
        scan_round()
        for i in range(len(wx)):
            goto(wx[i], wy[i])
            if not can_harvest():
                fix_camp()
    harvest()

quick_print("FINAL_TIME: ", get_time())
