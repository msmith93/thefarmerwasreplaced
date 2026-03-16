clear()

SIZE = get_world_size()

for i in range(SIZE):
    for j in range(SIZE):
        if get_ground_type() != Grounds.Soil:
            till()
        if get_entity_type() == None:
            plant(Entities.Sunflower)
        use_item(Items.Water, 4)
        move(North)
    move(East)

while num_items(Items.Power) < 10000:
    for i in range(SIZE):
        for j in range(SIZE):
            if can_harvest():
                harvest()
                plant(Entities.Sunflower)
            elif get_entity_type() == None:
                plant(Entities.Sunflower)
            use_item(Items.Water, 4)
            move(North)
        move(East)
