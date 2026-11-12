from mining_utils import flatten_to_ground_types

set_world_size(200)
world_size = get_world_size()

jump(Unlocks.Dynamite)

flatten_to_ground_types({Grounds.Dynamite, Grounds.Soot})

safe_blocks = {
	(get_pos_x(), get_pos_y()): 1
}
unsafe_blocks = {}

def check_block(block_pos, safe_blocks, unsafe_blocks, unsure_blocks):
	total_safe = 0
	total_unsafe = 0

	if block_pos[0] >= world_size or block_pos[0] < 0:
		return (1, 0)

	if block_pos[1] >= world_size or block_pos[1] < 0:
		return (1, 0)

	
	if block_pos in safe_blocks:
		total_safe += 1
	elif block_pos in unsafe_blocks:
		total_unsafe += 1
	else:
		if block_pos not in unsure_blocks:
			unsure_blocks.append(block_pos)
	
	return (total_safe, total_unsafe)
		

def get_surrounding_safe(x, y):
	total_safe = 0
	total_unsafe = 0
	unsure_blocks = []
	
	for dx in [-1, 0, 1]:
		for dy in [-1, 0, 1]:
			if dx == 0 and dy == 0:
				continue
			result = check_block((x + dx, y + dy), safe_blocks, unsafe_blocks, unsure_blocks)
			total_safe += result[0]
			total_unsafe += result[1]

	return total_safe, total_unsafe, unsure_blocks

def run_dyna_col(safe_blocks, unsafe_blocks):
	new_safe_blocks = []
	new_unsafe_blocks = []
	for j in range(world_size):
		total_safe = 0
		curr_x = get_pos_x()
		curr_y = get_pos_y()
		
		if get_ground_type() == Grounds.Dynamite:
			if (curr_x, curr_y) in safe_blocks:
				dig()
			elif (curr_x, curr_y) in unsafe_blocks:
				place(Grounds.Rock)
		
		if get_ground_type() == Grounds.Soot:
			curr_block_m = measure()

			if curr_block_m == None:
				return [], []
				
			total_safe, total_unsafe, unsure_blocks = get_surrounding_safe(curr_x, curr_y)

			if len(unsure_blocks) > 0 and len(unsure_blocks) == curr_block_m - total_unsafe:
				for unsure_block in unsure_blocks:
					if unsure_block not in unsafe_blocks:
						new_unsafe_blocks += [unsure_block]
			elif total_unsafe == curr_block_m:
				for unsure_block in unsure_blocks:
					if unsure_block not in safe_blocks:
						new_safe_blocks += [unsure_block]
		
		move(East)

	return new_safe_blocks, new_unsafe_blocks



def run_dynamite(safe_blocks, unsafe_blocks):
	drone_ids = []

	while True:

		for row in range(world_size):
			while num_drones() >= max_drones():
				pass

			drone_id = spawn_drone(run_dyna_col, safe_blocks, unsafe_blocks)
			drone_ids.append(drone_id)
			
			move(North)

		for drone in drone_ids:
			new_safe_blocks, new_unsafe_blocks = wait_for(drone)

			for new_safe_block in new_safe_blocks:
				if new_safe_block not in safe_blocks:
					safe_blocks[new_safe_block] = 1
			for new_unsafe_block in new_unsafe_blocks:
				if new_unsafe_block not in unsafe_blocks:
					unsafe_blocks[new_unsafe_block] = 1

run_dynamite(safe_blocks, unsafe_blocks)
		
		
	
	

