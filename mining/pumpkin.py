clear()
world_size = get_world_size()

while True:
	num_times_planting_new_pumpkin = 0
	for col in range(world_size):
		for row in range(world_size):
			if get_ground_type() != Grounds.Soil:
				till()
			if get_entity_type() != Entities.Pumpkin:
				plant(Entities.Pumpkin)
				num_times_planting_new_pumpkin += 1
			move(North)
		move(East)
	if num_times_planting_new_pumpkin == 0:
		harvest()