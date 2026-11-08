clear()

world_size = get_world_size()

jump(Unlocks.Mushrooms)
# Process a row of mushrooms
for j in range(get_world_size()):
	for i in range(get_world_size()):
		# Dig down to the top mushroom block
		while get_ground_type() != Grounds.Mushroom:
			dig()
	
		move(East)
	move(North)
	
def shroom_col():
	dig()
	target_shroom_num = measure()
	target_shroom_y = get_pos_y()
	target_shroom_z = get_pos_z()
	for i in range(world_size):
		move(North)
		curr_shroom_num = measure()
		if curr_shroom_num == target_shroom_num:
			for j in range(get_pos_y() - target_shroom_y):
				push(South)
				move(South)
		elif get_pos_z() > target_shroom_z:
			dig()
	
def hanlde_shroom():
	while num_drones() >= max_drones():
		pass
	
	spawn_drone(shroom_col)
	
	move(East)
	
def multi_mushroom():
	while True:
		hanlde_shroom()
		
multi_mushroom()

