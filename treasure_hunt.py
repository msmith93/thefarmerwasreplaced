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

def explore_option(direction):
	if not move(direction):
		return False
	
	if get_entity_type() == Entities.Treasure:
		harvest()
		return True
	
	for explore_direction in ALL_DIRECTIONS:
		if opposite_direction(explore_direction) != direction:
			if explore_option(explore_direction):
				return True
	
	move(opposite_direction(direction))

while True:
	clear()
	change_hat(Hats.Straw_Hat)
	plant(Entities.Bush)
	n_substance = get_world_size() * num_unlocked(Unlocks.Mazes)
	use_item(Items.Weird_Substance, n_substance)


	for direction in ALL_DIRECTIONS:
		if explore_option(direction):
			break
