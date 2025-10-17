
world_size = get_world_size()
water_threshold = 0.4

def harvest_jitter():
	for i in range(random() * 5 // 1):
		pass
	
	while not can_harvest():
		pass
	
	harvest()

def init_action():
	global world_size
	
	for i in range(world_size):
		plant(Entities.Bush)
		move(North)

def harvest_action():
	global water_threshold
	
    for i in range(100):
		while not can_harvest():
			pass
		harvest_jitter()

		companion, comp_pos = get_companion()
	
		while companion != Entities.Bush or not comp_pos[0] % 4:
			harvest()
			companion, comp_pos = get_companion()
		
		move(North)
	
	while True:
		while not can_harvest():
			pass
		harvest_jitter()
		
		if num_items(Items.Hay) >= 2000000000:
			return
    
        if get_water() < water_threshold:
			use_item(Items.Water)

		companion, comp_pos = get_companion()
	
		while companion != Entities.Bush or not comp_pos[0] % 4:
			harvest()
			companion, comp_pos = get_companion()
		
		move(North)

drones = []
for i in range(world_size):
	if i % 4:
		drones.append(spawn_drone(init_action))
	move(East)
		

# harvest_drones = []
# for i in range(world_size):
# 	if not i % 4:
# 		for j in range(4):
# 			harvest_drones.append(spawn_drone(harvest_action))
# 	move(East)

def run_harvests():
	global world_size
	
	harvest_drones = []
	for i in range(world_size):
		if not i % 4:
			for j in range(4):
				if len(harvest_drones) == 31:
					return
				while num_drones() >= max_drones():
					pass
				
				harvest_drones.append(spawn_drone(harvest_action))
		move(East)

run_harvests()
harvest_action()