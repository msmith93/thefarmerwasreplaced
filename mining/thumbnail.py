from mining_utils import *

world_size = get_world_size()

jump(Unlocks.Mushrooms)

dig_to_ground_type(Grounds.Mushroom)
target_z = get_pos_z()

for i in range(world_size):
	for j in range(world_size):
		move(East)
		x = get_pos_x()
		y = get_pos_y()
		abs_x = abs(world_size / 2 - x)
		abs_y = abs(world_size / 2 - y)
		dig_to_z(target_z + 1 - abs_x - abs_y)
	move(North)
