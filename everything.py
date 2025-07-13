mode = None
mode_iters_count = 0
mode_iters_target = 20

MIN_HAY = 30000
MIN_CARROT = 5000
MIN_PUMPKIN = 100000

pumpkin_first_run = True

def is_on_corner():
	x = get_pos_x()
	y = get_pos_y()
	world_size = get_world_size()
	
	if x == get_world_size() - 1:
		if y == world_size - 1 or y == 0:
			return True
	elif x == 0:
		if y == world_size - 1 or y == 0:
			return True
	
	return False

def get_mode():
	if num_items(Items.Hay) < MIN_HAY:
		return Entities.Grass
	if num_items(Items.Carrot) < MIN_CARROT:
		return Entities.Carrot
	if num_items(Items.Pumpkin) < MIN_PUMPKIN:
		return Entities.Pumpkin
	return Entities.Cactus
	
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
	
def plant_and_use_water_with_trees(plant_type):
	if is_on_corner():
		plant_type = Entities.Tree
	plant_and_use_water(plant_type)

def harvest_and_plant(plant_type):
	if can_harvest():
		harvest()
	if not get_entity_type() or get_entity_type() == Entities.Grass:
		plant_and_use_water_with_trees(plant_type)

def run_carrot_or_grass(plant_type):
	world_size = get_world_size()
	for x in range(world_size):
		for y in range(world_size):
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

			

def run_mode(mode):
	if mode in [Entities.Grass, Entities.Carrot, Entities.Cactus]:
		run_carrot_or_grass(mode)
	elif mode == Entities.Pumpkin:
		run_pumpkin()

while True:
	if mode_iters_count >= mode_iters_target or not mode:
		mode_iters_count = 0
		mode = get_mode()
	else:
		mode_iters_count += 1
		
	run_mode(mode)

