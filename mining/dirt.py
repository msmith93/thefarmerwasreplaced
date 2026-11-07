clear()
world_size = get_world_size()

while True:
	for row in range(world_size):
		dig()
		move(North)
	move(East)