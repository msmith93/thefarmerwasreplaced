rows = 6
cols = 6

def plant_cacti():	
	clear()
	for i in range(6):
		for j in range(6):
			till()
			plant(Entities.Cactus)
			move(East)
		move(North)
		
def move_to_x_pos(x_target):
	x_curr = get_pos_x()
	moves_needed = x_target - x_curr
	if moves_needed > 0:
		dir = East
	else:
		dir = West
	for i in range(abs(moves_needed)):
		move(dir)

def move_to_y_pos(y_target):
	y_curr = get_pos_y()
	moves_needed = y_target - y_curr
	if moves_needed > 0:
		dir = North
	else:
		dir = South
	for i in range(abs(moves_needed)):
		move(dir)

def go_to_origin():
	move_to_x_pos(0)
	move_to_y_pos(0)

def sort_row():
	# Assume drone is at the first column
	for i in range(cols):
		swapped = False
		for j in range(0, cols - i - 1):
			move_to_x_pos(j)
			if measure() > measure(East):
				swap(East)
				swapped = True
		if not swapped:
			break

def sort_all_rows():
	move_to_x_pos(0)
	for i in range(rows):
		move_to_y_pos(i)
		sort_row()
		
def sort_col():
	# Assume drone is at the first row
	for i in range(rows):
		swapped = False
		for j in range(0, rows - i - 1):
			move_to_y_pos(j)
			if measure() > measure(North):
				swap(North)
				swapped = True
		if not swapped:
			break
			
def sort_all_cols():
	move_to_y_pos(0)
	for i in range(cols):
		move_to_x_pos(i)
		sort_col()
		
def sort_cacti():
	sort_all_rows()
	sort_all_cols()

while True:
	plant_cacti()		
	go_to_origin()
	sort_cacti()
	harvest()
