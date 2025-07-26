def move_to_x_pos(x_target):
	x_curr = get_pos_x()
	moves_needed = x_target - x_curr
	if moves_needed > 0:
		dir = East
	else:
		dir = West
	for i in range(abs(moves_needed)):
		move(dir)

def move_to_y_pos(y_target):
	y_curr = get_pos_y()
	moves_needed = y_target - y_curr
	if moves_needed > 0:
		dir = North
	else:
		dir = South
	for i in range(abs(moves_needed)):
		move(dir)

def go_to_origin():
	move_to_x_pos(0)
	move_to_y_pos(0)


# {
# 	(companion_pos_x, companion_pos_y): compantion_entity_type
# }
companion_mapping = {}

# {
# 	(hay_pos_x, hay_pos_y): (companion_pos_x, companion_pos_y)
# }
hay_mapping = {}
# {
# 	(companion_pos_x, companion_pos_y): (hay_pos_x, hay_pos_y)
# }
companion_to_hay_mapping = {}

# Resolve a conflict when we are trying to track a companion entity but that
# position is already filled in the companion mapping
def resolveConflict(x_curr, y_curr, target_x, target_y):
	global companion_mapping
	global hay_mapping
	global companion_to_hay_mapping

	# If there is hay that is already being tracked (maybe it already has a companion)
	if (target_x, target_y) in hay_mapping:
		companion_pos = hay_mapping[(target_x, target_y)]
		# If the companion is not in the companion mapping, that means the companion has
		# already been planted. We can harvest this hay
		if companion_pos not in companion_mapping:
			move_to_x_pos(target_x)
			move_to_y_pos(target_y)
			do_harvest()
		else:
			resolveConflict(target_x, target_y, companion_pos[0], companion_pos[1])

	# Plant the conflicting companion, move to its parent hay, harvest that, and 
	# now the position is free to be added to the companion mapping
	conflicting_companion = companion_mapping[(target_x, target_y)]
	move_to_x_pos(target_x)
	move_to_y_pos(target_y)

	if get_ground_type() == Grounds.Grassland:
		if conflicting_companion not in [Entities.Bush, Entities.Tree]:
			till()

	plant(conflicting_companion)
	hay_pos = companion_to_hay_mapping[(target_x, target_y)]
	
	move_to_x_pos(hay_pos[0])
	move_to_y_pos(hay_pos[1])
	do_harvest()

	hay_mapping.pop(hay_pos)
	companion_mapping.pop((target_x, target_y))
	companion_to_hay_mapping.pop((target_x, target_y))
	
	# Return to original position
	move_to_x_pos(x_curr)
	move_to_y_pos(y_curr)


def track_companion(x_curr, y_curr):
	global companion_mapping
	global hay_mapping
	global companion_to_hay_mapping
	
	target_entity, (target_x, target_y) = get_companion()

	while target_entity == Entities.Carrot and num_items(Items.Wood) < 1:
		harvest()
		target_entity, (target_x, target_y) = get_companion()

	if (target_x, target_y) in companion_mapping:
		resolveConflict(x_curr, y_curr, target_x, target_y)	
	
	companion_mapping[(target_x, target_y)] = target_entity
	companion_to_hay_mapping[(target_x, target_y)] = (x_curr, y_curr)
	hay_mapping[(x_curr, y_curr)] = (target_x, target_y)

def do_harvest():
	prev_hay = num_items(Items.Hay)
	harvest()
	after_hay = num_items(Items.Hay)

	if after_hay != prev_hay and (after_hay - prev_hay < 50):
		pass

while True:
	if num_items(Items.Hay) >= 100000:
		break
	
	# TODO: Don't run this every loop. Track x and y separately
	x_curr = get_pos_x()
	y_curr = get_pos_y()
	
	if get_entity_type() == Entities.Grass:
		if can_harvest():
			do_harvest()

		if (x_curr, y_curr) in hay_mapping: # Had a companion that was already planted
			companion_pos = hay_mapping[(x_curr, y_curr)]
			hay_mapping.pop((x_curr, y_curr))
			companion_mapping.pop(companion_pos)
			companion_to_hay_mapping.pop(companion_pos)
		
		if (x_curr, y_curr) in companion_mapping: # Plant a companion
			target_entity = companion_mapping[(x_curr, y_curr)]
			if target_entity not in [Entities.Bush, Entities.Tree]:
				till()
			plant(target_entity)
		else: # Only when current position is growing grass
			track_companion(x_curr, y_curr) 
		
	else: # Entity is not grass AKA it is / was a companion
		if (x_curr, y_curr) not in companion_mapping: # Companion has served its purpose
			# Reset land back to grassland
			if get_ground_type() != Grounds.Grassland:
				till()
			else:
				do_harvest()
		
			track_companion(x_curr, y_curr)


	if y_curr == get_world_size() - 1:
		move(East)
	move(North)
	
