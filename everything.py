mode = None
mode_iters_count = 0
mode_iters_target = 20

MIN_POWER = 1000
MIN_HAY = 100000
MIN_WOOD = 1000000
MIN_CARROT = 40000
MIN_PUMPKIN = 200000
MIN_CACTI = 600000

world_size = get_world_size()

pumpkin_first_run = True

def is_on_corner():
	x = get_pos_x()
	y = get_pos_y()
	world_size = get_world_size()
	
	if x == world_size - 1:
		if y == world_size - 1 or y == 0:
			return True
	elif x == 0:
		if y == world_size - 1 or y == 0:
			return True
	
	return False

def get_mode():
	if num_items(Items.Power) < MIN_POWER:
		return Entities.Sunflower
	if num_items(Items.Hay) < MIN_HAY:
		return Entities.Grass
	if num_items(Items.Wood) < MIN_WOOD:
		return Entities.Tree
	if num_items(Items.Carrot) < MIN_CARROT:
		return Entities.Carrot
	if num_items(Items.Pumpkin) < MIN_PUMPKIN:
		return Entities.Pumpkin
	if num_items(Items.Cactus) < MIN_CACTI:
		return Entities.Cactus
	return Entities.Dinosaur
	
def prepare_ground(plant_type):
	ground_type = get_ground_type()
	if plant_type != Entities.Grass and ground_type == Grounds.Grassland:
		till()
	elif plant_type == Entities.Grass and ground_type != Grounds.Grassland:
		till()

def plant_and_use_water(plant_type):
	prepare_ground(plant_type)
	if get_water() < .5:
		use_item(Items.Water)
	if Entities.Grass != plant_type:
		plant(plant_type)

def harvest_and_plant(plant_type):
	if can_harvest():
		harvest()
	if not get_entity_type() or get_entity_type() == Entities.Grass:
		plant_and_use_water(plant_type)

def run_carrot_or_grass(plant_type):
	world_size = get_world_size()
	for x in range(world_size):
		for y in range(world_size):
			harvest_and_plant(plant_type)
			move(North)
		move(East)
		
def run_tree():
	global world_size
	for x in range(world_size):
		for y in range(world_size):
			if x % 2 == y % 2:
				plant_type = Entities.Tree
			else:
				plant_type = Entities.Bush
			harvest_and_plant(plant_type)
			move(North)
		move(East)
	
def run_pumpkin():
	global pumpkin_first_run
	world_size = get_world_size()
	empty_cell = False
	first_pass = True
	
	for x in range(world_size):
		for y in range(world_size):
			prepare_ground(Entities.Pumpkin)
			entity_type = get_entity_type()
			
			if entity_type != Entities.Pumpkin:
				empty_cell = True
				harvest()
				plant_and_use_water(Entities.Pumpkin)
				if not pumpkin_first_run:
					use_item(Items.Fertilizer)
					while not get_entity_type():
						plant_and_use_water(Entities.Pumpkin)
						use_item(Items.Fertilizer)
						
				
			move(North)
		move(East)
	
	if not pumpkin_first_run:
		if can_harvest():
			harvest()
			pumpkin_first_run = True
	else:
		pumpkin_first_run = False

def plant_cacti():
	clear()
	world_size = get_world_size()
	for i in range(world_size):
		for j in range(world_size):
			till()
			plant(Entities.Cactus)
			move(East)
		move(North)

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
	world_size = get_world_size()
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
	world_size = get_world_size()
	move_to_x_pos(0)
	for i in range(world_size):
		move_to_y_pos(i)
		sort_row()
		
def sort_col():
	world_size = get_world_size()
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
	world_size = get_world_size()
	move_to_y_pos(0)
	for i in range(world_size):
		move_to_x_pos(i)
		sort_col()
		
def sort_cacti():
	sort_all_rows()
	sort_all_cols()

def run_cactus():
	plant_cacti()
	go_to_origin()
	sort_cacti()
	harvest()

def run_sunflower():
	clear()
	change_hat(Hats.Straw_Hat)
	go_to_origin()
	sf_size_tracker = {}
	world_size = get_world_size()
	for x in range(world_size):
		for y in range(world_size):
			plant_and_use_water(Entities.Sunflower)
			pedal_count = measure()
			if pedal_count:
				if pedal_count not in sf_size_tracker:
					sf_size_tracker[pedal_count] = []
				else:
					pass
				sf_size_tracker[pedal_count].append((x, y))
			move(North)
		move(East)
	
	min_pedals = 7
	max_pedals = 15
	for j in range(0, max_pedals - min_pedals + 1):
		i = max_pedals - j
		targets_list = sf_size_tracker[i]
		
		for target in targets_list:
			move_to_x_pos(target[0])
			move_to_y_pos(target[1])
			harvest()

def hat_flip():
	change_hat(Hats.Straw_Hat)
	change_hat(Hats.Dinosaur_Hat)

def run_dino():
	next_x, next_y = measure()
	
	move_to_x_pos(next_x)
	move_to_y_pos(next_y)
	
	if get_entity_type() != Entities.Apple:
		hat_flip()

def prep_dino():
	clear()
	hat_flip()
	
def prep_ground(ground_type):
	clear()
	for i in range(world_size):
		for j in range(world_size):
			if get_ground_type() != ground_type:
				till()
			move(East)
		move(North)

def prep_mode(mode):
	if mode == Entities.Grass:
		prep_ground(Grounds.Grassland)
	elif mode in {Entities.Carrot, Entities.Pumpkin}:
		prep_ground(Grounds.Soil)
	elif mode == Entities.Tree:
		pass
	elif mode == Entities.Cactus:
		pass
	elif mode == Entities.Dinosaur:
		prep_dino()

def run_mode(mode):

	if mode in [Entities.Grass, Entities.Carrot]:
		run_carrot_or_grass(mode)
	elif mode == Entities.Tree:
		run_tree()
	elif mode == Entities.Sunflower:
		run_sunflower()
	elif mode == Entities.Cactus:
		run_cactus()
	elif mode == Entities.Pumpkin:
		run_pumpkin()
	elif mode == Entities.Dinosaur:
		run_dino()

change_hat(Hats.Straw_Hat)

while True:
	prev_mode = mode
	if mode_iters_count >= mode_iters_target or not mode:
		mode_iters_count = 0
		mode = get_mode()
	else:
		mode_iters_count += 1
	
	if prev_mode != mode:
		prep_mode(mode)
	run_mode(mode)
	
