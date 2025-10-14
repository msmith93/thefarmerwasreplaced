#set_world_size(8)
world_size = get_world_size()
target = 10000000

dir = North
def change_dir():
	global dir
	if dir == North:
		dir = South
	else:
		dir = North

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
	global dir
	
	for x in range(world_size):
		for y in range(world_size):
			till()
			plant(Entities.Pumpkin)
			if y == world_size - 1:
				break
			move(dir)
		change_dir()
	
		move(East)

def plant_first_pass(world_size_loc=10):
	global dir
	for x in range(world_size_loc):
		for y in range(world_size_loc):
			plant(Entities.Pumpkin)
			if y == world_size_loc - 1:
				break
			move(dir)
		change_dir()
		move(East)

def harvest_full_pumpkin(world_size_loc=10):
	global dir

	dead_pumpkins = []
	
	for x in range(world_size_loc):
		for y in range(world_size_loc):
			if get_entity_type() != Entities.Pumpkin or not can_harvest():
				plant(Entities.Pumpkin)
				dead_pumpkins.append((get_pos_x(), get_pos_y()))
			if y == world_size_loc - 1:
				break
			move(dir)
		change_dir()
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

			move_x = pumpkin[0]
			move_y = pumpkin[1]
			move_to_x_pos(move_x)
			move_to_y_pos(move_y)
			
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
			
			if move_x == 0:
				id1 = measure()
				id2 = measure(West)
				if id1 == id2:
					harvest()
					return
			elif move_x == 7:
				id1 = measure()
				id2 = measure(East)
				if id1 == id2:
					harvest()
					return
			elif move_y == 0:
				id1 = measure()
				id2 = measure(South)
				if id1 == id2:
					harvest()
					return
			elif move_y == 7:
				id1 = measure()
				id2 = measure(North)
				if id1 == id2:
					harvest()
					return

	harvest()

	
	
till_soil()
harvest_full_pumpkin(8)

num_pumpkins = num_items(Items.Pumpkin)
while num_pumpkins < target:
	plant_first_pass(8)
	harvest_full_pumpkin(8)
	
	num_pumpkins = num_items(Items.Pumpkin)
pass
