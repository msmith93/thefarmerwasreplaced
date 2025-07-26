# this file must be named multidrone for the code spawn_drone("multidrone") to work
world_size = get_world_size()

def prep_hay():
	clear()
	
def run_hay():
	global world_size
	global reverse
	
	for col in range(world_size):
		for row in range(world_size):
			if can_harvest():
				harvest()
			move(South)
		move(East)

if get_drone_id() == 0:
	prep_hay()
	for i in range(max_drones() - 1):
		spawn_drone("multidrone")

east_shift = world_size // max_drones() * get_drone_id()
for i in range(east_shift):
	move(East)

do_a_flip()

while True:
	run_hay()
