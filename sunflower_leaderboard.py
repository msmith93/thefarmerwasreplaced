world_size = get_world_size()

first_pass = True
HARVEST_DEFAULT = world_size * world_size
harvest_counter = HARVEST_DEFAULT
count = 0

# Comment these out for simulation runs
petal_min = 12
water_threshold = 0.535

def invoke_plant():
	global first_pass
	
	if first_pass:
		till()
	
	plant(Entities.Sunflower)

def move_to_x_pos(x_target):
	global world_size
	
	x_curr = get_pos_x()
	if x_target > x_curr:
		east_moves = x_target - x_curr
	else:
		east_moves = x_target + (world_size - x_curr)
	west_moves = world_size - east_moves
	
	if east_moves > west_moves:
		dir = West
	else:
		dir = East

	for i in range(min(east_moves, west_moves)):
		move(dir)


def move_to_y_pos(y_target):
	global world_size
	
	y_curr = get_pos_y()
	if y_target > y_curr:
		north_moves = y_target - y_curr
	else:
		north_moves = y_target + (world_size - y_curr)
	south_moves = world_size - north_moves
	
	if north_moves > south_moves:
		dir = South
	else:
		dir = North

	for i in range(min(north_moves, south_moves)):
		move(dir)

def go_to_origin():
	move_to_x_pos(0)
	move_to_y_pos(0)

def get_distance(x_curr, y_curr, x_target, y_target):
	if x_target > x_curr:
		east_moves = x_target - x_curr
	else:
		east_moves = x_target + (world_size - x_curr)
	west_moves = world_size - east_moves
	
	x_moves = min(west_moves, east_moves)
	
	if y_target > y_curr:
		north_moves = y_target - y_curr
	else:
		north_moves = y_target + (world_size - y_curr)
	south_moves = world_size - north_moves

	y_moves = min(north_moves, south_moves)
	
	return y_moves + x_moves

def check_sunflower_ready(curr_time, sunflower_plant_time, sunflower_water, distance_away, fertilizer_count):
	time_elapsed_since_planted = curr_time - sunflower_plant_time
	# Takes less than 8.3 seconds for sunflower to grow. Water at level 1 increases growth by 5x
	SUNFLOWER_GROWTH_TIME = 7.5
	sunflower_time_to_grow = SUNFLOWER_GROWTH_TIME
	if sunflower_water != 0:
		sunflower_time_to_grow = SUNFLOWER_GROWTH_TIME / (5 * sunflower_water)

	# Fertilizer reduces growth time by 2 seconds (need to test this in a simulation)
	sunflower_time_to_grow_with_fert = sunflower_time_to_grow - 2 * fertilizer_count

	TIME_TO_MOVE_ONE_STEP = 0.12
	ready_without_fertilizer =  time_elapsed_since_planted + TIME_TO_MOVE_ONE_STEP * distance_away > sunflower_time_to_grow
	ready_with_fertilizer = time_elapsed_since_planted + TIME_TO_MOVE_ONE_STEP * distance_away > sunflower_time_to_grow_with_fert

	return ready_without_fertilizer, ready_with_fertilizer

# Get closest sunflower that is harvestable by the time we get there
def get_closest_sunflower(x_curr, y_curr, sunflowers):
	min_distance = 100
	min_coordinate = (-1, -1)
	backup_coordinate = (-1, -1)

	fertilizer_count = num_items(Items.Fertilizer)

	for sunflower_pos in sunflowers:
		sunflower_plant_time = sunflowers[sunflower_pos]["time"]
		sunflower_water = sunflowers[sunflower_pos]["water"]
		distance = get_distance(x_curr, y_curr, sunflower_pos[0], sunflower_pos[1])

		curr_time = get_time()
		
		if distance < min_distance:
			sunflower_ready, sunflower_ready_with_fertilizer = check_sunflower_ready(curr_time, sunflower_plant_time, sunflower_water, distance, fertilizer_count)
			if not (sunflower_ready or sunflower_ready_with_fertilizer):
				# If we don't have a min yet, set a backup if we never get a min_coordinate
				if min_coordinate == (-1, -1):
					backup_coordinate = sunflower_pos
				else:
					continue
			else:
				requires_fertilizer = not sunflower_ready
				min_distance = distance
				min_coordinate = sunflower_pos
				ret_data = min_coordinate, requires_fertilizer
	
	if min_coordinate == (-1, -1):
		ret_data = backup_coordinate, False

	return ret_data

def run_sunflower():
	global count 
	global petal_min
	global water_threshold
	go_to_origin()
	sf_size_tracker = {}
	world_size = get_world_size()
	for x in range(world_size):
		for y in range(world_size):
			if get_entity_type() != Entities.Sunflower:
				invoke_plant()
			pedal_count = measure()
			
			if pedal_count > petal_min:
				if get_water() < water_threshold:
					use_item(Items.Water)
			
			if pedal_count:
				if pedal_count not in sf_size_tracker:
					sf_size_tracker[pedal_count] = {}

				curr_time = get_time()
				curr_water = get_water()
				sf_size_tracker[pedal_count][(x, y)] = {
					"time": curr_time,
					"water": curr_water
				}
			move(North)
		move(East)
	
	harvest_counter = HARVEST_DEFAULT
	min_pedals = 7
	max_pedals = 15
	for j in range(0, max_pedals - min_pedals + 1):
		i = max_pedals - j
		if i not in sf_size_tracker:
			continue
		targets_dict = sf_size_tracker[i]
		
		while len(targets_dict) > 0:
			# We no longer get the power boost when less than 10 sunflowers remain
			if harvest_counter < 10:
				return False
			
			x_curr = get_pos_x()
			y_curr = get_pos_y()
			(target_x, target_y), requires_fertilizer = get_closest_sunflower(x_curr, y_curr, targets_dict)

			move_to_x_pos(target_x)
			move_to_y_pos(target_y)

			if requires_fertilizer:
				while not can_harvest() and num_items(Items.Fertilizer) > 1:
					use_item(Items.Fertilizer)

			harvest() # sometimes we harvest a sunflower that is not yet fully grown. TODO track these cases?
			harvest_counter -= 1
			if num_items(Items.Power) >= 100000:
				return True

			targets_dict.pop((target_x, target_y))
	
	return False
		

run_sunflower()
first_pass = False
		
while not run_sunflower():
	pass
