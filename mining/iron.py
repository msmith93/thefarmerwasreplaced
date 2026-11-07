from mining_utils import dig_to_ground_type

clear()
jump(Unlocks.Iron)

while True:
	iron_dir = prospect_iron()
	while iron_dir:
		move(iron_dir)
		while get_ground_type() == Grounds.Quartz:
			dig()
		iron_dir = prospect_iron()
	
	dig_to_ground_type(Grounds.Iron)
	dig() # get the iron the drone is above
	