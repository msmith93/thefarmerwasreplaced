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

def harvest_carrot(target_carrot):
	global world_size

	world_size = get_world_size()

	cost = get_cost(Entities.Carrot)
	harvest_wood(target_carrot * cost[Items.Wood] + cost[Items.Wood])
	harvest_hay(target_carrot * cost[Items.Hay] + cost[Items.Hay])

	if num_unlocked(Unlocks.Megafarm):
		while num_items(Items.Carrot) < target_carrot:
			for i in range(world_size):
				
				spawn_drone(drone_action)
				while num_drones() >= max_drones():
					pass
			
				move(East)
	else:
		while num_items(Items.Carrot) < target_carrot:
			plant_stuff()
			
			if get_pos_y() == 0 and num_unlocked(Unlocks.Expand) > 1:
				move(East)
			move(North)
