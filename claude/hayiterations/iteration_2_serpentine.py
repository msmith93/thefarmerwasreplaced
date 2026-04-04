# Iteration 2: Serpentine + cached SIZE + skip can_harvest after first sweep
# Optimizations:
# 1. Cache get_world_size() to avoid 1-tick call each loop
# 2. Serpentine (boustrophedon) traversal: alternate N/S per column
#    saves 8 wrap-around moves per sweep (1600 ticks)
# 3. After first sweep, skip can_harvest() -- grass regrows in 0.5s
#    and a full sweep takes ~4.5s, so all tiles are ready

SIZE = get_world_size()
SZ1 = SIZE - 1
goal = 100000000

# First sweep: use can_harvest since initial state has random growth
going_north = True
for i in range(SIZE):
    for j in range(SZ1):
        if can_harvest():
            harvest()
        if going_north:
            move(North)
        else:
            move(South)
    if can_harvest():
        harvest()
    going_north = not going_north
    if i < SZ1:
        move(East)

# Subsequent sweeps: skip can_harvest, just harvest every tile
while num_items(Items.Hay) < goal:
    going_north = True
    for i in range(SIZE):
        for j in range(SZ1):
            harvest()
            if going_north:
                move(North)
            else:
                move(South)
        harvest()
        going_north = not going_north
        if i < SZ1:
            move(East)
