clear()
world_size = get_world_size()


def init_action():
	global world_size
	
	for i in range(world_size):
		plant(Entities.Bush)
		move(North)

def harvest_action():
	while True:
		while not can_harvest():
			pass
		harvest()
		
		if num_items(Items.Hay) >= 2000000000:
			return

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
		
for drone in drones:
	wait_for(drone)

for i in range(world_size):
	if not i % 4:
		for j in range(4):
			drones.append(spawn_drone(harvest_action))
	move(East)

# def run_harvests():
# 	global world_size
	
# 	for i in range(world_size):
# 		if not i % 4:
# 			for j in range(4):
# 				new_drone = spawn_drone(harvest_action)
# 				if new_drone:
# 					drones.append(new_drone)
# 				else:
# 					return
# 		move(East)

# run_harvests()
