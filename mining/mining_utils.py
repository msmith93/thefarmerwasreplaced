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
		
	while curr_z < target_z:
		place(Grounds.Dirt)
		curr_z = get_pos_z()
	return True

def dig_to_ground_type(ground_type):
	while get_ground_type() != ground_type:
		dig()
