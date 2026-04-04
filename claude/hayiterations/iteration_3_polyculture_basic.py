# Iteration 3: Basic Polyculture
# For each tile: check companion, plant bush/tree at companion position,
# harvest with 160x bonus (81,920 hay/harvest vs 512 without).
# Need 100M / 81,920 = ~1,221 polyculture harvests vs ~195K without.
# Skip tiles that want Carrot (needs soil + resources we don't have).
# After harvesting, clean up companion tile (harvest bush/tree, till twice to restore grass).

SIZE = get_world_size()
SZ1 = SIZE - 1
goal = 100000000

def goto(tx, ty):
    cx = get_pos_x()
    cy = get_pos_y()
    # Move east/west
    dx = (tx - cx) % SIZE
    if dx > SIZE // 2:
        for k in range(SIZE - dx):
            move(West)
    else:
        for k in range(dx):
            move(East)
    # Move north/south
    dy = (ty - cy) % SIZE
    if dy > SIZE // 2:
        for k in range(SIZE - dy):
            move(South)
    else:
        for k in range(dy):
            move(North)

while num_items(Items.Hay) < goal:
    # Sweep all tiles in serpentine order
    going_north = True
    for i in range(SIZE):
        for j in range(SIZE):
            # Try polyculture on this tile
            if can_harvest():
                comp = get_companion()
                if comp != None:
                    ptype = comp[0]
                    pos = comp[1]
                    px = pos[0]
                    py = pos[1]
                    # Only do polyculture for Bush or Tree (free to plant on grassland)
                    if ptype == Entities.Bush or ptype == Entities.Tree:
                        # Save current position
                        sx = get_pos_x()
                        sy = get_pos_y()
                        # Go plant companion
                        goto(px, py)
                        plant(ptype)
                        # Go back and harvest with bonus
                        goto(sx, sy)
                        harvest()
                        # Clean up: go to companion tile, harvest it, restore grass
                        goto(px, py)
                        harvest()
                        # till twice to restore grassland with grass
                        till()
                        till()
                        # Return to sweep position
                        goto(sx, sy)
                    else:
                        # Carrot companion -- just harvest without bonus
                        harvest()
                else:
                    harvest()
            # Move to next tile
            if j < SZ1:
                if going_north:
                    move(North)
                else:
                    move(South)
        going_north = not going_north
        if i < SZ1:
            move(East)
