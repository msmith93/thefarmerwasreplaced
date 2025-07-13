clear()

while True:	
	for i in range(4):
		for j in range(4):
			if can_harvest():
				harvest()
				if i % 2 == j % 2:
					plant(Entities.Tree)
				else:
					plant(Entities.Bush)
			elif get_water() < 0.8:
				use_item(Items.Water)
			move(East)
		move(North)
