from mining_utils import  climb_to_z

clear()

world_size = get_world_size()


def plant_column():
	for j in range(world_size):
		if get_ground_type() != Grounds.Soil:
			till()
		plant(Entities.Bamboo)
		
		move(North)

def harvest_west():
	move(West)
	harvest()
	move(East)

def harvest_east():
	move(East)
	harvest()
	move(West)
		
def harvest_bamboo():
	for j in range(world_size):
		west_bamboo_height = measure(West) + 1
		east_bamboo_height = measure(East) + 1
		
		west_taller = False
		if west_bamboo_height > east_bamboo_height:
			west_taller = True
		
		if west_taller:
			hover(west_bamboo_height)
			harvest_west()
			hover(east_bamboo_height)
			harvest_east()
		else:
			hover(east_bamboo_height)
			harvest_east()
			hover(west_bamboo_height)
			harvest_west()
		move(North)

while True:
	for i in range(world_size):
		if i % 3 != 1:
			plant_column()
		move(East)
	
	
	for i in range((world_size // 3) * 3):
		if i % 3 == 1:
			harvest_bamboo()
		move(East)
	clear()