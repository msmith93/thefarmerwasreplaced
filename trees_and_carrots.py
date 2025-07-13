
def is_on_corner():
	x = get_pos_x()
	y = get_pos_y()
	world_size = get_world_size()
	
	if x == get_world_size() - 1:
		if y == world_size - 1 or y == 0:
			return True
	elif x == 0:
		if y == world_size - 1 or y == 0:
			return True
	
	return False
	
def plant_and_use_water(plant_type):
	if plant_type != Entities.Grass and get_ground_type() == Grounds.Grassland:
		till()
	if get_water() < .8:
		use_item(Items.Water)
	plant(plant_type)

def harvest_and_plant(plant_type):
	if can_harvest():
		harvest() 
		
		plant_and_use_water(plant_type)
	else:
		# Ensure our plant is growing
		if get_entity_type() != plant_type:
			plant_and_use_water(plant_type)

while True:
	
	for i in range(get_world_size()):
		if is_on_corner():
			harvest_and_plant(Entities.Tree)
		else:
			harvest_and_plant(Entities.Carrot)
		move(North)
	move(East)
