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
	if action == "Till" and get_ground_type() != Grounds.Soil:
		till()
	elif action == "PBush":
		plant(Entities.Bush)
	elif action == "PGrass":
		plant(Entities.Grass)
	elif action == "PSunflower":
		plant(Entities.Sunflower)

def spell_letter(letter_mapping, draw_action, scale=1):
	first_draw = True
	rounded = False
		
	for letter_attrs in letter_mapping:
		prev_rounded = rounded
		rounded = False
		letter_attrs_cnt = len(letter_attrs)
		if letter_attrs_cnt == 2:
			dir_str, moves = letter_attrs
		elif letter_attrs_cnt == 3:
			dir_str, moves, rounded = letter_attrs
		scaled_moves = scale * moves
		for i in range(scaled_moves):
			if i == 0 and i != scaled_moves and prev_rounded and not first_draw:
				move_str(dir_str)
				continue
			draw(draw_action)
			move_str(dir_str)
		first_draw = False
	
	draw(draw_action)

S = [("E", 3), ("NE", 1), ("N", 1), ("NW", 1), ("W", 2), ("NW", 1), ("N", 1), ("NE", 1), ("E", 3)]
def spell_S(entity, scale=1):
	global S
	spell_letter(S, entity, scale)
	
U = [("S", 5), ("SE", 1), ("E", 1), ("NE", 1), ("N", 5)]
def spell_U(entity, scale=1):
	global U
	spell_letter(U, entity, scale)

B = [("S", 6), ("E", 2), ("NE", 1), ("N", 1), ("NW", 1), ("W", 2), ("E", 2), ("NE", 1), ("N", 1), ("NW", 1), ("W", 2)]
def spell_B(entity, scale=1):
	global B
	spell_letter(B, entity, scale)

def dance_dance():
	while True:
		do_a_flip()
		pet_the_piggy()
