ALL_DIRECTIONS = [North, South, East, West]

def opposite_direction(direction):
	if direction == North:
		return South
	elif direction == East:
		return West
	elif direction == South:
		return North
	elif direction == West:
		return East

def explore_option_iterative(start_direction):
	global ALL_DIRECTIONS
	if not move(start_direction):
		return False
	
	path_stack = [(start_direction, 0)]
	
	while path_stack and num_items(Items.Gold) < 9863168:
		if get_entity_type() == Entities.Treasure:
			harvest()
			start_maze()
			return True
			
		last_move_direction, next_dir_index = path_stack[-1]
		
		while next_dir_index < len(ALL_DIRECTIONS):
			explore_direction = ALL_DIRECTIONS[next_dir_index]
			
			path_stack[-1] = (last_move_direction, next_dir_index + 1)

			if opposite_direction(explore_direction) != last_move_direction:
				
				if move(explore_direction):
					path_stack.append((explore_direction, 0))
					break
			
			next_dir_index += 1
		
		if next_dir_index == len(ALL_DIRECTIONS):
			path_stack.pop()
			
			move(opposite_direction(last_move_direction))
			
	move(opposite_direction(start_direction))
	return False

def start_maze():
	plant(Entities.Bush)
	substance = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
	use_item(Items.Weird_Substance, substance)

def search():
	global drone_id
	global ALL_DIRECTIONS

	for _ in range(drone_id):
		do_a_flip()
		
	if drone_id % 2:
		ALL_DIRECTIONS = ALL_DIRECTIONS[::-1]
	if drone_id % 3:
		ALL_DIRECTIONS[0], ALL_DIRECTIONS[1] = (ALL_DIRECTIONS[1], ALL_DIRECTIONS[0])
	if drone_id % 5:
		ALL_DIRECTIONS[1], ALL_DIRECTIONS[3] = (ALL_DIRECTIONS[3], ALL_DIRECTIONS[1])
	
	while True:
		for direction in ALL_DIRECTIONS:
			if explore_option_iterative(direction):
				break
		if num_items(Items.Gold) >= 9863168:
			break
drone_id = 0
start_maze()
for i in range(max_drones()):
	drone_id = i
	spawn_drone(search)

drone_id = 0

search()
