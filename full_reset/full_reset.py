# =============================================================================
# full_reset — pluggable starting point
# =============================================================================
# A generic driver that buys a sequence of Unlocks, harvesting whatever each one
# costs along the way. To make it your own, fill in the three CONFIG sections
# below and (optionally) the pre_harvest hook, then run this file in-game.
#
#   - crop_template.py    : a stub for writing one crop's harvest_<crop>(num)
#   - full_reset_solution.py : a complete worked example of everything below
#   - README.md           : the full guide
# =============================================================================

# ---- IMPORT your crop harvest functions -------------------------------------
# Each must satisfy the harvest_<crop>(target) contract (see crop_template.py):
# on return, num_items(Items.<Crop>) is at least target (a total, not a delta).
# from wood import harvest_wood
# from carrot import harvest_carrot


# ---- CONFIG 1: the unlock strategy ------------------------------------------
# The ordered list of Unlocks to buy. The driver buys each in turn, harvesting
# whatever it costs first.
unlock_order = [
	# Unlocks.Speed, Unlocks.Expand, Unlocks.Plant, ...
]


# ---- CONFIG 2: map each Item to the function that harvests it ----------------
harvest_funcs = {
	# Items.Wood:   harvest_wood,
	# Items.Carrot: harvest_carrot,
}


# ---- CONFIG 3: order to gather items within a single unlock step ------------
# Only items present in a given unlock's cost are harvested. List raw inputs
# LAST: a crop tops up and then consumes its inputs while farming, so anything
# also owed directly to the unlock (e.g. Wood, Hay) must be re-gathered after.
harvesting_order = [
	# Items.Carrot, Items.Wood, Items.Hay, ...
]


# ---- OPTIONAL: pre-harvest hook ---------------------------------------------
# Runs once per unlock step BEFORE the per-item harvesting loop. Use it to
# stockpile something proactively (full_reset_solution.py uses it to batch
# sunflower/power). Leave it as a no-op if you don't need it.
def pre_harvest(items_needed, unlock_num):
	pass


# =============================================================================
# Framework (you usually don't need to edit below here)
# =============================================================================
def harvest_all(items_needed, unlock_num):
	pre_harvest(items_needed, unlock_num)

	# Pass the cost as a target: ensure each costed item reaches that amount.
	for item in harvesting_order:
		if item in items_needed:
			harvest_funcs[item](items_needed[item])

def unlock_wrapper(unlock_item, unlock_num):
	unlock_cost = get_cost(unlock_item)
	harvest_all(unlock_cost, unlock_num)
	unlock(unlock_item)

for i in range(len(unlock_order)):
	unlock_wrapper(unlock_order[i], i)
