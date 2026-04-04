# Iteration 21: Mixed Column 0 (6 grass + 2 bush) + Optimized Loop
# Plant 2 bushes at (0,6) and (0,7) to reduce grass-in-candidate collisions.
# Each grass tile at rows 0-5 gets ~3 grass candidates vs 6 → P(match) rises to ~28-29%.
# Visit 6 grass tiles per cycle, skip 2 bush rows with extra moves.
# Uses nested-if re-roll check and for-loop (minimal AST overhead).

SIZE = get_world_size()

# Plant bushes on columns 1-7
move(East)
for x in range(SIZE - 1):
    for y in range(SIZE):
        plant(Entities.Bush)
        move(North)
    move(East)

# Plant bushes at column 0, rows 6-7
for y in range(6):
    move(North)
plant(Entities.Bush)
move(North)
plant(Entities.Bush)
move(North)
# Now at (0,0)

_B = Entities.Bush
def run():
    for _ in range(210):
        for y in range(6):
            while True:
                harvest()
                companion, comp_pos = get_companion()
                if companion == _B:
                    if comp_pos[0]:
                        break
            move(North)
        # Skip bush rows 6,7 → back to row 0
        move(North)
        move(North)

run()
