clear()

set_world_size(max_drones() - 1)

hats = [Hats.Green_Hat, Hats.Purple_Hat]

world_size = get_world_size()

def drone_action_plant_cacti():
	global world_size
	
	change_hat(hats[get_pos_x() % 2])
	
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
	
	for i in range(world_size):
		drones.append(spawn_drone(drone_action_plant_cacti))
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
	
	change_hat(hats[get_pos_y() % 2])
	
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
	
	change_hat(hats[get_pos_x() % 2])
	
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
	
	for i in range(world_size):
		drones.append(spawn_drone(sort_col))
		move(East)
	
	wait_for_drones(drones)
	
def sort_rows():
	global world_size
	
	# Assume we're at the origin
	drones = []
	
	for i in range(world_size):
		drones.append(spawn_drone(sort_row))
		move(North)
	
	wait_for_drones(drones)

while True:
	plant_cacti()
	sort_columns()
	sort_rows()
	harvest()