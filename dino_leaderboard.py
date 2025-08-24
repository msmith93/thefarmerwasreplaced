world_size = get_world_size()

offlimit_columns_stage1 = [0, world_size - 1]
offlimit_columns_stage2 = [0, world_size - 1]
clear()
change_hat(Hats.Dinosaur_Hat)
apple_pos = measure()
squares_occupied = 1
game_complete = False
aggressive_stage = True


def measure_apple():
	global apple_pos
	global squares_occupied
	apple_pos = measure()
	squares_occupied += 1
	
def move_and_check_apple(direction):
	global apple_pos

	if not move(direction):
		return False
	if (get_pos_x(), get_pos_y()) == apple_pos:
		measure_apple()

	return True

def move_to_col(target_x_pos, do_measure=True):
	global world_size
	global apple_pos
	curr_x = get_pos_x()
	
	direction = West
	if curr_x < target_x_pos:
		direction = East
	
	for x in range(abs(target_x_pos - curr_x)):
		this_check = move
		if do_measure:
			this_check = move_and_check_apple 
		if not this_check(direction):
			return False
	
	return True

def move_to_row(target_y_pos, do_measure=True):
	global world_size
	global apple_pos
	curr_y = get_pos_y()
	
	direction = South
	if curr_y < target_y_pos:
		direction = North
		
	for y in range(abs(target_y_pos - curr_y)):
		this_check = move
		if do_measure:
			this_check = move_and_check_apple 
		if not this_check(direction):
			return False
	
	return True

def transition_to_stage_2():
	global offlimit_columns_stage1
	global world_size
	
	move_to_col(world_size - 1)
	move_to_row(0)
	
	offlimit_columns_stage1 = [0, world_size - 1]
	
	return False

def transition_to_stage_1():
	global offlimit_columns_stage2
	global world_size
	
	move_to_col(0)
	move_to_row(world_size - 1)
	
	offlimit_columns_stage2 = [0, world_size - 1]
	
	return False

def stage_1_apple_collect():
	global apple_pos
	global world_size
	global offlimit_columns_stage1
	global offlimit_columns_stage2
	
	apple_pos_x, apple_pos_y = apple_pos
	if (apple_pos_x in offlimit_columns_stage1) or (apple_pos_y == 0):
		return transition_to_stage_2()
	else:
		apple_x_odd = apple_pos_x % 2
		target_x_pos = apple_pos_x 
		if not apple_x_odd:
			target_x_pos = apple_pos_x - 1
		
		if target_x_pos <= get_pos_x():
			return transition_to_stage_2()
		else:
			move_to_col(target_x_pos)
			move_to_row(apple_pos_y)
			move_and_check_apple(East)
			move_to_row(world_size - 1)
			offlimit_columns_stage2 += [target_x_pos, target_x_pos + 1]
	
	return True

def stage_2_apple_collect():
	global apple_pos
	global world_size
	global offlimit_columns_stage1
	global offlimit_columns_stage2
	
	apple_pos_x, apple_pos_y = apple_pos
	if (apple_pos_x in offlimit_columns_stage2) or (apple_pos_y == world_size - 1):
		return transition_to_stage_1()
	else:
		apple_x_odd = apple_pos_x % 2
		target_x_pos = apple_pos_x 
		if apple_x_odd:
			target_x_pos = apple_pos_x + 1
		
		if target_x_pos >= get_pos_x():
			return transition_to_stage_1()
		else:
			move_to_col(target_x_pos)
			move_to_row(apple_pos_y)
			move_and_check_apple(West)
			move_to_row(0)
			offlimit_columns_stage1 += [target_x_pos, target_x_pos - 1]
	
	return True

# STAGE 1
move_to_row(world_size - 1)

while aggressive_stage:
	while stage_1_apple_collect() and get_pos_x() < world_size - 1:
		pass
		
	
	while stage_2_apple_collect() and get_pos_x() > 0:
		pass
	
	if squares_occupied > (world_size - 1) * 4 - 7:
		break

move_to_col(world_size - 1)
move_to_row(0)
move_to_col(0)


while True:
	for i in range(world_size / 2):
		game_complete = not move_to_row(world_size - 1, False)
		game_complete = game_complete or not move(East)
		game_complete = game_complete or not move_to_row(1, False)
		if i != world_size / 2 - 1:
			game_complete = game_complete or not move(East)
		
		if game_complete:
			break

	game_complete = game_complete or not move_to_row(0, False)
	game_complete = game_complete or not move_to_col(0,)
	
	if game_complete:
		break

change_hat(Hats.Straw_Hat)
