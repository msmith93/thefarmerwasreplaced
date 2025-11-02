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

while True:
	simulate(filename, sim_unlocks, sim_items, sim_globals, seed, speedup)

