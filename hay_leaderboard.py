world_size = 3
set_world_size(world_size)

counter = 0
water_counter = 0
water_threshold = 0.4

plant(Entities.Bush)
move(North)
plant(Entities.Bush)
move(North)
plant(Entities.Bush)
move(East)
plant(Entities.Bush)
move(South)
plant(Entities.Bush)
move(South)
plant(Entities.Bush)
move(East)

def run_hay():
	global counter
	global water_counter
	global water_threshold

	while True:
		if not can_harvest():
			counter += 1
		harvest()

		if num_items(Items.Hay) > 100000000:
			return
		
		if get_water() < water_threshold:
			use_item(Items.Water)
			water_counter += 1

		companion, comp_pos = get_companion()
		
		while companion != Entities.Bush or comp_pos[0] == 2:
			harvest()
			companion, comp_pos = get_companion()

		move(North)

run_hay()
pass
