world_size = get_world_size()
world_size_minus_one = world_size - 1

edge_positions = [0, world_size_minus_one]

offlimit_columns_stage1 = {
}
offlimit_columns_stage2 = {
}

grid_data = [
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]
    


clear()
change_hat(Hats.Dinosaur_Hat)
apple_pos = measure()
tail_positions = [(0,0)]
tail_positions_set = set(tail_positions)
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
    global tail_positions
	global tail_positions_set
	global grid_data
    
    curr_pos = (get_pos_x(), get_pos_y())

    if not move(direction):
        return False
       
    curr_pos_x = get_pos_x()
    curr_pos_y = get_pos_y()
    curr_pos = (curr_pos_x, curr_pos_y)
    tail_positions.insert(0, curr_pos)
    tail_positions_set.add(curr_pos)
    grid_data[curr_pos[0]][curr_pos[1]] = 1
        
    if curr_pos == apple_pos:
        measure_apple()
    else:
        popped_item = tail_positions.pop()
        grid_data[popped_item[0]][popped_item[1]] = 0
        tail_positions_set.remove(popped_item)

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
            if do_measure:
                pass
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

def transition_to_stage_2(panic_mode=False):
    global offlimit_columns_stage1
    global world_size
    global world_size_minus_one
    global offlimit_columns_stage2
    
    if panic_mode:
        move_and_check_apple(East)
        curr_x = get_pos_x()
        if not curr_x % 2:
            move_and_check_apple(East)
        while curr_x < world_size_minus_one:
            if curr_x in offlimit_columns_stage1:
                target_y_pos = offlimit_columns_stage1[curr_x] + 1
                move_to_row(target_y_pos)
                offlimit_columns_stage2[curr_x] = target_y_pos
                offlimit_columns_stage2[curr_x + 1] = target_y_pos
            else:
                move_to_row(5)
                offlimit_columns_stage2[curr_x] = 5
                offlimit_columns_stage2[curr_x + 1] = 5
            
            move_and_check_apple(East)
            move_to_row(world_size_minus_one)
            move_and_check_apple(East)

            curr_x = get_pos_x()
        
        move_to_row(0)
    else:
        move_to_col(world_size_minus_one)
        move_to_row(0)
    
    offlimit_columns_stage1 = {
    }

    
    return False

def transition_to_stage_1(panic_mode=False):
    global offlimit_columns_stage2
    global offlimit_columns_stage1
    global world_size
    global world_size_minus_one

    if panic_mode:
        move_and_check_apple(West)
        curr_x = get_pos_x()
        if curr_x % 2:
            move_and_check_apple(West)
        while curr_x > 0:
            if curr_x in offlimit_columns_stage2:
                target_y_pos = offlimit_columns_stage2[curr_x] - 1
                move_to_row(target_y_pos)
                offlimit_columns_stage1[curr_x] = target_y_pos
                offlimit_columns_stage1[curr_x - 1] = target_y_pos
            else:
                move_to_row(4)
                offlimit_columns_stage1[curr_x] = 4
                offlimit_columns_stage1[curr_x - 1] = 4
            
            move_and_check_apple(West)
            move_to_row(0)
            move_and_check_apple(West)

            curr_x = get_pos_x()
        
        move_to_row(world_size_minus_one)
    else:
        move_to_col(0)
        move_to_row(world_size_minus_one)
    
    offlimit_columns_stage2 = {
    }
    
    return False

def stage_1_apple_collect():
    global apple_pos
    global world_size
    global offlimit_columns_stage1
    global offlimit_columns_stage2
    global world_size_minus_one
    global squares_occupied

    apple_pos_x, apple_pos_y = apple_pos

    buffer_needed = 0
    if squares_occupied > 35:
        buffer_needed = squares_occupied - 35
    
    apple_buffer = (world_size_minus_one - apple_pos_y) * 2
    if buffer_needed > apple_buffer:
        return transition_to_stage_2(True)
    
    if apple_pos_y == 0 or apple_pos_x in edge_positions or (apple_pos_x in offlimit_columns_stage1 and apple_pos_y <= offlimit_columns_stage1[apple_pos_x]):
        return transition_to_stage_2()
    else:
        apple_x_odd = apple_pos_x % 2
        target_x_pos = apple_pos_x 
        if not apple_x_odd:
            target_x_pos = apple_pos_x - 1
        
        if target_x_pos <= get_pos_x() or (apple_pos_y < 3 and apple_pos_x > 7):
            return transition_to_stage_2()
        else:
            move_to_col(target_x_pos)
            move_to_row(apple_pos_y)
            offlimit_columns_stage2[target_x_pos] = apple_pos_y
            offlimit_columns_stage2[target_x_pos + 1] = apple_pos_y
            move_and_check_apple(East)
            move_to_row(world_size_minus_one)
    
    return True

def stage_2_apple_collect():
    global apple_pos
    global world_size
    global offlimit_columns_stage1
    global offlimit_columns_stage2
    global world_size_minus_one
    global squares_occupied
    
    apple_pos_x, apple_pos_y = apple_pos

    buffer_needed = 0
    if squares_occupied > 35:
        buffer_needed = squares_occupied - 35
    
    apple_buffer = apple_pos_y * 2
    if buffer_needed > apple_buffer:
        return transition_to_stage_1(True)

    if apple_pos_y == world_size_minus_one or apple_pos_x in edge_positions or (apple_pos_x in offlimit_columns_stage2 and apple_pos_y >= offlimit_columns_stage2[apple_pos_x]):
        return transition_to_stage_1()
    else:
        apple_x_odd = apple_pos_x % 2
        target_x_pos = apple_pos_x 
        if apple_x_odd:
            target_x_pos = apple_pos_x + 1
        
        if target_x_pos >= get_pos_x()  or (apple_pos_y > 7 and apple_pos_x < 3):
            return transition_to_stage_1()
        else:
            move_to_col(target_x_pos)
            move_to_row(apple_pos_y)
            offlimit_columns_stage1[target_x_pos] = apple_pos_y
            offlimit_columns_stage1[target_x_pos - 1] = apple_pos_y
            move_and_check_apple(West)
            move_to_row(0)
    
    return True

def move_to_right_col_wavy():
    global world_size
    global world_size_minus_one
    global offlimit_columns_stage1

    # Assume curr x is zero
    for x in range(world_size):
        if x % 2:
            target_y = 1
            if x in offlimit_columns_stage1:
                target_y = offlimit_columns_stage1[x] + 1
            while get_pos_y() != target_y:
                move(South)
            move(East)
        else: # x is even, go up to top row, then move right
            while get_pos_y() != world_size_minus_one:
                move(North)
            move(East)

def find_origin():
	curr_y = get_pos_y()
	curr_x = get_pos_x()
	
	if curr_x > 0 and not curr_x % 2:
		move(West)
		while get_pos_y() > 0:
			move(South)
		while get_pos_x() > 0:
			move(West)
		

def transition_to_route():
	find_origin()
    move_to_right_col_wavy()
    while get_pos_y() != 0:
        move(South)
    while get_pos_x() != 0:
        move(West)
	

# STAGE 1
move_to_row(world_size_minus_one)

while aggressive_stage:
    while stage_1_apple_collect() and get_pos_x() < world_size_minus_one:
        pass
        
    
    while stage_2_apple_collect() and get_pos_x() > 0:
        pass
    
    if squares_occupied > (world_size_minus_one) * 4 + 1:
        break

transition_to_route()

while True:
    for i in range(world_size / 2):
        game_complete = not move_to_row(world_size_minus_one, False)
        game_complete = game_complete or not move(East)
        game_complete = game_complete or not move_to_row(1, False)
        if i != world_size / 2 - 1:
            game_complete = game_complete or not move(East)
        
        if game_complete:
            break

    game_complete = game_complete or not move_to_row(0, False)
    game_complete = game_complete or not move_to_col(0,False)
    
    if game_complete:
        break
        
change_hat(Hats.Straw_Hat)