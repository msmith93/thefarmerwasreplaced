from mining_utils import dig_to_z, dig_to_ground_type, dig_to_ground_types, goto

world_size = get_world_size()

def mine_ore_col():
	for row in range(get_world_size()):
		if (get_pos_y() + get_pos_x()) % 2:
			i = 0
			while i < 3 and get_hardness() < 5:
				dig()
				i += 1
		while get_ground_type() in {Grounds.Iron, Grounds.Quartz}:
			dig()
		move(South)

def dispatch_miners():
	while not spawn_drone(mine_ore_col):
		pass
	
	move(East)
	
	while get_pos_x() > 0:

		if spawn_drone(mine_ore_col):
			move(East)
			
def multi_ore_mining():
	global world_size
	goto(0, world_size - 1)
	while get_ground_type() in {Grounds.Rock, Grounds.Iron, Grounds.Quartz}:
		dispatch_miners()

def main():
	clear()
	jump(Unlocks.Iron)
	dig_to_ground_type(Grounds.Rock)
	multi_ore_mining()