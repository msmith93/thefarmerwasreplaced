from Choreography import *

clear()
#world_size = 20
#x_offset = 1
#y_offset = 0
set_world_size(world_size)
num_tiles = world_size**2
drone_id = 0
#wear_costume(x_offset)

def till_column():
	global world_size
	for _ in range(world_size - 1):
		move(North)
		till()

def wait_for_drones(drones):
	for drone in drones:
		wait_for(drone)

def till_all():
	global world_size
	drones = []
	for _ in range(world_size):
		drones.append(spawn_drone(till_column))
		till()
		move(East)
	wait_for_drones(drones)

x_offset = x_offset % world_size

drawings = [
	(0 + x_offset,  0 + y_offset, spell_S, "Till", 1),
	(6 + x_offset,  6 + y_offset, spell_U, "Till", 1),
	(11 + x_offset, 6 + y_offset, spell_B, "Till", 1),
]

drawing = ()

def draw():
	global drawing
	goto_x(drawing[0])
	goto_y(drawing[1])
	drawing[2](drawing[3], drawing[4])

def draw_all():
	global drawings
	global drawing
	
	drones = []
	num_drawings = len(drawings)
	for i in range(num_drawings - 1):
		drawing = drawings[i]
		drones.append(spawn_drone(draw))
	
	drawing = drawings[num_drawings - 1]
	draw()

drone_id = 0
#till_all()
draw_all()
goto_x(world_size - 1)
goto_y(world_size - 1)
for i in range(50):
	do_a_flip()
