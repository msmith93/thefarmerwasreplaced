from wood import harvest_wood
from hay import harvest_hay
from carrot import harvest_carrot
from power import harvest_power
from pumpkin import harvest_pumpkin

POWER_THRESHOLD = 100

harvesting_order = [Items.Pumpkin, Items.Carrot, Items.Wood, Items.Hay]
unlock_order = [Unlocks.Speed, Unlocks.Expand, 
	Unlocks.Plant, Unlocks.Expand, Unlocks.Speed,
	Unlocks.Carrots, Unlocks.Expand, Unlocks.Speed,
	Unlocks.Watering, Unlocks.Trees, Unlocks.Grass,
	Unlocks.Trees, Unlocks.Carrots, Unlocks.Sunflowers,
	Unlocks.Expand, Unlocks.Grass,
	Unlocks.Speed, Unlocks.Fertilizer, Unlocks.Watering,
	Unlocks.Pumpkins, Unlocks.Polyculture, Unlocks.Speed,
	Unlocks.Carrots, Unlocks.Watering, Unlocks.Fertilizer,
	Unlocks.Trees, Unlocks.Pumpkins]

harvest_funcs = {
#   Item type       :   harvest func,
	Items.Wood      :   harvest_wood,
	Items.Hay       :   harvest_hay,
	Items.Carrot    :   harvest_carrot,
	Items.Pumpkin	:   harvest_pumpkin,
	Items.Power		: 	harvest_power,
}

def harvest_all(items_needed):
	if num_unlocked(Unlocks.Sunflowers) and num_items(Items.Power) < POWER_THRESHOLD:
		harvest_power(POWER_THRESHOLD * 5)

	for item in harvesting_order:
		if item in items_needed:
			harvest_funcs[item](items_needed[item])

def unlock_wrapper(unlock_item):
	unlock_cost = get_cost(unlock_item)
	harvest_all(unlock_cost)
	unlock(unlock_item)

for unlck in unlock_order:
	unlock_wrapper(unlck)

while True:
	do_a_flip()