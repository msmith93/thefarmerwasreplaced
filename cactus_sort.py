cols = 6
rows = 6

def grow_cactus_row():
	for j in range(cols):
		till()
		plant(Entities.Cactus)
		move(East)
		
		
def grow_all_cactuses():
	clear()
	for i in range(rows):
		grow_cactus_row()
		move(North)
		
		
def move_drone_to_x_pos(x_target):
	# Assume drone is on first row
	x_curr = get_pos_x()
	moves_needed = x_target - x_curr
	if moves_needed > 0:
		dir = East
	else:
		dir = West
	
	for i in range(abs(moves_needed)):
		move(dir)



def sort_row():
	row_nums = list()
	for i in range(cols):
		row_nums.append(measure())
		move(East)
	
	for i in range(cols):
		swapped = False
		for j in range(0, cols - i - 1):
			move_drone_to_x_pos(j)
			if row_nums[j] > row_nums[j + 1]:
				swap(East)
				row_nums[j], row_nums[j + 1] = row_nums[j + 1], row_nums[j]
				swapped = True
		if not swapped:
			break


clear()

for y in range(cols):
	grow_cactus_row()
	move_drone_to_x_pos(0)
	sort_row()
	move(North)
