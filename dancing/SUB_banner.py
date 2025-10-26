clear()
filename = "draw"
sim_unlocks = Unlocks
sim_items = {
	Items.Power: 1000000,
	Items.Wood: 1000000,
	Items.Carrot: 1000000,
	Items.Water: 10000000,
	Items.Fertilizer: 10000000,
}
world_size = 32
sim_globals = {
	"world_size": world_size,
	"draw_string": "SUB",
}
seed = 0
speedup = 1000

x_offset = 0
x_incr = -1
y_offset = 1
y_offset_bounds = (0, 3)
y_incr = 0
while True:
	sim_globals["x_offset"] = x_offset % world_size
	sim_globals["y_offset"] = y_offset # % not needed b/c y_offset_bounds
	simulate(filename, sim_unlocks, sim_items, sim_globals, seed, speedup)
	x_offset += x_incr
	if y_offset >= y_offset_bounds[1]:
		y_incr *= -1
	elif y_offset <= y_offset_bounds[0]:
		y_incr *= -1
	y_offset += y_incr

