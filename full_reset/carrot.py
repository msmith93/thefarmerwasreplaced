from wood import harvest_wood
from hay import harvest_hay

world_size = 1

# def plant_stuff():
# 	if get_ground_type() != Grounds.Soil:
# 		till()
	
# 	if get_entity_type() != Entities.Carrot:
# 		harvest()
# 		plant(Entities.Carrot)
# 	elif can_harvest():
# 		harvest()
		
# 	plant(Entities.Carrot)

def plant_stuff():
	if can_harvest():
		harvest()

	if ((get_pos_x() + get_pos_y()) % 2):
		if get_ground_type() != Grounds.Soil:
			till()
		plant(Entities.Carrot)
	else:
		if get_ground_type() != Grounds.Grassland:
			till()

def drone_action():
	global world_size
	
	for j in range(world_size):
		plant_stuff()
		
		move(North)

def harvest_carrot(num_carrot):
	global world_size

	world_size = get_world_size()
	curr_wood = num_items(Items.Wood)
	cost_carrot = 1
	needed_wood = cost_carrot * num_carrot + get_cost(Entities.Carrot)[Items.Wood]
	if curr_wood < needed_wood:
		harvest_wood(needed_wood - curr_wood)
	
	curr_hay = num_items(Items.Hay)
	cost_hay = 1
	needed_hay = cost_hay * num_carrot + get_cost(Entities.Carrot)[Items.Hay]
	if curr_hay < needed_hay:
		harvest_hay(needed_hay - curr_hay)

	ending_carrot = num_items(Items.Carrot) + num_carrot
	
	if num_unlocked(Unlocks.Megafarm):
		while num_items(Items.Carrot) < ending_carrot:
			for i in range(world_size):
				
				spawn_drone(drone_action)
				while num_drones() >= max_drones():
					pass
			
				move(East)
	else:
		while num_items(Items.Carrot) < ending_carrot:
			plant_stuff()
			
			if get_pos_y() == 0 and num_unlocked(Unlocks.Expand) > 1:
				move(East)
			move(North)
