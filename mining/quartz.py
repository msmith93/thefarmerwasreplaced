from mining_utils import dig_to_ground_type, dig_to_z

world_size = get_world_size()
clear()
jump(Unlocks.Quartz)


def get_coal():
	coal_depth = get_pos_z()
	
	for col in range(world_size):
		for row in range(world_size):
			move(North)
			if not dig_to_z(coal_depth):
				continue
			if get_ground_type() == Grounds.Coal:
				dig()
		move(East)

while True:
	for col in range(world_size):
		for row in range(world_size):
			move(North)
			dig()
			while get_ground_type() == Grounds.Quartz:
				dig()

		move(East)
