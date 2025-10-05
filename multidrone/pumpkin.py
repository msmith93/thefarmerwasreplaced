clear()
set_world_size(max_drones() - 1)
change_hat(Hats.Brown_Hat)
world_size = get_world_size()
first_pass = True

def check_pumpkin():
	left_id = measure()
	move(West)
	right_id = measure()
	move(East)
	return left_id == right_id

def wait_for_drones(drones):
	for drone in drones:
		wait_for(drone)

def plant_column():
	global world_size
	global first_pass
	
	for j in range(world_size):
		if get_entity_type() != Entities.Pumpkin:
			if get_ground_type() != Grounds.Soil:
				till()
			plant(Entities.Pumpkin)
				
			if not first_pass:
				while not can_harvest():
					if get_entity_type() == Entities.Dead_Pumpkin:
						plant(Entities.Pumpkin)
					use_item(Items.Fertilizer)
		move(North)

def plant_pumpkins():
	global world_size
	
	# Assume we're at the origin
	drones = []
	
	for i in range(world_size):
		drones.append(spawn_drone(plant_column))
		move(East)
	
	wait_for_drones(drones)

while True:
	plant_pumpkins()
	first_pass = False
	if check_pumpkin():
		harvest()
		first_pass = True