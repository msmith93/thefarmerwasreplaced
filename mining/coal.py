from mining_utils import dig_to_z

world_size = get_world_size()

def reset(world_size):
	clear()
	for i in range(world_size / 2):
		move(North)
		move(East)
	
reset(world_size)

def get_coal():
	coal_depth = get_pos_z()
	
	for col in range(world_size):
		for row in range(world_size):
			move(North)
			if not dig_to_z(coal_depth):
				continue
			if get_ground_type() == Grounds.Coal:
				dig()
		move(East)

while True:
	while get_ground_type() not in [Grounds.Coal, Grounds.Clay]:
		dig()
	if get_ground_type() == Grounds.Coal:
		get_coal()

	reset(world_size)