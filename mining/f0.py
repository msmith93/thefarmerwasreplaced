from mining_utils import dig_to_ground_type

jump(Unlocks.Mushrooms)

dig_to_ground_type(Grounds.Mushroom)

all_directions = [North, South, East, West]

while True:
	rand = random()
	
	if rand < 0.33:
		dig()
	elif rand < 0.66:
		rand_dir = all_directions[random() * 4 // 1]
		move(North)
	else:
		rand_dir = all_directions[random() * 4 // 1]
		push(South)

