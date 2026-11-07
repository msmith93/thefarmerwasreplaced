clear()
world_size = get_world_size()

while True:
	for i in range(world_size):
		if can_harvest():
			harvest()
			if (get_pos_x() + get_pos_y()) % 2:
				plant(Entities.Tree)
				if get_water() < 0.25:
					use_item(Items.Water)

		move(North)
	move(East)
