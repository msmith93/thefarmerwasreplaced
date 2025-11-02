def harvest_wood(num_wood):
	ending_wood = num_items(Items.Wood) + num_wood

	plant_trees = num_unlocked(Unlocks.Trees) > 0
	watering = num_unlocked(Unlocks.Watering) > 0
	
	while num_items(Items.Wood) < ending_wood:
		if can_harvest() or get_entity_type() not in [Entities.Bush, Entities.Tree]:
			harvest()
			if plant_trees and ((get_pos_x() + get_pos_y()) % 2):
				plant(Entities.Tree)
				if watering and get_water() < 0.5:
					use_item(Items.Water)
			else:
				plant(Entities.Bush)
		
		if get_pos_y() == 0 and num_unlocked(Unlocks.Expand) > 1:
			move(East)
		move(North)