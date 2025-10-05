clear()
set_world_size(max_drones() - 1)
change_hat(Hats.Brown_Hat)

hats = [Hats.Green_Hat, Hats.Purple_Hat]
world_size = get_world_size()

# Sunflower Facts.
max_petals = 15
min_petals = 7

curr_petal_gathering = max_petals

def plant_col():
	global world_size
	
	for j in range(world_size):
		if get_ground_type() != Grounds.Soil:
			till()
		plant(Entities.Sunflower)
		if get_water() < 0.5:
			use_item(Items.Water)
		move(North)

def plant_crop():
	global world_size
	
	# Assume we're at the origin
	drones = []
		
	for i in range(world_size):
		drones.append(spawn_drone(plant_col))
		move(East)
		
	wait_for_drones(drones)
	
	
def run_drone():
	global curr_petal_gathering
	global world_size
	
	change_hat(hats[get_pos_x() % 2])
	
	for j in range(world_size):
		if measure() == curr_petal_gathering:
			while not can_harvest():
				use_item(Items.Fertilizer)
			harvest()
		move(North)

def wait_for_drones(drones):
	for drone in drones:
		wait_for(drone)

def run_sunflower():
	global world_size
	global max_petals
	global min_petals
	global curr_petal_gathering
	
	plant_crop()
	
	for petal_count in range(max_petals, min_petals, -1):
		curr_petal_gathering = petal_count
		 
		# Assume we're at the origin
		drones = []
		
		for i in range(world_size):
			drones.append(spawn_drone(run_drone))
			move(East)
		
		wait_for_drones(drones)
	
while True:
	run_sunflower()
	