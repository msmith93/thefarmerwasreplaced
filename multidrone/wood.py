clear()

hats = [Hats.Green_Hat, Hats.Purple_Hat]
world_size = get_world_size()

def init_action():
	global world_size
	
	for i in range(world_size):
		if ((get_pos_x() + get_pos_y()) % 2):
			plant(Entities.Tree)
			use_item(Items.Water)
		else:
			plant(Entities.Bush)
			
		move(North)

drones = []
for i in range(world_size - 1):
	drones.append(spawn_drone(init_action))
	move(East)

init_action()
move(East)

def run_drone():
	global hats
	
	while True:
		if can_harvest():
			harvest()
			if ((get_pos_x() + get_pos_y()) % 2):
				plant(Entities.Tree)
				use_item(Items.Water)
				companion, comp_pos = get_companion()
		
				while companion != Entities.Bush or ((comp_pos[0] + comp_pos[1]) % 2):
					harvest()
					plant(Entities.Tree)
					companion, comp_pos = get_companion()
			else:
				plant(Entities.Bush)
		move(North)

def run_harvests():
	global world_size
	
	harvest_drones = []
	for i in range(world_size):
		if len(harvest_drones) == 31:
			return
		while num_drones() >= max_drones():
			pass
				
		harvest_drones.append(spawn_drone(run_drone))
		move(East)

run_harvests()
run_drone()
	
