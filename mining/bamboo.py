from mining_utils import  climb_to_z

clear()

world_size = get_world_size()


def plant_column():
	for j in range(world_size):
		if get_ground_type() != Grounds.Soil:
			till()
		plant(Entities.Bamboo)
		
		move(North)
		
def harvest_bamboo():
	for j in range(world_size):
		west_bamboo_height = measure(West)
		east_bamboo_height = measure(East)
		
		if west_bamboo_height < east_bamboo_height:
			climb_to_z(west_bamboo_height)
			move(West)
			harvest()
			move(East)
			climb_to_z(east_bamboo_height)
			move(East)
			harvest()
			move(West)
		else:
			climb_to_z(east_bamboo_height)
			move(East)
			harvest()
			move(West)
			climb_to_z(west_bamboo_height)
			move(West)
			harvest()
			move(East)
		
		move(North)

while True:
	for i in range(world_size):
		if i % 3 > 0:
			plant_column()
		move(East)
	
	
	for i in range(world_size):
		if i % 3 == 0:
			harvest_bamboo()
		move(East)
