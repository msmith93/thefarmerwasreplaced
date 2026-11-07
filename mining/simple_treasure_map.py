from mining_utils import dig_to_z, goto, dig_to_ground_types

jump(Unlocks.Treasure_Map)
dig_to_ground_types([Grounds.Basalt])
current_level = get_pos_z()
map_pos = measure()
goto(map_pos[0], map_pos[1])
dig_to_z(current_level - 1)

treasure_path = measure()
current_level = get_pos_z()

step_mapping = {
	"E": East,
	"W": West,
	"N": North,
	"S": South
}

horiz_diff = 0
vert_diff = 0
m = 0

for step in treasure_path:
	if step == "D":
		dig()
		current_level = get_pos_z()
	else:
		move(step_mapping[step])
		dig_to_z(current_level)
		
harvest()