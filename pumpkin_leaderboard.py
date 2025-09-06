world_size = get_world_size()
target = 100000

fert_target = 40 # 25 statistically
water_target = 6 # 20 * 0.25 statistically
water_level_min = 0.15
fert_amt = 0
water_amt = 0

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

def till_soil():
	global world_size
	
	for x in range(world_size):
		for y in range(world_size):
			till()
			plant(Entities.Pumpkin)
			move(North)
		move(East)

def pumpkin_is_full():
	bot_left_id = measure()
	move(West)
	bot_right_id = measure()
	move(East)
	if not (bot_left_id and bot_right_id):
		return False
	return bot_left_id == bot_right_id

def choose_mode(water_amt, fert_amt):
	if water_amt > water_target and fert_amt > fert_target:
		return "water_and_fert"
	
	return "normal"

def plant_first_pass(world_size_loc=10):
	global water_amt
	global fert_amt
	global mode
	global water_level_min
	
	for x in range(world_size_loc):
		for y in range(world_size_loc):
			if get_water() < water_level_min:
				use_item(Items.Water)

			plant(Entities.Pumpkin)
			move(North)
		move(East)

	water_amt = num_items(Items.Water)
	fert_amt = num_items(Items.Fertilizer)
	
	mode = choose_mode(water_amt, fert_amt)

def harvest_full_pumpkin(world_size_loc=10):
	
	dead_pumpkins = []
	
	for x in range(world_size_loc):
		for y in range(world_size_loc):
			if get_entity_type() != Entities.Pumpkin or not can_harvest():
				plant(Entities.Pumpkin)
				dead_pumpkins.append((get_pos_x(), get_pos_y()))
			move(North)
		move(East)
	
	dead_pumpkins_set = set(dead_pumpkins)
	
	curr_water_amt = num_items(Items.Water)
	curr_fert_amt = num_items(Items.Fertilizer)
	use_water_fert = False
	
	pumpkins_to_deal_with = len(dead_pumpkins_set) * 1.5
	if curr_fert_amt > pumpkins_to_deal_with and curr_water_amt > pumpkins_to_deal_with * 0.25:
		use_water_fert = True
	
	while dead_pumpkins_set:
		for pumpkin in dead_pumpkins:
			if pumpkin not in dead_pumpkins_set:
				continue

			move_to_x_pos(pumpkin[0])
			move_to_y_pos(pumpkin[1])
			
			# Arrived at a spot where there was a dead pumpkin
				# Could be a fully grown pumpkin ready to harvest
				# Could be a dead pumpkin
				# Could be a pumpkin not fully grown
			if can_harvest():
				dead_pumpkins_set.remove(pumpkin)
				continue
			
			if get_entity_type() != Entities.Pumpkin:
				plant(Entities.Pumpkin)

			if use_water_fert:
				use_item(Items.Water)
				
				while not can_harvest():
					use_item(Items.Fertilizer)
					if get_entity_type() != Entities.Pumpkin:
						plant(Entities.Pumpkin)

	harvest()

def harvest_full_pumpkin_water_fert():
	global world_size
	
	for x in range(world_size):
		for y in range(world_size):
			if get_entity_type() != Entities.Pumpkin:
				if get_water() < 0.25:
					use_item(Items.Water)
				while True:
					plant(Entities.Pumpkin)
					use_item(Items.Fertilizer)
					
					if get_entity_type() == Entities.Pumpkin:
						break
			move(North)
		move(East)
		
	harvest_full_pumpkin()
	
	
till_soil()
harvest_full_pumpkin()

num_pumpkins = num_items(Items.Pumpkin)
while num_pumpkins < target:
#while True:
	if target - num_pumpkins < 1000:
		move_to_x_pos(0)
		move_to_y_pos(0)
		plant_first_pass(5)
		harvest_full_pumpkin(5)
	else:
		plant_first_pass()
		harvest_full_pumpkin()
	
	num_pumpkins = num_items(Items.Pumpkin)