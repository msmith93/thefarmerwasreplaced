from carrot import harvest_carrot

world_size = 1

def move_to_x_pos(x_target, world_size=8):
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
	

def move_to_y_pos(y_target, world_size=8):
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

def till_soil(world_size=8):
	for x in range(world_size):
		for y in range(world_size):
			if get_ground_type() != Grounds.Soil:
				till()
			if get_entity_type() != Entities.Pumpkin:
				harvest()
			plant(Entities.Pumpkin)
			if y == world_size - 1:
				break
			move(North)
		move(East)

def plant_first_pass(world_size=8):
	for x in range(world_size):
		for y in range(world_size):
			plant(Entities.Pumpkin)
			if y == world_size - 1:
				break 
			move(North)
		move(East)

def harvest_full_pumpkin(world_size=8):
	dead_pumpkins = []
	
	for x in range(world_size):
		for y in range(world_size):
			if get_entity_type() != Entities.Pumpkin or not can_harvest():
				plant(Entities.Pumpkin)
				dead_pumpkins.append((get_pos_x(), get_pos_y()))
			if y == world_size - 1:
				break
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
			elif move_x == world_size - 1:
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
			elif move_y == world_size - 1:
				id1 = measure()
				id2 = measure(North)
				if id1 == id2:
					harvest()
					return

	harvest()

def harvest_pumpkin(num_pumpkins):
	global world_size
	starting_pumpkins = num_items(Items.Pumpkin)
	ending_pumpkins = starting_pumpkins + num_pumpkins
	
	world_size = get_world_size()

	curr_carrots = num_items(Items.Carrot)
	needed_carrots = get_cost(Entities.Pumpkin)[Items.Carrot] * num_pumpkins
	if curr_carrots < needed_carrots:
		harvest_carrot(needed_carrots - curr_carrots)


	till_soil(world_size)
	harvest_full_pumpkin(world_size)

	while num_items(Items.Pumpkin) < ending_pumpkins:
		plant_first_pass(world_size)
		harvest_full_pumpkin(world_size)