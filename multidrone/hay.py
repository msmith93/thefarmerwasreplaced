clear()

hats = [Hats.Green_Hat, Hats.Purple_Hat]
hats_len = len(hats)

counter = 5
world_size = get_world_size()

def drone_action():
	global counter
	global world_size
	global hats
	
	change_hat(hats[get_pos_x() % 2])
	
	for j in range(world_size):
		harvest()
		move(North)

while True:
	for i in range(world_size):
		counter = hats_len % (i + 1)
		
		spawn_drone(drone_action)
		while num_drones() >= max_drones():
			pass
	
		move(East)