def move_to_x_pos(x_target):
	x_curr = get_pos_x()
	moves_needed = x_target - x_curr
	if moves_needed > 0:
		dir = East
	else:
		dir = West
	for i in range(abs(moves_needed)):
		if not move(dir):
			hat_flip()

def move_to_y_pos(y_target):
	y_curr = get_pos_y()
	moves_needed = y_target - y_curr
	if moves_needed > 0:
		dir = North
	else:
		dir = South
	for i in range(abs(moves_needed)):
		if not move(dir):
			hat_flip()

def go_to_origin():
	move_to_x_pos(0)
	move_to_y_pos(0)

def hat_flip():
	change_hat(Hats.Straw_Hat)
	change_hat(Hats.Dinosaur_Hat)

def prep_dino():
	clear()
	change_hat(Hats.Straw_Hat)
	
	hat_flip()

world_size = get_world_size()
go_to_origin()
hat_flip()

while True:
	for i in range(world_size / 2):
		move_to_y_pos(world_size - 1)
		if not move(East):
			hat_flip()
		move_to_y_pos(1)
		if i != world_size / 2 - 1:
			if not move(East):
				hat_flip()

	move_to_y_pos(0)
	move_to_x_pos(0)

