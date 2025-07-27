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
	moves_needed = x_target - x_curr
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
	moves_needed = y_target - y_curr
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
				plant_and_use_water()
			pedal_count = measure()
			
			if pedal_count > petal_min:
				if get_water() < water_threshold:
					use_item(Items.Water)
			
			if pedal_count:
				if pedal_count not in sf_size_tracker:
					sf_size_tracker[pedal_count] = []

				sf_size_tracker[pedal_count].append((x, y))
			move(North)
		move(East)
	
	harvest_counter = HARVEST_DEFAULT
	min_pedals = 7
	max_pedals = 15
	for j in range(0, max_pedals - min_pedals + 1):
		i = max_pedals - j
		if i not in sf_size_tracker:
			continue
		targets_list = sf_size_tracker[i]
		
		for target in targets_list:
			# We no longer get the power boost when less than 10 sunflowers remain
			if harvest_counter < 10:
				return False
			
			move_to_x_pos(target[0])
			move_to_y_pos(target[1])
			while not can_harvest() and num_items(Items.Fertilizer) > 1:
				use_item(Items.Fertilizer)
			if not can_harvest():
				count += 1
			harvest() # sometimes we harvest a sunflower that is not yet fully grown. TODO track these cases?
			harvest_counter -= 1
			if num_items(Items.Power) >= 100000:
				return True
	
	return False
		

run_sunflower()
first_pass = False
		
while not run_sunflower():
	pass
