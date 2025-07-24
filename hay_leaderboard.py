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

companion_mapping = {}
hay_mapping = {}

def resolveConflict(x_curr, y_curr, target_x, target_y, target_entity):
	global companion_mapping
	global hay_mapping

	if (target_x, target_y) in hay_mapping:
		companion_pos = hay_mapping[(target_x, target_y)]
		if companion_pos not in companion_mapping:
			move_to_x_pos(target_x)
			move_to_y_pos(target_y)
		else:
			if (companion_pos[0], companion_pos[1]) in companion_mapping:
				resolveConflict(target_x, target_y, companion_pos[0], companion_pos[1], companion_mapping[companion_pos])
			
			# Plant the companion at the target position and immediately return
			move_to_x_pos(companion_pos[0])
			move_to_y_pos(companion_pos[1])
			plant(companion_mapping[companion_pos])
			move_to_x_pos(target_x)
			move_to_y_pos(target_y)
		
		harvest()
		hay_mapping.pop((target_x, target_y))
		track_companion(x_curr, y_curr)

		move_to_x_pos(x_curr)
		move_to_y_pos(y_curr)

	else:


def track_companion(x_curr, y_curr):
	global companion_mapping
	global hay_mapping
	
	target_entity, (target_x, target_y) = get_companion()

	if target_entity == Entities.Carrot and num_items(Items.Wood) < 1:
		return

	if (target_x, target_y) in companion_mapping:
		resolveConflict(x_curr, y_curr, target_x, target_y, target_entity)	
	
	companion_mapping[(target_x, target_y)] = target_entity
	hay_mapping[(x_curr, y_curr)] = (target_x, target_y)

# Wait for initial grass to grow
while not can_harvest():
	pass

while True:
	if num_items(Items.Hay) >= 100000:
		break
	
	# TODO: Don't run this every loop. Track x and y separately
	x_curr = get_pos_x()
	y_curr = get_pos_y()
	
	if get_entity_type() == Entities.Grass:
		harvest()
		if (x_curr, y_curr) in hay_mapping: # Had a companion that was already planted
			companion_pos = hay_mapping[(x_curr, y_curr)]
			hay_mapping.pop((x_curr, y_curr))
			companion_mapping.pop(companion_pos)
		
		if (x_curr, y_curr) in companion_mapping: # Plant a companion
			target_entity = companion_mapping[(x_curr, y_curr)]
			if target_entity not in [Entities.Bush, Entities.Tree]:
				till()
			plant(target_entity)
		else: # Only when current position is growing grass
			track_companion() 
		
	else: # Entity is not grass AKA it is / was a companion
		if (x_curr, y_curr) not in companion_mapping: # Companion has served its purpose
			# Reset land back to grassland
			if get_ground_type() != Grounds.Grassland:
				till()
			else:
				harvest()
		
			track_companion()


	if y_curr == get_world_size() - 1:
		move(East)
	move(North)
	
