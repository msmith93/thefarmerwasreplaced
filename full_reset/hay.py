def harvest_hay(num_hay):
	starting_hay = num_items(Items.Hay)
	ending_hay = starting_hay + num_hay

	while num_items(Items.Hay) < ending_hay:
		if get_ground_type() != Grounds.Grassland:
			till()

		while not can_harvest():
			pass
		harvest()

		if get_pos_y() == 0 and num_unlocked(Unlocks.Expand) > 1:
			move(East)
		if num_unlocked(Unlocks.Expand):
			move(North)

