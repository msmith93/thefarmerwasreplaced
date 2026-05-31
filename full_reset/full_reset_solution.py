# =============================================================================
# full_reset_solution — a complete worked example of the full_reset.py skeleton
# =============================================================================
# This is the reference strategy. It is a concrete instantiation of the generic
# skeleton in full_reset.py: same framework (harvest_all / unlock_wrapper /
# driver), with the three CONFIG sections filled in and a real pre_harvest hook.
#
# Use it as a model for your own full_reset.py. See README.md.
# =============================================================================

from wood import harvest_wood
from hay import harvest_hay
from carrot import harvest_carrot
from power import harvest_power
from pumpkin import harvest_pumpkin
from gold import harvest_gold
from weird_substance import harvest_weird_substance
from cacti import harvest_cacti
from bone import harvest_bone

POWER_THRESHOLD = 250

# CONFIG 1: ordered list of Unlocks to buy.
unlock_order = [Unlocks.Speed, Unlocks.Expand, 
	Unlocks.Plant, Unlocks.Expand, Unlocks.Speed,
	Unlocks.Carrots, Unlocks.Expand, Unlocks.Speed,
	Unlocks.Watering, Unlocks.Trees, Unlocks.Grass,
	Unlocks.Trees, Unlocks.Carrots, Unlocks.Sunflowers,
	Unlocks.Expand, Unlocks.Grass,
	Unlocks.Speed, Unlocks.Fertilizer, Unlocks.Watering,
	Unlocks.Pumpkins, Unlocks.Polyculture, Unlocks.Speed,
	Unlocks.Carrots, Unlocks.Watering, Unlocks.Fertilizer,
	Unlocks.Trees, Unlocks.Pumpkins, Unlocks.Fertilizer, 
	Unlocks.Grass, Unlocks.Trees, Unlocks.Watering, 
	Unlocks.Carrots, Unlocks.Pumpkins, Unlocks.Expand,
	Unlocks.Cactus, Unlocks.Fertilizer, Unlocks.Expand,
	Unlocks.Carrots, Unlocks.Pumpkins, Unlocks.Expand,
	Unlocks.Mazes, Unlocks.Megafarm, Unlocks.Megafarm,
	Unlocks.Cactus, Unlocks.Mazes, Unlocks.Megafarm,
	Unlocks.Mazes, Unlocks.Dinosaurs, Unlocks.Cactus,
	Unlocks.Mazes, Unlocks.Dinosaurs, Unlocks.Hats,
	Unlocks.Polyculture, Unlocks.Polyculture, Unlocks.Grass,
	Unlocks.Trees, Unlocks.Carrots, Unlocks.Grass, 
	Unlocks.Trees, Unlocks.Carrots, Unlocks.Grass, 
	Unlocks.Trees, Unlocks.Carrots, Unlocks.Grass, Unlocks.Grass,
	Unlocks.Megafarm, Unlocks.Megafarm,
	Unlocks.Trees, Unlocks.Carrots, Unlocks.Pumpkins,
	Unlocks.Dinosaurs, Unlocks.Dinosaurs,
	Unlocks.Cactus, Unlocks.Mazes, Unlocks.Mazes,
	Unlocks.Leaderboard
	]

# CONFIG 2: map each Item to the function that harvests it.
harvest_funcs = {
#   Item type       :   harvest func,
	Items.Wood      :   harvest_wood,
	Items.Hay       :   harvest_hay,
	Items.Carrot    :   harvest_carrot,
	Items.Pumpkin	:   harvest_pumpkin,
	Items.Power		: 	harvest_power,
	Items.Gold		:   harvest_gold,
	Items.Weird_Substance : harvest_weird_substance,
	Items.Cactus    :   harvest_cacti,
	Items.Bone		:	harvest_bone,
}

# CONFIG 3: order to gather items within one unlock step.
harvesting_order = [Items.Bone, Items.Gold, Items.Weird_Substance, Items.Cactus, Items.Pumpkin, Items.Carrot, Items.Wood, Items.Hay]

# pre_harvest hook: runs once per unlock step before the per-item loop.
# Here it proactively batches sunflowers/power so power stays above a threshold.
# Calls use the target contract: pass the absolute amount you want on hand.
def pre_harvest(items_needed, unlock_num):
	if num_unlocked(Unlocks.Sunflowers) and num_items(Items.Power) < POWER_THRESHOLD:
		desired_sunflowers = POWER_THRESHOLD * 2 + (unlock_num * 30)

		harvest_carrot(desired_sunflowers // 3)
		harvest_power(desired_sunflowers)

# ---- framework (shared with full_reset.py; usually no need to edit) ----
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

do_a_flip()
