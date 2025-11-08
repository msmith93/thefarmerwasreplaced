def harvest_hay(num_hay):
	starting_hay = num_items(Items.Hay)
	ending_hay = starting_hay + num_hay

	plant_trees = (
		num_unlocked(Unlocks.Polyculture) > 0 and num_unlocked(Unlocks.Trees) > 0
	)
	watering = num_unlocked(Unlocks.Watering) > 0

	while num_items(Items.Hay) < ending_hay:
		if get_ground_type() != Grounds.Grassland:
			till()

		if can_harvest():
			harvest()

		if ((get_pos_x() + get_pos_y()) % 2) and plant_trees:
			plant(Entities.Tree)
			if watering and get_water() < 0.5:
				use_item(Items.Water)

		if get_pos_y() == 0 and num_unlocked(Unlocks.Expand) > 1:
			move(East)
		if num_unlocked(Unlocks.Expand):
			move(North)
