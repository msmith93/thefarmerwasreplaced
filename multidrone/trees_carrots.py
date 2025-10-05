clear()
set_world_size(max_drones() - 1)
change_hat(Hats.Brown_Hat)

hats = [Hats.Green_Hat, Hats.Purple_Hat]
world_size = get_world_size()

def plant_crop(i, j):
	if (i + j) % 2 == 0:
		plant(Entities.Tree)
	else:
		plant(Entities.Carrot)
	
	if get_water() < 0.5:
			use_item(Items.Water)

def run_drone():
	global hats
	
	change_hat(hats[get_pos_x() % 2])
	
	for j in range(get_world_size()):
		if get_ground_type() != Grounds.Soil:
			till()
			plant_crop(get_pos_x(), j)

		if can_harvest():
			harvest()
			plant_crop(get_pos_x(), j)
		move(North)

def run_carrots_trees():
	global world_size
	
	for i in range(world_size):
		spawn_drone(run_drone)
		while num_drones() >= max_drones():
			pass
		move(East)
	

while True:
	run_carrots_trees()
	