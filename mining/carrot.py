clear()

while True:
	for i in range(get_world_size()):

		if get_ground_type() != Grounds.Soil:
			till()
			plant(Entities.Carrot)
		
		if can_harvest():
			harvest()
			if (get_pos_x() + get_pos_y()) % 2:
				plant(Entities.Carrot)
			elif get_pos_x() % 2:
				plant(Entities.Grass)
			else:
				plant(Entities.Tree)
		move(North)
	move(East)
	