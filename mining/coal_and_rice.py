from mining_utils import dig_to_z, dig_to_ground_types, goto
from multi_rice import multi_rice_harvest
from multi_ore_simple import multi_ore_mining

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

def reset(world_size):
	for i in range(world_size / 2):
		move(North)
		move(East)

def get_coal():
	coal_depth = get_pos_z()
	
	reset(world_size)
	
	for col in range(world_size):
		while num_drones() >= max_drones():
			pass
		spawn_drone(mine_coal, coal_depth)
		move(East)

while True:
	dig_to_ground_types({Grounds.Coal, Grounds.Clay, Grounds.Rock})
	
	ground_type = get_ground_type()
	if ground_type == Grounds.Coal:
		get_coal()
	elif ground_type == Grounds.Clay:
		goto(0,0)
		multi_rice_harvest()
	elif ground_type == Grounds.Rock:
		multi_ore_mining()
	