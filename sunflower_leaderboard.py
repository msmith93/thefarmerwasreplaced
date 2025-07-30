world_size = get_world_size()

first_pass = True
HARVEST_DEFAULT = world_size * world_size
harvest_counter = HARVEST_DEFAULT
count = 0

# Comment these out for simulation runs
petal_min = 12
water_threshold = 0.535

def plant_and_use_water():
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

def check_sunflower_ready(curr_time, sunflower_plant_time, sunflower_water, fertilizer_count):
	time_elapsed_since_planted = curr_time - sunflower_plant_time
	# Takes less than 8.3 seconds for sunflower to grow. Water at level 1 increases growth by 5x
	# Growth speed increases linearly with water
	# -4 * 7 / 5 = -5.6 (save ticks by not doing math each time)
	sunflower_time_to_grow = -5.6 * sunflower_water + 7

	# Fertilizer reduces growth time by 2 seconds (need to test this in a simulation)
	sunflower_time_to_grow_with_fert = sunflower_time_to_grow - 2 * fertilizer_count

	ready_without_fertilizer =  time_elapsed_since_planted > sunflower_time_to_grow
	ready_with_fertilizer = time_elapsed_since_planted > sunflower_time_to_grow_with_fert

	return ready_without_fertilizer, ready_with_fertilizer

def run_sunflower():
	global count 
	global petal_min
	global water_threshold
	go_to_origin()
	sf_size_tracker = {}
	world_size = get_world_size()
	before_time = get_time()
	for x in range(world_size):
		for y in range(world_size):
			if get_entity_type() != Entities.Sunflower:
				plant_and_use_water()
			pedal_count = measure()
			
			if pedal_count > petal_min and get_water() < water_threshold:
				use_item(Items.Water)
			
			
			if pedal_count not in sf_size_tracker:
				sf_size_tracker[pedal_count] = {}

			#curr_time = get_time()
			#curr_water = get_water()
			sf_size_tracker[pedal_count][(x, y)] = {
				"time": 0,
				#"water": curr_water
			}
			move(North)
		move(East)
	
	after_time = get_time()

	while after_time - before_time < 5:
		do_a_flip()
		after_time = get_time()
	
	harvest_counter = HARVEST_DEFAULT
	min_pedals = 7
	max_pedals = 15
	for j in range(0, max_pedals - min_pedals + 1):
		i = max_pedals - j
		if i not in sf_size_tracker:
			continue
		sunflowers = sf_size_tracker[i]
		
		#curr_time = get_time()

		for sunflower_pos in sunflowers:
			fertilizer_count = num_items(Items.Fertilizer)

			# We no longer get the power boost when less than 10 sunflowers remain
			if harvest_counter < 10:
				return False
			
			#sunflower_plant_time = sunflowers[sunflower_pos]["time"]
			#sunflower_water = sunflowers[sunflower_pos]["water"]
			
			#sunflower_ready, sunflower_ready_with_fertilizer = check_sunflower_ready(curr_time, sunflower_plant_time, sunflower_water, fertilizer_count)
			
			move_to_x_pos(sunflower_pos[0])
			move_to_y_pos(sunflower_pos[1])

			if fertilizer_count > 4:
			#if sunflower_ready_with_fertilizer and not sunflower_ready:
				while not can_harvest():
					use_item(Items.Fertilizer)
			
			
			harvest() # sometimes we harvest a sunflower that is not yet fully grown. TODO track these cases?
			harvest_counter -= 1
		if num_items(Items.Power) >= 100000:
			return True
	
	return False
		

run_sunflower()
first_pass = False
		
while not run_sunflower():
	pass
