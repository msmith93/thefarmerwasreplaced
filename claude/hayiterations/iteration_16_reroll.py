# Iteration 16: Companion Re-Roll (inspired by human_hay.py)
# Key insight: harvest() on regrowing grass costs 200 ticks, yields 0 hay,
# but RE-ROLLS the companion. By repeatedly harvesting until the companion
# is Bush at a bush tile, we guarantee 100% polyculture rate.
#
# Mechanic: previous visit's re-roll sets companion to match. On next visit,
# harvest() uses that matching companion → 81,920 hay. Then re-roll for
# next visit.
#
# P(match per re-roll) = 18/24 * 1/3 = 25% → avg 4 attempts (3 re-rolls).
# Per tile: harvest(200) + 3*(harvest(200) + get_companion(1) + checks) + move(200) ≈ 1,029 ticks.
# 100% poly → 81,920 hay per productive harvest.
# Efficiency: 81,920 / 1,029 = 79.6 hay/tick (vs 52.2 in iter 12).
#
# 8 tiles, cycle = 1.2s >> 0.5s grass grow → no water needed.
# Harvests needed: ceil(100M / 81920) = 1,221.
# Estimated time: ~207s.

SIZE = get_world_size()
goal = 100000000

# Setup: plant bushes on columns 1-7
move(East)
for x in range(SIZE - 1):
    for y in range(SIZE):
        plant(Entities.Bush)
        move(North)
    move(East)

# Main loop: harvest + re-roll companions + move
def run():
    while True:
        harvest()
        if num_items(Items.Hay) >= goal:
            return
        companion, comp_pos = get_companion()
        while companion != Entities.Bush or comp_pos[0] == 0:
            harvest()
            companion, comp_pos = get_companion()
        move(North)

run()
