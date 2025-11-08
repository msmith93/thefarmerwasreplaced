from wood import harvest_wood
from hay import harvest_hay
from carrot import harvest_carrot
from power import harvest_power
from pumpkin import harvest_pumpkin
from gold import harvest_gold
from weird_substance import harvest_weird_substance
from cacti import harvest_cacti

POWER_THRESHOLD = 250


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
	Unlocks.Mazes, Unlocks.Dinosaurs]

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
}
harvesting_order = [Items.Gold, Items.Weird_Substance, Items.Cactus, Items.Pumpkin, Items.Carrot, Items.Wood, Items.Hay]

def harvest_all(items_needed, unlock_num):
	if num_unlocked(Unlocks.Sunflowers) and num_items(Items.Power) < POWER_THRESHOLD:
		desired_sunflowers = POWER_THRESHOLD * 2 + (unlock_num * 30)

		curr_carrots = num_items(Items.Carrot)
		needed_carrots = desired_sunflowers // 3
		if curr_carrots < needed_carrots:
			harvest_carrot(needed_carrots - curr_carrots)
		harvest_power(desired_sunflowers)

	for item in harvesting_order:
		if item in items_needed:
			harvest_funcs[item](items_needed[item])

def unlock_wrapper(unlock_item, unlock_num):
	if unlock_item == Unlocks.Megafarm:
		pass
	unlock_cost = get_cost(unlock_item)
	harvest_all(unlock_cost, unlock_num)
	unlock(unlock_item)

for i in range(len(unlock_order)):
	unlck = unlock_order[i]
	unlock_wrapper(unlck, i)

while True:
	do_a_flip()