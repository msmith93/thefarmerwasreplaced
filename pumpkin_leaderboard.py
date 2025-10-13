world_size = get_world_size()
target = 10000000

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

def plant_first_pass(world_size_loc=10):
	global water_amt
	global fert_amt
	global mode
	global water_level_min
	
	for x in range(world_size_loc):
		for y in range(world_size_loc):

			plant(Entities.Pumpkin)
			move(North)
		move(East)

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
	
	pumpkins_to_deal_with = len(dead_pumpkins_set) * 0.225
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

	
	
till_soil()
harvest_full_pumpkin()

num_pumpkins = num_items(Items.Pumpkin)
while num_pumpkins < target:
	plant_first_pass(8)
	harvest_full_pumpkin(8)
	
	num_pumpkins = num_items(Items.Pumpkin)
