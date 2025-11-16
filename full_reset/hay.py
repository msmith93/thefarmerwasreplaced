world_size = 1
plant_trees = False
watering = False

def plant_stuff():
	global plant_trees
	global watering

	if get_ground_type() != Grounds.Grassland:
		till()

	if can_harvest():
		harvest()
	
	if ((get_pos_x() + get_pos_y()) % 2) and plant_trees:
		plant(Entities.Tree)
		if watering and get_water() < 0.5:
			use_item(Items.Water)

def drone_action():
	global world_size
	
	for j in range(world_size):
		plant_stuff()
		
		move(North)

def harvest_hay(num_hay):
	global world_size
	global plant_trees
	global watering

	starting_hay = num_items(Items.Hay)
	ending_hay = starting_hay + num_hay

	world_size = get_world_size()

	plant_trees = (
		num_unlocked(Unlocks.Polyculture) > 0 and num_unlocked(Unlocks.Trees) > 0
	)
	watering = num_unlocked(Unlocks.Watering) > 0

	if num_unlocked(Unlocks.Megafarm):
		while num_items(Items.Hay) < ending_hay:
			for i in range(world_size):
				
				spawn_drone(drone_action)
				while num_drones() >= max_drones():
					pass
			
				move(East)
	else:

		while num_items(Items.Hay) < ending_hay:
			plant_stuff()

			if get_pos_y() == 0 and num_unlocked(Unlocks.Expand) > 1:
				move(East)
			if num_unlocked(Unlocks.Expand):
				move(North)


