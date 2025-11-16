plant_trees = False
watering = False
world_size = 1

def plant_stuff():
	global plant_trees
	global watering

	if can_harvest() or get_entity_type() not in [Entities.Bush, Entities.Tree]:
		harvest()
		if plant_trees and ((get_pos_x() + get_pos_y()) % 2):
			plant(Entities.Tree)
			if watering and get_water() < 0.5:
				use_item(Items.Water)
		else:
			plant(Entities.Bush)

def drone_action():
	global world_size
	
	for j in range(world_size):
		plant_stuff()
		
		move(North)

def harvest_wood(num_wood):
	global world_size
	global plant_trees
	global watering

	world_size = get_world_size()
	ending_wood = num_items(Items.Wood) + num_wood

	plant_trees = num_unlocked(Unlocks.Trees) > 0
	watering = num_unlocked(Unlocks.Watering) > 0

	if num_unlocked(Unlocks.Megafarm):
		while num_items(Items.Wood) < ending_wood:
			for i in range(world_size):
				
				spawn_drone(drone_action)
				while num_drones() >= max_drones():
					pass
			
				move(East)
	else:
		while num_items(Items.Wood) < ending_wood:
			plant_stuff()
			
			if get_pos_y() == 0 and num_unlocked(Unlocks.Expand) > 1:
				move(East)
			move(North)
	

