while True:
	for i in range(get_world_size()):
		if can_harvest():
			harvest()
		move(North)
	move(East)
