from mining_utils import dig_to_z, dig_to_ground_type, dig_to_ground_types

world_size = get_world_size()
clear()
jump(Unlocks.Rice)

def plant_rice_col():
	for row in range(get_world_size()):
		dig_to_ground_type(Grounds.Clay)
		plant(Entities.Rice)
		move(North)

def plant_rice():
	while not spawn_drone(plant_rice_col):
		pass
	
	move(East)
	
	while get_pos_x() > 0:
		if spawn_drone(plant_rice_col):
			move(East)

def harvest_rice_col():
	for row in range(get_world_size()):
		harvest()
		dig()
		if get_ground_type() == Grounds.Clay:
			plant(Entities.Rice)
		
		move(North)

def harvest_rice():
	while not spawn_drone(harvest_rice_col):
		pass
	
	move(East)
	
	while get_pos_x() > 0:
		if spawn_drone(harvest_rice_col):
			move(East)
	
def multi_rice_harvest():
	plant_rice()
	while True:
		harvest_rice()
		if get_ground_type() not in {Grounds.Rice_Terrace, Grounds.Dry_Rice_Terrace}:
			break
