def harvest_weird_substance(num_weird_substance):
	starting_weird_substance = num_items(Items.Weird_Substance)
	ending_weird_substance = starting_weird_substance + num_weird_substance
	
	clear()

	while num_items(Items.Weird_Substance) < ending_weird_substance:
		while get_water() < 0.75:
			use_item(Items.Water)
		
		plant(Entities.Tree)

		while get_companion()[0] != Entities.Grass:
			harvest()
			plant(Entities.Tree)
		
		while not can_harvest():
			use_item(Items.Fertilizer)

		harvest()
