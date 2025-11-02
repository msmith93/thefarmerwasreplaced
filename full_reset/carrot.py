from wood import harvest_wood
from hay import harvest_hay

def harvest_carrot(num_carrot):
	curr_wood = num_items(Items.Wood)
	needed_wood = get_cost(Entities.Carrot)[Items.Wood] * num_carrot
	if curr_wood < needed_wood:
		harvest_wood(needed_wood - curr_wood)
	
	curr_hay = num_items(Items.Hay)
	needed_hay = get_cost(Entities.Carrot)[Items.Hay] * num_carrot
	if curr_hay < needed_hay:
		harvest_hay(needed_hay - curr_hay)

	ending_carrot = num_items(Items.Carrot) + num_carrot
	
	while num_items(Items.Carrot) < ending_carrot:
		if get_ground_type() != Grounds.Soil:
			till()
		
		if get_entity_type() != Entities.Carrot:
			harvest()
			plant(Entities.Carrot)
		elif can_harvest():
			harvest()
			plant(Entities.Carrot)
		
		if get_pos_y() == 0 and num_unlocked(Unlocks.Expand) > 1:
			move(East)
		move(North)