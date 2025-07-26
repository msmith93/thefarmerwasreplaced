world_size = get_world_size()

min_num_items = 10000
water_threshold = 0.75
mode_interval = 20
pumpkin_fertilizer_needed = 200

def prep_carrot():
	till_all(Entities.Carrot)
	
def run_carrot():
	global world_size
	for col in range(world_size):
		for row in range(world_size):
			if can_harvest():
				harvest()
				plant(Entities.Carrot)
				if get_water() < water_threshold:
					use_item(Items.Water)
			move(North)
		move(East)

def prep_hay():
	clear()
	
def run_hay():
	global world_size
	for col in range(world_size):
		for row in range(world_size):
			if can_harvest():
				harvest()
			move(North)
		move(East)
	
def prep_wood():
	clear()

def run_wood():
	global world_size
	global water_threshold
	
	for col in range(world_size):
		for row in range(world_size):
			if can_harvest():
				harvest()
				if col % 2 == row % 2:
					plant(Entities.Tree)
					if get_water() < water_threshold:
						use_item(Items.Water)
				else:
					plant(Entities.Bush)
			move(North)
		move(East)

def prep_pumpkin():
	till_all(None)

def plant_all(plant_type):
	global world_size
	
	for col in range(world_size):
		for row in range(world_size):
			plant(plant_type)
			move(North)
		move(East)

def till_all(plant_type, water=True):
	global world_size
	
	clear()
	for col in range(world_size):
		for row in range(world_size):
			till()
			if water:
				while get_water() < water_threshold:
					use_item(Items.Water)
			if plant_type:
				plant(plant_type)
			move(North)
		move(East)
		
def fertilize_empties(plant_type):
	global world_size
	
	for col in range(world_size):
		for row in range(world_size):
			while not can_harvest():
				plant(plant_type)
				use_item(Items.Fertilizer)
			move(North)
		move(East)

def run_pumpkin():
	global world_size
	
	plant_all(Entities.Pumpkin)
	fertilize_empties(Entities.Pumpkin)
	harvest()

def move_to_x_pos(x_target):
	x_curr = get_pos_x()
	moves_needed = x_target - x_curr
	if moves_needed > 0:
		dir = East
	else:
		dir = West
	for i in range(abs(moves_needed)):
		if not move(dir):
			hat_flip()

def move_to_y_pos(y_target):
	y_curr = get_pos_y()
	moves_needed = y_target - y_curr
	if moves_needed > 0:
		dir = North
	else:
		dir = South
	for i in range(abs(moves_needed)):
		if not move(dir):
			hat_flip()

def go_to_origin():
	move_to_x_pos(0)
	move_to_y_pos(0)

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

def sort_all_rows():
	global world_size
	
	move_to_x_pos(0)
	for row in range(world_size):
		move_to_y_pos(row)
		sort_row()
		
def sort_col():
	global world_size
	
	# Assume drone is at the first row
	for i in range(world_size):
		swapped = False
		for j in range(0, world_size - i - 1):
			move_to_y_pos(j)
			if measure() > measure(North):
				swap(North)
				swapped = True
		if not swapped:
			break
			
def sort_all_cols():
	global world_size

	move_to_y_pos(0)
	for col in range(world_size):
		move_to_x_pos(col)
		sort_col()
		
def sort_cacti():
	sort_all_rows()
	sort_all_cols()

def prep_cactus():
	till_all(None, False)

def run_cactus():
	go_to_origin()
	plant_all(Entities.Cactus)
	sort_cacti()
	harvest()

def get_mode():
	global min_num_items
	
	if num_items(Items.Hay) < min_num_items:
		return Items.Hay
	elif num_items(Items.Wood) < min_num_items:
		return Items.Wood
	elif num_items(Items.Carrot) < min_num_items:
		return Items.Carrot
	elif num_items(Items.Pumpkin) < min_num_items and num_items(Items.Fertilizer) > pumpkin_fertilizer_needed:
		return Items.Pumpkin
	elif num_items(Items.Cactus) < min_num_items:
		return Items.Cactus
	else:
		min_num_items *= 2
		return get_mode()
		
def prep_mode(mode):
	if mode == Items.Hay:
		prep_hay()
	elif mode == Items.Wood:
		prep_wood()
	elif mode == Items.Carrot:
		prep_carrot()
	elif mode == Items.Pumpkin:
		prep_pumpkin()
	elif mode == Items.Cactus:
		prep_cactus()

def run_mode(mode):
	if mode == Items.Hay:
		run_hay()
	elif mode == Items.Wood:
		run_wood()
	elif mode == Items.Carrot:
		run_carrot()
	elif mode == Items.Pumpkin:
		run_pumpkin()
	elif mode == Items.Cactus:
		run_cactus()
	
mode_cnt = 0
curr_mode = None
while True:
	if mode_cnt % mode_interval == 0:
		next_mode = get_mode()
		if next_mode != curr_mode:
			prep_mode(next_mode)
		curr_mode = next_mode
	run_mode(next_mode)
	mode_cnt += 1
