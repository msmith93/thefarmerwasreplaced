
filename = "f5"

sim_unlocks = Unlocks

sim_items = {Items.Carrot : 1000000, Items.Power : 1000000, Items.Fertilizer : 1000000}

sim_globals = {"a" : 13}
seed = 0
speedup = 1000

petal_mins = range(11,13)
water_thresholds = [0.475, 0.48, 0.485, 0.49, 0.495, 0.5, 0.505, 0.510, 0.515, 0.520, 0.525, 0.530, 0.535, 0.540, 0.545]

quick_print("petal_min,water_threshold,count,water,run_time")

for petal_min in petal_mins:
	for water_threshold in water_thresholds:
		quick_print(petal_min)
		quick_print(water_threshold)
		
		sim_globals = {"petal_min": petal_min, "water_threshold": water_threshold}
		run_time = simulate(filename, sim_unlocks, sim_items, sim_globals, seed, speedup)
		quick_print(run_time / 60)
		quick_print("-------")
