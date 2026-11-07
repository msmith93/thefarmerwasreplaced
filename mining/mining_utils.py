def dig_to_z(target_z):
	curr_z = get_pos_z()
	if curr_z < target_z:
		return False
		
	while curr_z > target_z:
		dig()
		curr_z = get_pos_z()
	return True

def climb_to_z(target_z):
	curr_z = get_pos_z()
	while curr_z > target_z:
		dig()
		curr_z = get_pos_z()
		
	if curr_z < target_z:
		hover(target_z)
	return True

def goto(x, y):
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)

def dig_to_ground_type(ground_type):
	while get_ground_type() != ground_type:
		dig()

def dig_to_ground_types(ground_types):
	while get_ground_type() not in ground_types:
		dig()