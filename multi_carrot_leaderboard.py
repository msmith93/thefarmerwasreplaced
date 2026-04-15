TARGET_CARROTS = 2000000000

world_size = get_world_size()


def populate_curr_companions():
	global world_size

	# curr_companions data structure to store companion locations and companion types for one column
	#   each column list: 32 row square data of (crop type, used_by_refcount)
	curr_companions = list()

	for i in range(world_size):
		curr_companions.append([Entities.Grass, 0])
	return curr_companions

def goto(tx, ty):
	cx = get_pos_x()
	cy = get_pos_y()
	dx = (tx - cx) % world_size
	dy = (ty - cy) % world_size
	if dx <= (world_size // 2):
		for _ in range(dx):
			move(East)
	else:
		for _ in range(world_size - dx):
			move(West)
	if dy <= (world_size // 2):
		for _ in range(dy):
			move(North)
	else:
		for _ in range(world_size - dy):
			move(South)

def plant_companion(comp_type, comp_pos):
	goto(comp_pos[0], comp_pos[1])

	harvest()
	plant(comp_type)

def comp_valid(comp_type, comp_pos, curr_companions):
	# Companion is valid when:
	#   1. the comp column is one left of current column
	#   2. AND
	#       the comp type matches existing comp type of a used comp position (check curr_companions)
	#       OR the comp row is not used
	
	curr_x_pos = get_pos_x()
	if curr_x_pos == 0:
		comp_pos_good = 31
	else:
		comp_pos_good = curr_x_pos - 1
	
	if comp_pos[0] != comp_pos_good:
		return False
	
	if curr_companions[comp_pos[1]][0] == comp_type:
		# The companion is already there! No need to spawn a drone to plant it!
		curr_companions[comp_pos[1]][1] += 1        # Increase used_by ref count
		return True

	if curr_companions[comp_pos[1]][1] == 0:
		while not spawn_drone(plant_companion, comp_type, comp_pos):
			pass
		curr_companions[comp_pos[1]][1] += 1        # Increase used_by ref count
		curr_companions[comp_pos[1]][0] = comp_type
		return True
	

# Ensure current carrot square has a good companion
# Update curr_companions list to mark the current carrot's companion with the companion type and is_used == True
def ensure_proper_companion(curr_companions):
	
	curr_x_pos = get_pos_x()

	if curr_x_pos == 0:
		comp_pos_good = 31
	else:
		comp_pos_good = curr_x_pos - 1
	
	comp_type, comp_pos = get_companion()
	while not comp_valid(comp_type, comp_pos, curr_companions):
		harvest()
		plant(Entities.Carrot)
		comp_type, comp_pos = get_companion()
	

def drone_till_and_plant():
	global world_size

	curr_companions = populate_curr_companions()

	while num_items(Items.Carrot) < TARGET_CARROTS:
		
		if get_ground_type() != Grounds.Soil:
			till()
		else:
			comp_type, comp_pos = get_companion()
			curr_companions[comp_pos[1]][1] -= 1        # Decrement used_by ref count

			while not can_harvest():
				pass

			harvest()
		
		if get_water() < 0.5:
			use_item(Items.Water)

		plant(Entities.Carrot)

		ensure_proper_companion(curr_companions)
		
		move(North)


child_drone_ids = list()

for i in range(world_size / 2 - 1):
	child_drone_id = spawn_drone(drone_till_and_plant)
	child_drone_ids.append(child_drone_id)
	move(East)
	move(East)

drone_till_and_plant()

