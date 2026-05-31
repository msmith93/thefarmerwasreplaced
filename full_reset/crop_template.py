# =============================================================================
# CROP HARVESTER TEMPLATE
# =============================================================================
# Copy this file to <your_crop>.py, rename the functions, and fill in the
# stub bodies. This file is NOT imported by anything, so it never affects a run.
#
# THE CONTRACT every harvest_<crop>(target) must satisfy:
#   1. On return, num_items(Items.<Crop>) must be at least `target` (a total, not
#      a delta). Loop until num_items reaches the target.
#   2. Acquire any prerequisite items yourself by calling their harvest_*
#      function(s) before you start (see step 1 below). Those functions also take
#      a target, so pass the absolute amount you need (no current/delta math).
#   3. If you change global farm state (e.g. set_world_size), restore it before
#      returning so the next crop starts from a known state.
#
# TO PLUG IN (see README.md for the full recipe):
#   - In full_reset.py:  from <your_crop> import harvest_<your_crop>
#   - Add  Items.<Crop> : harvest_<your_crop>  to the `harvest_funcs` dict
#   - Add  Items.<Crop>  to the `harvesting_order` list
# =============================================================================

# Import the harvest_* functions for any items this crop depends on.
# Example:
# from carrot import harvest_carrot

# Module-level world_size cache. Drone functions can't take arguments, so the
# convention here is to stash the current world size in a global and read it
# from inside drone_action(). Refresh it at the top of harvest_<crop>().
world_size = 1


def plant_stuff():
	# Per-tile logic for the drone's CURRENT square. Customize for your crop.
	# Typical steps: till the ground if needed, harvest what's ready, then
	# (re)plant. Keep this branchless and fast; it runs once per tile.
	#
	# Example shape:
	#   if can_harvest():
	#       harvest()
	#   if get_ground_type() != Grounds.Soil:
	#       till()
	#   plant(Entities.<Crop>)
	pass


def drone_action():
	# One drone's job: walk a single column, doing plant_stuff() on each tile.
	# Used in megafarm mode where one drone is spawned per column.
	global world_size

	for j in range(world_size):
		plant_stuff()
		move(North)


def harvest_crop(target_crop):
	# Rename to harvest_<your_crop> and replace Items.Crop / Entities.Crop below.
	# target_crop is a TOTAL: ensure num_items(Items.Crop) >= target_crop.
	global world_size

	world_size = get_world_size()

	# ---- STEP 1: ensure prerequisite items -------------------------------
	# Acquire anything you consume (wood, hay, carrots, power, ...) by calling
	# the relevant harvest_* function with the absolute amount you need. Read
	# per-plant quantities from get_cost(Entities.Crop). Example:
	#   cost = get_cost(Entities.Crop)
	#   harvest_carrot(target_crop * cost[Items.Carrot] + cost[Items.Carrot])

	# ---- STEP 2: harvest until the target is reached ---------------------
	# Branch on Megafarm so you can fan out with drones once it's unlocked,
	# and fall back to a single-drone loop before then.
	if num_unlocked(Unlocks.Megafarm):
		while num_items(Items.Crop) < target_crop:
			for i in range(world_size):
				spawn_drone(drone_action)
				while num_drones() >= max_drones():
					pass
				move(East)
	else:
		while num_items(Items.Crop) < target_crop:
			plant_stuff()

			if get_pos_y() == 0 and num_unlocked(Unlocks.Expand) > 1:
				move(East)
			move(North)

	# ---- STEP 3: restore any global state you changed --------------------
	# e.g. set_world_size(original_world_size) if you called set_world_size().
