clear()

def plant_something():
	if (get_pos_x() + get_pos_y()) % 2:
		plant(Entities.Carrot)
	elif get_pos_x() % 2:
		plant(Entities.Grass)
	else:
		plant(Entities.Tree)
		if get_water() < 0.25:
			use_item(Items.Water)

while True:
	for i in range(get_world_size()):
		if get_ground_type() != Grounds.Soil:
			till()
			plant_something()
		
		if can_harvest():
			harvest()
			plant_something()

		move(North)
	move(East)
	