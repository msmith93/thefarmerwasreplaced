curr_x = 0
curr_y = 0
world_size = get_world_size()
target_num = 100000

companion_mapping = {}
tree_mapping = {}

def track_companion():
	global companion_mapping
	global hay_mapping
	global curr_x
	global curr_y
	
	target_entity, (target_x, target_y) = get_companion()
	if not tree_tile(target_x, target_y) and (target_x, target_y) not in companion_mapping:
		companion_mapping[(target_x, target_y)] = target_entity
		tree_mapping[(curr_x, curr_y)] = (target_x, target_y)
		# TODO only water the plant if we are planting a tree that will have a companion return True

def tree_tile(curr_x, curr_y):
	return curr_x % 2 == curr_y % 2

while True:
	if tree_tile(curr_x, curr_y):
		if (curr_x, curr_y) in tree_mapping:
			while not can_harvest():
				use_item(Items.Fertilizer)
		harvest()
		plant(Entities.Tree)
		if (curr_x, curr_y) in tree_mapping: # Had a companion that was already planted
			companion_pos = tree_mapping[(curr_x, curr_y)]
			tree_mapping.pop((curr_x, curr_y))
			companion_mapping.pop(companion_pos)
				
		track_companion()
		if get_water() < 0.13:
			use_item(Items.Water)
	elif (curr_x, curr_y) in companion_mapping:
		target_entity = companion_mapping[(curr_x, curr_y)]
		curr_entity = get_entity_type()
		harvest()
		if target_entity == Entities.Grass:
			if get_ground_type() != Grounds.Grassland:
				# Grass that needs tilling. Grass never needs any planting though.
				till()
		elif target_entity == Entities.Carrot and get_ground_type() != Grounds.Soil:
			# Carrot that needs tilling
			till()
			plant(target_entity)
		else:
			# Not grass, but does not need any tilling.
			plant(target_entity)
	else:
		# not a tree tile, but is not a companion
		harvest()
		plant(Entities.Bush)
		
	if num_items(Items.Wood) >= target_num:
		break

	move(North)
	curr_y += 1
	if curr_y == world_size:
		curr_y = 0
		move(East)
		curr_x += 1
		if curr_x == world_size:
			curr_x = 0
