from mining_utils import dig_to_z

world_size = get_world_size()

jump(Unlocks.Rice)
while get_ground_type() != Grounds.Clay:
	dig()

clay_depth = get_pos_z()
plant(Entities.Rice)

for i in range(world_size):
	for j in range(world_size):
		move(North)
		dig_to_z(clay_depth)
		plant(Entities.Rice)
	move(East)

while True:
	for i in range(world_size):
		harvest()
		dig()
		plant(Entities.Rice)
		move(North)
	move(East)
	
	
	
	
