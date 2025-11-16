from pumpkin import harvest_pumpkin

world_size = 1

def drone_action_plant_cacti():
	global world_size
	
	for j in range(world_size):
		if get_ground_type() != Grounds.Soil:
			till()
		plant(Entities.Cactus)
		move(North)

def wait_for_drones(drones):
	for drone in drones:
		wait_for(drone)
	
def plant_cacti():
	global world_size
	
	# Assume we're at the origin
	drones = []
	
	for i in range(world_size - 1):
		drones.append(spawn_drone(drone_action_plant_cacti))
		move(East)
	drone_action_plant_cacti()
	move(East)
	
	wait_for_drones(drones)

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

def sort_row():
	global world_size
	
	# Assume drone is at the first column
	for i in range(world_size):
		swapped = False
		for j in range(0, world_size - i - 1):
			move_to_x_pos(j)
			if measure() > measure(East):
				swap(East)
				swapped = True
		if not swapped:
			break

def sort_col():
	global world_size
	
	# Assume drone is at first row
	for i in range(world_size):
		swapped = False
		for j in range(0, world_size - i - 1):
			move_to_y_pos(j)
			if measure() > measure(North):
				swap(North)
				swapped = True
		if not swapped:
			break

def sort_columns():
	global world_size
	
	# Assume we're at the origin
	drones = []
	
	for i in range(world_size - 1):
		drones.append(spawn_drone(sort_col))
		move(East)

	sort_col()
	move(East) 
	wait_for_drones(drones)
	
def sort_rows():
	global world_size
	
	# Assume we're at the origin
	drones = []
	
	for i in range(world_size - 1):
		drones.append(spawn_drone(sort_row))
		move(North)

	sort_row()
	move(North) 
	wait_for_drones(drones)

def harvest_cacti(num_cacti):
	global world_size
	clear()
	original_world_size = get_world_size()
	set_world_size(max_drones())

	world_size = get_world_size()

	curr_pumpkin = num_items(Items.Pumpkin)
	cacti_harvested_each_loop = (world_size * world_size) ** 2 * (2 ** (num_unlocked(Unlocks.Cactus) - 1))

	needed_loops = (num_cacti + cacti_harvested_each_loop - 1) // cacti_harvested_each_loop
	# needed loops: number of loops
	cactus_planted_per_loop = world_size * world_size # cactus / loop
	needed_cactus_planted = cactus_planted_per_loop * needed_loops # cactus planted total
	needed_pumpkin = needed_cactus_planted * get_cost(Entities.Cactus)[Items.Pumpkin]
	if curr_pumpkin < needed_pumpkin:
		harvest_pumpkin(needed_pumpkin - curr_pumpkin)

	ending_cacti = num_items(Items.Cactus) + num_cacti
	
	while num_items(Items.Cactus) < ending_cacti:
		plant_cacti()
		sort_columns()
		sort_rows()
		for i in range(5):
			do_a_flip()
		harvest()
	
	set_world_size(original_world_size)