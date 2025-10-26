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
	


def move_char(dir_char):
	if dir_char == "E":
		move(East)
	elif dir_char == "W":
		move(West)
	elif dir_char == "S":
		move(South)
	elif dir_char == "N":
		move(North)
	
def move_str(dir_str):
	for ch in dir_str:
		move_char(ch)
		
DRAW_ACTIONS = [
	"PBush",
	"PGrass",
	"PSunflower",
]

def draw(action):
	while get_water() < 0.75:
		use_item(Items.Water)
	if get_ground_type() != Grounds.Soil:
		till()
		
	if action == "PBush":
		plant(Entities.Bush)
	elif action == "PGrass":
		plant(Entities.Grass)
	elif action == "PSunflower":
		plant(Entities.Sunflower)
	elif action == "PCarrot":
		plant(Entities.Carrot)

def move_to_letter_start(moves_needed, scale):
	for move in moves_needed:
		dir_str, moves = move
		scaled_moves = scale * moves
		for i in range(scaled_moves):
			move_str(dir_str)


# "Pre" -> follow directions to where the letter starts
# "S" == South, "E" == East, etc.
# "SE" == SouthEast, "NW" == NorthWest, etc.

####################################### The lists after "Pre" are where the drone draws the letter
U = [("Pre", [("N", 6)]),				("S", 5), ("SE", 1), ("E", 1), ("NE", 1), ("N", 5)]
####################################### For I, the drone just draws a line going 6 moves South
I = [("Pre", [("N", 6)]), 				("S", 6)]

####################################### For L, the drone just draws a line going 6 moves South, then 4 moves East
L = [("Pre", [("N", 6)]),				("S", 6), ("E", 3)]


# letter_mapping is shown above
def spell_letter(letter_mapping, draw_action, scale=1):
	first_draw = True
	
	if letter_mapping[0][0] == "Pre":
		moves_needed = letter_mapping.pop(0)[1]
		move_to_letter_start(moves_needed, scale)
		
	for draw_info in letter_mapping:
		dir_str, moves = draw_info
		scaled_moves = scale * moves
		for i in range(scaled_moves):
			draw(draw_action)
			move_str(dir_str)
		first_draw = False
	
	draw(draw_action)


T = [("Pre", [("N", 6)]), 				("E", 4), ("W", 2), ("S", 6)]
S = [									("E", 2), ("NE", 1), ("N", 1), ("NW", 1), ("W", 1), ("NW", 1), ("N", 1),
											("NE", 1), ("E", 2)]
B = [("Pre", [("N", 6)]),				("S", 6), ("E", 2), ("NE", 1), ("N", 1), ("NW", 1), ("W", 2), ("E", 2),
											("NE", 1), ("N", 1), ("NW", 1), ("W", 2)]
C = [("Pre", [("N", 1), ("E", 3)]),		("SW", 1), ("W", 1), ("NW", 2), ("N", 2), ("NE", 2), ("E", 1), ("SE", 1)]
P = [("Pre", [("N", 6)]),				("S", 6), ("N", 6), ("E", 2), ("SE", 1), ("S", 1), ("SW", 1), ("W", 2)]

def spell_B(entity, scale=1):
	global B
	spell_letter(B, entity, scale)
def spell_I(entity, scale=1):
	global I
	spell_letter(I, entity, scale)
def spell_T(entity, scale=1):
	global T
	spell_letter(T, entity, scale)
def spell_S(entity, scale=1):
	global S
	spell_letter(S, entity, scale)
def spell_C(entity, scale=1):
	global C
	spell_letter(C, entity, scale)
def spell_U(entity, scale=1):
	global U
	spell_letter(U, entity, scale)
def spell_L(entity, scale=1):
	global L
	spell_letter(L, entity, scale)
def spell_P(entity, scale=1):
	global P
	spell_letter(P, entity, scale)


def dance_dance():
	while True:
		do_a_flip()
		pet_the_piggy()
