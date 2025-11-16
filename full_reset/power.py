from carrot import harvest_carrot

# Comment these out for simulation runs
petal_min = 12
water_threshold = 0.535
initial_wait = 8

world_size = 1
curr_petal_gathering = 15

def plant_and_use_water():
	if get_ground_type() != Grounds.Soil:
		till()
	
	if get_entity_type() != Entities.Sunflower:
		harvest()

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

def run_sunflower(harvest_default, watering, fert_unlocked):
	global petal_min
	global water_threshold
	global initial_wait

	go_to_origin()
	sf_size_tracker = {}
	world_size = get_world_size()
	
	for x in range(world_size):
		for y in range(world_size):
			if get_entity_type() != Entities.Sunflower:
				plant_and_use_water()
			pedal_count = measure()
			
			if watering and pedal_count > petal_min:
				if get_water() < water_threshold:
					use_item(Items.Water)

			if pedal_count:
				if pedal_count not in sf_size_tracker:
					sf_size_tracker[pedal_count] = []

				sf_size_tracker[pedal_count].append((x, y))
			move(North)
		move(East)

	before_time = get_time()
	
	goal = before_time + initial_wait

	# Give the flowers a bit o time to grow
	while get_time() < goal:
		pass

	harvest_counter = harvest_default
	min_pedals = 7
	max_pedals = 15

	for i in range(max_pedals, min_pedals - 1, -1):
		if i not in sf_size_tracker:
			continue
		targets_list = sf_size_tracker[i]
		
		for target in targets_list:
			# We no longer get the power boost when less than 10 sunflowers remain
			if harvest_counter < 10:
				return False
			
			move_to_x_pos(target[0])
			move_to_y_pos(target[1])
			if fert_unlocked:
				while not can_harvest() and num_items(Items.Fertilizer) > 1:
					use_item(Items.Fertilizer)

			harvest() # sometimes we harvest a sunflower that is not yet fully grown. TODO track these cases?
			harvest_counter -= 1
	
	return False

def plant_col():
	global world_size
	
	for j in range(world_size):
		if get_ground_type() != Grounds.Soil:
			till()
		plant(Entities.Sunflower)
		if get_water() < 0.5:
			use_item(Items.Water)
		move(North)

def plant_crop():
	global world_size
	global initial_wait
	
	# Assume we're at the origin
	drones = []
		
	for i in range(world_size - 1):
		drones.append(spawn_drone(plant_col))
		move(East)
	
	plant_col()
	move(East)
	
	before_time = get_time()
	goal = before_time + initial_wait
	# Give the flowers a bit o time to grow
	while get_time() < goal:
		pass

	wait_for_drones(drones)

def run_drone():
	global curr_petal_gathering
	global world_size
	
	for j in range(world_size):
		if measure() == curr_petal_gathering:
			while not can_harvest():
				use_item(Items.Fertilizer)
			harvest()
		move(North)

def wait_for_drones(drones):
	for drone in drones:
		wait_for(drone)

def run_sunflower_multi():
	global world_size
	global curr_petal_gathering

	min_petals = 7
	max_petals = 15
	
	plant_crop()
	
	for petal_count in range(max_petals, min_petals - 1, -1):
		curr_petal_gathering = petal_count
		 
		# Assume we're at the origin
		drones = []
		
		for i in range(world_size - 1):
			drones.append(spawn_drone(run_drone))
			move(East)
		
		run_drone()
		move(East)
		wait_for_drones(drones)

def harvest_power(num_power):
	global world_size

	curr_carrots = num_items(Items.Carrot)
	needed_carrots = get_cost(Entities.Sunflower)[Items.Carrot] * num_power
	if curr_carrots < needed_carrots:
		harvest_carrot(needed_carrots - curr_carrots)

	ending_power = num_items(Items.Power) + num_power

	if num_unlocked(Unlocks.Megafarm) < 2:
		world_size = get_world_size()
		harvest_default = world_size * world_size
		
		watering = num_unlocked(Unlocks.Watering) > 0
		fert_unlocked = num_unlocked(Unlocks.Fertilizer) > 0

		while num_items(Items.Power) < ending_power:
			run_sunflower(harvest_default, watering, fert_unlocked)
	else:
		orig_world_size = get_world_size()
		set_world_size(max_drones())
		world_size = get_world_size()

		while num_items(Items.Power) < ending_power:
			run_sunflower_multi()
		
		set_world_size(orig_world_size)
