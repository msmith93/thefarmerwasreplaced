from Choreography import *

clear()
world_size = 5
set_world_size(world_size)
set_execution_speed(2)

num_tiles = world_size**2
dance_id = 0

def dance():
	global world_size
	global dance_id
	get_into_position(dance_id, world_size)
	wear_costume(dance_id)
	dance_dance()

for i in range(num_tiles - 1, 0, -1):
	dance_id = i
	spawn_drone(dance)

dance_id = 0
dance()
