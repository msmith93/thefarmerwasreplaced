world_size = get_world_size()

# Currently only supports farming for Hay, Wood, and Carrots. Need to port other Item farming here.

min_num_items = 10000
water_threshold = 0.75

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
	pass


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

def till_all(plant_type):
	global world_size
	
	clear()
	for col in range(world_size):
		for row in range(world_size):
			till()
			plant(plant_type)
			move(North)
		move(East)

def get_mode():
	global min_num_items
	
	if num_items(Items.Hay) < min_num_items:
		return Items.Hay
	elif num_items(Items.Wood) < min_num_items:
		return Items.Wood
	elif num_items(Items.Carrot) < min_num_items:
		return Items.Carrot
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

def run_mode(mode):
	if mode == Items.Hay:
		run_hay()
	elif mode == Items.Wood:
		run_wood()
	elif mode == Items.Carrot:
		run_carrot()
	
mode_interval = 20
mode_cnt = 0
curr_mode = None
while True:
	if mode_cnt % mode_interval == 0:
		next_mode = get_mode()
		if next_mode != curr_mode:
			prep_mode(next_mode)
	run_mode(next_mode)
	mode_cnt += 1
