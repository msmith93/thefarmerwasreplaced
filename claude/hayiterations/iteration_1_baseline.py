# Iteration 1: Baseline
# Direct copy of hay_basic.py -- simple sweep with can_harvest check.
# No watering, no polyculture, no routing optimization.

while num_items(Items.Hay) < 100000000:
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            move(North)
        move(East)
