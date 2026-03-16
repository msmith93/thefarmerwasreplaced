clear()

SIZE = get_world_size()
TARGET = 10000

# Till all tiles once
for i in range(SIZE):
    for j in range(SIZE):
        till()
        move(North)
    move(East)

# Main batch loop
while num_items(Items.Power) < TARGET:
    # Combined plant + measure + water pass
    # Store petals in a flat grid: petal_at[x * SIZE + y]
    petal_at = []
    total = 0
    max_p = 0
    for x in range(SIZE):
        for y in range(SIZE):
            if get_entity_type() == None:
                plant(Entities.Sunflower)
            use_item(Items.Water, 4)
            p = measure()
            if p != None:
                petal_at.append(p)
                total = total + 1
                if p > max_p:
                    max_p = p
            else:
                petal_at.append(0)
            move(North)
        move(East)

    # Harvest in descending petal order using serpentine passes
    harvested = 0
    target_p = max_p
    while target_p >= 7 and num_items(Items.Power) < TARGET:
        for x in range(SIZE):
            for y in range(SIZE):
                if total - harvested > 10:
                    if petal_at[x * SIZE + y] == target_p:
                        if can_harvest():
                            harvest()
                            harvested = harvested + 1
                            if num_items(Items.Power) >= TARGET:
                                target_p = -1
                move(North)
            move(East)
        target_p = target_p - 1
