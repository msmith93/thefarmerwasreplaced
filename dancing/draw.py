from Choreography import *

clear()
world_size = 32

#################
# Comment these out before running sub banner
x_offset = 0
y_offset = 5
draw_string = "BITSCULPT"
#################

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

sub_drawings = [
	(0  + x_offset, 1 + y_offset, spell_S, "Till", 2),
	(9 + x_offset, 1 + y_offset, spell_U, "Till", 2),
	(18 + x_offset, 1 + y_offset, spell_B, "Till", 2),
]

bitsculpt_drawings = [
	(0  + x_offset, 8 + y_offset, spell_B, "PSunflower", 2),
	(10 + x_offset, 8 + y_offset, spell_I, "PBush", 2),
	(14 + x_offset, 8 + y_offset, spell_T, "PBush", 2),
	(0  + x_offset,     y_offset, spell_S, "PBush", 1),
	(6  + x_offset,     y_offset, spell_C, "PBush", 1),
	(11 + x_offset,     y_offset, spell_U, "PBush", 1),
	(16 + x_offset,     y_offset, spell_L, "PBush", 1),
	(21 + x_offset,     y_offset, spell_P, "PSunflower", 1),
	(26 + x_offset,     y_offset, spell_T, "PBush", 1),
]

drawing = ()

def draw():
	global drawing
	goto_x(drawing[0])
	goto_y(drawing[1])
	drawing[2](drawing[3], drawing[4])

def select_drawings():
	global draw_string
	global drawings
	global bitsculpt_drawings
	global sub_drawings
	if draw_string == "BITSCULPT":
		drawings = bitsculpt_drawings
	elif draw_string == "SUB":
		drawings = sub_drawings

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
select_drawings()
draw_all()
goto_x(world_size - 1)
goto_y(world_size - 1)
for i in range(200):
	do_a_flip()
