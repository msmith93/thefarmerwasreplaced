def goto_x(x):
	curr_x = get_pos_x()
	moves = abs(x - curr_x)
	if x > curr_x:
		dir = East
	else:
		dir = West
	for _ in range(moves):
		move(dir)
		
def goto_y(y):
	curr_y = get_pos_y()
	moves = abs(y - curr_y)
	if y > curr_y:
		dir = North
	else:
		dir = South
	for _ in range(moves):
		move(dir)

def get_into_position(dance_id, world_size):
	x = dance_id % world_size
	y = dance_id // world_size
	goto_x(x)
	goto_y(y)
	
HATS = [Hats.Gold_Trophy_Hat, Hats.Wizard_Hat, Hats.Traffic_Cone_Stack, Hats.Silver_Trophy_Hat, Hats.Golden_Cactus_Hat]
NUM_HATS = 5

def wear_costume(dance_id):
	hat = HATS[dance_id % NUM_HATS]
	change_hat(hat)

def dance_dance():
	while True:
		do_a_flip()
		pet_the_piggy()
