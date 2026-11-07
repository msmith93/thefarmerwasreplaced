from mining_utils import dig_to_z

world_size = get_world_size()

def reset(world_size):
	clear()
	for i in range(world_size / 2):
		move(North)
		move(East)
	
reset(world_size)

def mine_coal(coal_depth):
	for row in range(get_world_size()):
		dig_to_z(coal_depth)
		
		if get_ground_type() == Grounds.Coal:
			dig()
		
		move(North)

def get_coal():
	coal_depth = get_pos_z()
	
	for col in range(world_size):
		while num_drones() >= max_drones():
			pass
		spawn_drone(mine_coal, coal_depth)
		move(East)

while True:
	while get_ground_type() != Grounds.Coal:
		dig()
		
	get_coal()
