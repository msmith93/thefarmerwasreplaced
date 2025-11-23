clear()
world_size = get_world_size()

curr_col = []


frames = [[4294959103, 3892289535, 3825147903, 3787202553, 3758103491, 3758096903, 3758096391, 3758096399, 4026531855, 4026531871, 805306431, 63, 2248147071, 2248159359, 2264952832, 2273439744, 3280199683, 3221340167, 3254779919, 3279970367, 3825197183, 3791634559, 3774840959, 3762159871, 3758096639, 3758096639, 3758096511, 3821011071, 4294951039, 4294959231, 4294963327, 4294966527]]


def run_col():
    global curr_col

    for pixel in curr_col:
        if pixel:
            if get_ground_type() == Grounds.Soil:
                till()
        else:
            if get_ground_type() != Grounds.Soil:
                till()

        move(East)


def wait_for_drones(drones):
    for drone in drones:
        wait_for(drone)

def int_to_binary(n):
    if n == 0:
		return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	binary_string = []
	while n > 0:
		binary_string = [n % 2] + binary_string
		n //= 2
    
    while len(binary_string) < 32:
        binary_string = [0] + binary_string
	return binary_string

move(South)

drones = []

for i in range(100):
    wait_for_drones(drones)

    for frame in frames:
        for column in frame:
            column_list = int_to_binary(column)
            curr_col = column_list

            while num_drones() >= max_drones():
                pass

            drones.append(spawn_drone(run_col))
            move(South)
        
        # Only if you want to pause between images
        #wait_for_drones(drones)

