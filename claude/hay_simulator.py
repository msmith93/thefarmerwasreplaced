#!/usr/bin/env python3
"""
hay_simulator.py -- Hay_Single Leaderboard Simulator
for "The Farmer Was Replaced"

Simulates the Hay_Single leaderboard conditions:
  - 8x8 farm, single drone, all unlocks at max level
  - Starting inventory: lots of power (exact amount TBD -- needs calibration)
  - Win condition: num_items(Items.Hay) >= 100_000_000 (script must terminate itself)

Hay / Grass mechanics:
  - Grass (Entities.Grass) grows AUTOMATICALLY on Grounds.Grassland (default ground)
  - NO planting required -- grass regrows after each harvest
  - NO death -- grass never dies
  - NO mega-group mechanic -- each tile is independent
  - Harvesting a grown grass tile yields GRASS_YIELD_BASE * GRASS_YIELD_MULTIPLIER hay
  - After harvest, tile immediately begins regrowing (new random grow time assigned)
  - Tilling converts Grassland -> Soil, stopping auto-regrowth (avoid!)
  - Average grow time: 0.5s (exact range TBD -- needs calibration)

Calibration status (*** = confirmed from real game, ??? = placeholder):
  GRASS_GROW_TIME            *** (0.5s; calibrated -- all 20 real cycles = exactly 0.5s)
  GRASS_YIELD_BASE           *** (1 hay per tile at base, from docs)
  GRASS_YIELD_MULTIPLIER     *** (512; calibrated -- 20/20 harvests consistent)
  STARTING_POWER             *** (nonzero; avg sweep 2.37s matches powered ~2.4s)
  POLYCULTURE_MULTIPLIER     *** (160; calibrated -- 81920 / 512)
  companion re-roll          *** (re-rolls on EVERY harvest(), even regrowing grass)
  harvest() on regrowing     *** (costs 200 ticks, returns True, re-rolls companion, yields 0 hay)
  measure() on grass         *** (returns None; confirmed in calibration)
  water decay variance       *** (deterministic; apparent variance is get_water() rounding artifact)
  TICKS_PER_SECOND_POWERED   *** (6075; calibrated from 100-move timing in real game)
  REAL_GAME_SCALE_FACTOR     ~2.0x (inherited from pumpkins; needs hay-specific verification)

Usage:
    python hay_simulator.py --script myscript.py --iterations 100 --output details.json

Options:
    --script PATH       Path to the farming script to simulate (required)
    --iterations N      Number of simulation runs (default: 1)
    --output PATH       Output JSON file path (default: output.json)
    --timeout SECONDS   Per-run timeout in simulated seconds (default: 3600)
    --seed N            Base random seed; each run uses seed+i (default: random)
    --quiet             Suppress per-iteration progress output
"""

import argparse
import ast
from collections import defaultdict
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# CONFIGURATION (*** = confirmed, ??? = placeholder)
# ============================================================

WORLD_SIZE = 8
WIN_CONDITION_HAY = 100_000_000  # *** from leaderboard.md

# Grass mechanics
# grow time range: calibrated -- all 20 cycles returned exactly 0.5s
GRASS_GROW_TIME           = 0.5    # *** calibrated -- all 20 real cycles = exactly 0.5s
GRASS_YIELD_BASE          = 1      # *** base yield per tile (1 hay)
GRASS_YIELD_MULTIPLIER    = 512    # *** calibrated: 512 hay per harvest (20/20 consistent)

# Leaderboard starting inventory (Hay_Single)
# "starts with all unlocks, resources needed to grow, and lots of power"
# Grass needs no planting resources; drone starts with lots of power.
STARTING_POWER  = 1_000_000_000   # ??? assumed large; calibration will confirm
STARTING_HAY    = 0

# Tick / speed system (calibrated from pumpkins/sunflowers)
TICKS_PER_SECOND_UNPOWERED = 3037.0
TICKS_PER_SECOND_POWERED   = 6075.0   # *** calibrated from real game (was 6030)
POWER_CONSUMPTION_ACTIONS  = 30   # 1 power consumed every 30 drone actions

# Water system (all Watering upgrades at max)
WATER_TANKS_PER_10S = 256
WATER_DECAY_RATE    = 0.01
WATER_GROWTH_MIN    = 1.0
WATER_GROWTH_MAX    = 5.0

# Fertilizer
FERTILIZER_PER_10S        = 8
FERTILIZER_GROW_REDUCTION = 2.0   # seconds of grow time removed per use (same as pumpkins)

# Polyculture
# At max unlock level the multiplier is unknown -- needs calibration.
# The companion mechanic multiplies yield when the correct companion plant is present.
# "Before polyculture is unlocked, the yield multiplier is 5. It doubles every time you upgrade."
# Placeholder: 5 (base single-level multiplier). Update after calibration.
# Possible max-level values: 5, 10, 20, 40, 80, 160, 320 depending on number of upgrade levels.
POLYCULTURE_MULTIPLIER    = 160   # *** calibrated: 81920 / 512 = 160

DEFAULT_TIMEOUT_SECONDS = 3600.0


# ============================================================
# GAME ENUMERATIONS (shared with pumpkins/sunflowers sims)
# ============================================================

class _Entities:
    Grass        = "Entities.Grass"
    Bush         = "Entities.Bush"
    Tree         = "Entities.Tree"
    Carrot       = "Entities.Carrot"
    Pumpkin      = "Entities.Pumpkin"
    Dead_Pumpkin = "Entities.Dead_Pumpkin"
    Sunflower    = "Entities.Sunflower"
    Cactus       = "Entities.Cactus"
    Hedge        = "Entities.Hedge"
    Treasure     = "Entities.Treasure"
    Apple        = "Entities.Apple"

    def __iter__(self):
        return iter([
            self.Grass, self.Bush, self.Tree, self.Carrot, self.Pumpkin,
            self.Dead_Pumpkin, self.Sunflower, self.Cactus, self.Hedge,
            self.Treasure, self.Apple,
        ])

    def __repr__(self):
        return "Entities"


class _Items:
    Hay             = "Items.Hay"
    Wood            = "Items.Wood"
    Carrot          = "Items.Carrot"
    Pumpkin         = "Items.Pumpkin"
    Power           = "Items.Power"
    Cactus          = "Items.Cactus"
    Gold            = "Items.Gold"
    Bone            = "Items.Bone"
    Water           = "Items.Water"
    Fertilizer      = "Items.Fertilizer"
    Weird_Substance = "Items.Weird_Substance"

    def __iter__(self):
        return iter([
            self.Hay, self.Wood, self.Carrot, self.Pumpkin, self.Power,
            self.Cactus, self.Gold, self.Bone, self.Water,
            self.Fertilizer, self.Weird_Substance,
        ])

    def __repr__(self):
        return "Items"


class _Grounds:
    Grassland = "Grounds.Grassland"
    Soil      = "Grounds.Soil"

    def __iter__(self):
        return iter([self.Grassland, self.Soil])

    def __repr__(self):
        return "Grounds"


class _Hats:
    Straw_Hat    = "Hats.Straw_Hat"
    Dinosaur_Hat = "Hats.Dinosaur_Hat"
    Gray_Hat     = "Hats.Gray_Hat"
    Purple_Hat   = "Hats.Purple_Hat"
    Green_Hat    = "Hats.Green_Hat"
    Brown_Hat    = "Hats.Brown_Hat"

    def __iter__(self):
        return iter([
            self.Straw_Hat, self.Dinosaur_Hat, self.Gray_Hat,
            self.Purple_Hat, self.Green_Hat, self.Brown_Hat,
        ])

    def __repr__(self):
        return "Hats"


class _Leaderboards:
    Fastest_Reset     = "Leaderboards.Fastest_Reset"
    Maze              = "Leaderboards.Maze"
    Maze_Single       = "Leaderboards.Maze_Single"
    Dinosaur          = "Leaderboards.Dinosaur"
    Cactus            = "Leaderboards.Cactus"
    Cactus_Single     = "Leaderboards.Cactus_Single"
    Sunflowers        = "Leaderboards.Sunflowers"
    Sunflowers_Single = "Leaderboards.Sunflowers_Single"
    Pumpkins          = "Leaderboards.Pumpkins"
    Pumpkins_Single   = "Leaderboards.Pumpkins_Single"
    Wood              = "Leaderboards.Wood"
    Wood_Single       = "Leaderboards.Wood_Single"
    Carrots           = "Leaderboards.Carrots"
    Carrots_Single    = "Leaderboards.Carrots_Single"
    Hay               = "Leaderboards.Hay"
    Hay_Single        = "Leaderboards.Hay_Single"

    def __iter__(self):
        return iter([
            self.Fastest_Reset, self.Maze, self.Maze_Single, self.Dinosaur,
            self.Cactus, self.Cactus_Single, self.Sunflowers,
            self.Sunflowers_Single, self.Pumpkins, self.Pumpkins_Single,
            self.Wood, self.Wood_Single, self.Carrots, self.Carrots_Single,
            self.Hay, self.Hay_Single,
        ])

    def __repr__(self):
        return "Leaderboards"


class _Unlocks:
    Loops       = "Unlocks.Loops"
    Expand      = "Unlocks.Expand"
    Speed       = "Unlocks.Speed"
    Plant       = "Unlocks.Plant"
    Senses      = "Unlocks.Senses"
    Operators   = "Unlocks.Operators"
    Variables   = "Unlocks.Variables"
    Functions   = "Unlocks.Functions"
    Carrots     = "Unlocks.Carrots"
    Trees       = "Unlocks.Trees"
    Pumpkins    = "Unlocks.Pumpkins"
    Sunflowers  = "Unlocks.Sunflowers"
    Cactus      = "Unlocks.Cactus"
    Watering    = "Unlocks.Watering"
    Fertilizer  = "Unlocks.Fertilizer"
    Mazes       = "Unlocks.Mazes"
    Polyculture = "Unlocks.Polyculture"
    Costs       = "Unlocks.Costs"
    Megafarm    = "Unlocks.Megafarm"
    Hats        = "Unlocks.Hats"
    Dinosaurs   = "Unlocks.Dinosaurs"
    Simulation  = "Unlocks.Simulation"
    Timing      = "Unlocks.Timing"
    Import      = "Unlocks.Import"
    Debug       = "Unlocks.Debug"
    Debug_2     = "Unlocks.Debug_2"
    Auto_Unlock = "Unlocks.Auto_Unlock"
    Leaderboard = "Unlocks.Leaderboard"
    Grass       = "Unlocks.Grass"
    Utilities   = "Unlocks.Utilities"
    Dicts       = "Unlocks.Dicts"
    Lists       = "Unlocks.Lists"
    For         = "Unlocks.For"

    def __iter__(self):
        return iter([v for v in self.__class__.__dict__.values() if isinstance(v, str)])

    def __repr__(self):
        return "Unlocks"


Entities     = _Entities()
Items        = _Items()
Grounds      = _Grounds()
Hats         = _Hats()
Leaderboards = _Leaderboards()
Unlocks      = _Unlocks()

North = "North"
East  = "East"
South = "South"
West  = "West"

_DIRECTION_DELTA: Dict[str, tuple] = {
    North: (0,  1),
    East:  (1,  0),
    South: (0, -1),
    West:  (-1, 0),
}


# ============================================================
# TILE DATA
# ============================================================

@dataclass
class Tile:
    # For hay: entity is Entities.Grass when the grass has been "planted" (auto).
    # grow_progress tracks growth toward grow_time.
    # On a grassland tile, entity is always Entities.Grass (regrowing or grown).
    # On a soil tile, entity is None unless something was explicitly planted.
    entity:           Optional[str]   = None
    ground:           str             = Grounds.Grassland
    water:            float           = 0.0
    grow_progress:    float           = 0.0
    grow_time:        float           = 0.0
    # Fertilizer / Weird Substance infection
    infected:         bool            = False
    # Polyculture companion preference (assigned per grass tile at grow time)
    companion_type:   Optional[str]   = None  # Entities.Bush / Tree / Carrot (not Grass)
    companion_x:      Optional[int]   = None  # desired companion x-position on farm
    companion_y:      Optional[int]   = None  # desired companion y-position on farm

    def is_grown(self) -> bool:
        return (
            self.entity is not None
            and self.grow_time > 0
            and self.grow_progress >= self.grow_time
        )


# ============================================================
# GAME STATE
# ============================================================

class SimulationTimeout(Exception):
    pass


class GameState:
    def __init__(self, seed: Optional[int], timeout_seconds: float):
        self.rng = random.Random(seed)
        self.timeout_seconds = timeout_seconds

        # Active world size (can be changed by set_world_size; grid is always 8x8 max)
        self.world_size: int = WORLD_SIZE

        # Drone position (x=col, y=row; (0,0) = SW corner)
        self.drone_x: int = 0
        self.drone_y: int = 0

        # Inventory
        self.inventory: Dict[str, float] = {
            Items.Power:          float(STARTING_POWER),
            Items.Hay:            float(STARTING_HAY),
            Items.Water:          0.0,
            Items.Fertilizer:     0.0,
            Items.Weird_Substance: 0.0,
        }

        # Farm grid: grid[x][y]
        # All tiles start as Grassland with grass growing from t=0.
        # Grass is given a random initial grow_progress so they don't all
        # mature at exactly the same time at the start.
        self.grid: List[List[Tile]] = []
        for x in range(WORLD_SIZE):
            col = []
            for y in range(WORLD_SIZE):
                gt = GRASS_GROW_TIME
                # Random initial progress: some tiles start already grown
                progress = self.rng.uniform(0.0, gt * 1.5)
                progress = min(progress, gt)
                comp_type, comp_x, comp_y = self._roll_companion(x, y)
                t = Tile(
                    entity=Entities.Grass,
                    ground=Grounds.Grassland,
                    grow_time=gt,
                    grow_progress=progress,
                    companion_type=comp_type,
                    companion_x=comp_x,
                    companion_y=comp_y,
                )
                col.append(t)
            self.grid.append(col)

        # Time tracking
        self.sim_time:    float = 0.0
        self.tick_count:  int   = 0
        self.action_count: int  = 0

        # Stats
        self.stat_hay_harvested:       int = 0
        self.stat_total_actions:       int = 0
        self.stat_harvests:            int = 0
        self.stat_polyculture_bonuses: int = 0

    def _roll_companion(self, x: int, y: int) -> Tuple[str, int, int]:
        """
        Roll a random companion preference for a grass tile at (x, y).
        Companion type: Entities.Bush, Tree, or Carrot (not Grass -- always different type).
        Companion position: any tile within Manhattan distance 3 of (x, y), not (x, y) itself.
        Both match the polyculture.md specification.
        """
        companion_types = [Entities.Bush, Entities.Tree, Entities.Carrot]
        comp_type = self.rng.choice(companion_types)

        # Collect all positions within Manhattan distance 3 (excluding self)
        candidates = []
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if abs(dx) + abs(dy) <= 3 and (dx != 0 or dy != 0):
                    nx = (x + dx) % self.world_size
                    ny = (y + dy) % self.world_size
                    candidates.append((nx, ny))

        comp_x, comp_y = self.rng.choice(candidates)
        return comp_type, comp_x, comp_y

    def _tps(self) -> float:
        return (
            TICKS_PER_SECOND_POWERED
            if self.inventory.get(Items.Power, 0) > 0
            else TICKS_PER_SECOND_UNPOWERED
        )

    def _current_tile(self) -> Tile:
        return self.grid[self.drone_x][self.drone_y]

    def advance_ticks(self, n: int, is_action: bool = False) -> None:
        if n <= 0:
            return

        tps = self._tps()
        dt  = n / tps

        self.tick_count += n
        self.sim_time   += dt

        if self.sim_time > self.timeout_seconds:
            raise SimulationTimeout(
                f"Script exceeded {self.timeout_seconds:.0f}s timeout "
                f"(tick {self.tick_count})"
            )

        water_per_sec = WATER_TANKS_PER_10S / 10.0
        fert_per_sec  = FERTILIZER_PER_10S  / 10.0
        self.inventory[Items.Water]      = \
            self.inventory.get(Items.Water, 0.0) + water_per_sec * dt
        self.inventory[Items.Fertilizer] = \
            self.inventory.get(Items.Fertilizer, 0.0) + fert_per_sec * dt

        for col in self.grid:
            for tile in col:
                # Water decay
                if tile.water > 0.0:
                    tile.water *= math.exp(-WATER_DECAY_RATE * dt)
                    if tile.water < 1e-9:
                        tile.water = 0.0

                # Grass growth (only on grassland tiles with a grass entity)
                if (
                    tile.ground == Grounds.Grassland
                    and tile.entity == Entities.Grass
                    and tile.grow_progress < tile.grow_time
                ):
                    growth_rate = (
                        WATER_GROWTH_MIN
                        + (WATER_GROWTH_MAX - WATER_GROWTH_MIN) * tile.water
                    )
                    tile.grow_progress = min(
                        tile.grow_time,
                        tile.grow_progress + dt * growth_rate,
                    )

        # Power consumption
        if is_action:
            self.action_count       += 1
            self.stat_total_actions += 1
            if self.action_count >= POWER_CONSUMPTION_ACTIONS:
                self.action_count -= POWER_CONSUMPTION_ACTIONS
                cur = self.inventory.get(Items.Power, 0.0)
                if cur > 0:
                    self.inventory[Items.Power] = cur - 1.0


# ============================================================
# SIMULATION NAMESPACE (functions available to scripts)
# ============================================================

def build_namespace(state: GameState) -> Dict[str, Any]:

    def move(direction):
        dx, dy = _DIRECTION_DELTA.get(direction, (0, 0))
        new_x = (state.drone_x + dx) % state.world_size
        new_y = (state.drone_y + dy) % state.world_size
        if new_x == state.drone_x and new_y == state.drone_y:
            state.advance_ticks(1)
            return False
        state.drone_x = new_x
        state.drone_y = new_y
        state.advance_ticks(200, is_action=True)
        return True

    def can_harvest():
        state.advance_ticks(1)
        t = state._current_tile()
        return t.entity is not None and t.is_grown()

    def harvest():
        t = state._current_tile()
        if t.entity is None:
            # Truly empty tile (e.g. bare soil) -- no-op
            state.advance_ticks(200, is_action=True)
            return False

        # Harvest always costs 200 ticks, even on regrowing grass
        # (calibrated: real game returns True and costs 200 ticks regardless)
        state.advance_ticks(200, is_action=True)

        if t.entity == Entities.Grass and t.ground == Grounds.Grassland:
            # Only yield hay if grass is fully grown
            if t.is_grown():
                # Base yield
                base = GRASS_YIELD_BASE * GRASS_YIELD_MULTIPLIER

                # Polyculture bonus: multiply yield if the correct companion is present
                poly_bonus = False
                if t.companion_type is not None and t.companion_x is not None:
                    comp_tile = state.grid[t.companion_x][t.companion_y]
                    if comp_tile.entity == t.companion_type:
                        base = base * POLYCULTURE_MULTIPLIER
                        poly_bonus = True

                # Infection split: infected tiles send half yield to Weird Substance
                if t.infected:
                    ws_yield  = base // 2
                    hay_yield = base - ws_yield
                    state.inventory[Items.Weird_Substance] = \
                        state.inventory.get(Items.Weird_Substance, 0.0) + ws_yield
                else:
                    hay_yield = base

                state.inventory[Items.Hay] = \
                    state.inventory.get(Items.Hay, 0.0) + hay_yield
                state.stat_hay_harvested += hay_yield
                state.stat_harvests      += 1
                if poly_bonus:
                    state.stat_polyculture_bonuses += 1

            # Reset growth and re-roll companion on EVERY harvest
            # (calibrated: companion re-rolls even on regrowing grass)
            t.grow_progress = 0.0
            t.grow_time     = GRASS_GROW_TIME
            t.infected      = False
            t.companion_type, t.companion_x, t.companion_y = \
                state._roll_companion(state.drone_x, state.drone_y)
            # entity stays as Entities.Grass (it will regrow)
        else:
            # Non-grass entity (shouldn't happen in hay leaderboard, but handle gracefully)
            t.entity = None

        return True

    def till():
        # till() toggles Grassland <-> Soil
        # On grassland: converts to soil, grass entity is removed (can't regrow)
        # On soil: converts back to grassland, grass will start growing again
        state.advance_ticks(200, is_action=True)
        t = state._current_tile()
        if t.ground == Grounds.Grassland:
            t.ground = Grounds.Soil
            t.entity = None         # grass is destroyed
            t.grow_progress = 0.0
            t.grow_time = 0.0
        else:
            t.ground = Grounds.Grassland
            # Start growing grass again
            t.entity = Entities.Grass
            t.grow_progress = 0.0
            t.grow_time = GRASS_GROW_TIME

    def plant(entity):
        t = state._current_tile()

        # *** calibrated: Carrot (and other soil plants) require inventory items.
        # On Hay_Single leaderboard, you only get power — no wood/hay for planting.
        # Bush and Tree are free to plant on grassland; Carrot/Pumpkin/etc fail.
        planting_costs = {
            Entities.Carrot:  {Items.Hay: 1, Items.Wood: 1},
            Entities.Pumpkin: {Items.Carrot: 1},
        }
        if entity in planting_costs:
            cost = planting_costs[entity]
            for item, amount in cost.items():
                if state.inventory.get(item, 0) < amount:
                    state.advance_ticks(1)
                    return False
            # Deduct items
            for item, amount in cost.items():
                state.inventory[item] -= amount

        # Bush and Tree grow on Grassland OR Soil; everything else needs Soil
        grassland_ok = entity in (Entities.Bush, Entities.Tree)
        if t.ground == Grounds.Grassland and not grassland_ok:
            state.advance_ticks(1)
            return False
        if t.ground == Grounds.Soil and t.entity is not None:
            state.advance_ticks(1)
            return False
        if t.ground == Grounds.Grassland and t.entity is not None:
            # Grass occupies the tile; planting replaces it (like in the real game)
            if t.entity != Entities.Grass:
                # Another non-grass entity is already here
                state.advance_ticks(1)
                return False
        # Plant a non-grass entity; Grass doesn't need to be planted
        state.advance_ticks(200, is_action=True)
        t.entity = entity
        t.grow_progress = 0.0
        # Assign grow times for known entities
        if entity == Entities.Pumpkin:
            t.grow_time = state.rng.uniform(0.2, 3.8)
        elif entity == Entities.Carrot:
            t.grow_time = state.rng.uniform(0.5, 1.5)
        else:
            t.grow_time = state.rng.uniform(1.0, 3.0)
        return True

    def get_entity_type():
        state.advance_ticks(1)
        t = state._current_tile()
        # *** calibrated: regrowing grass returns Entities.Grass, not None
        return t.entity

    def get_ground_type():
        state.advance_ticks(1)
        return state._current_tile().ground

    def get_pos_x():
        state.advance_ticks(1)
        return state.drone_x

    def get_pos_y():
        state.advance_ticks(1)
        return state.drone_y

    def get_world_size():
        state.advance_ticks(1)
        return state.world_size

    def num_items(item):
        state.advance_ticks(1)
        return int(state.inventory.get(item, 0))

    def get_water():
        state.advance_ticks(1)
        return state._current_tile().water

    def use_item(item, n=1):
        t = state._current_tile()

        if item == Items.Water:
            if state.inventory.get(Items.Water, 0) >= n:
                state.inventory[Items.Water] -= n
                t.water = min(1.0, t.water + n * 0.25)
                state.advance_ticks(200, is_action=True)
                return True

        elif item == Items.Fertilizer:
            available = int(state.inventory.get(Items.Fertilizer, 0))
            use_count = min(n, available)
            if use_count <= 0:
                state.advance_ticks(1)
                return False
            state.inventory[Items.Fertilizer] -= use_count
            # Advance grow progress and mark tile as infected (fertilizer side effect)
            if t.entity is not None and t.grow_progress < t.grow_time:
                reduction = use_count * FERTILIZER_GROW_REDUCTION
                t.grow_progress = min(t.grow_time, t.grow_progress + reduction)
                t.infected = True
            state.advance_ticks(200, is_action=True)
            return True

        elif item == Items.Weird_Substance:
            # Toggles infected status of current tile and all 4 cardinal neighbors.
            # No wrapping at farm edges (same as pumpkins sim behavior).
            available = int(state.inventory.get(Items.Weird_Substance, 0.0))
            use_count = min(n, available)
            if use_count <= 0:
                state.advance_ticks(1)
                return False
            state.inventory[Items.Weird_Substance] -= use_count
            # Toggle current tile
            if t.entity is not None:
                t.infected = not t.infected
            # Toggle 4 cardinal neighbors (no edge wrapping)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx = state.drone_x + dx
                ny = state.drone_y + dy
                if 0 <= nx < state.world_size and 0 <= ny < state.world_size:
                    adj = state.grid[nx][ny]
                    if adj.entity is not None:
                        adj.infected = not adj.infected
            state.advance_ticks(200, is_action=True)
            return True

        state.advance_ticks(1)
        return False

    def measure(direction=None):
        state.advance_ticks(1)
        if direction is not None:
            dx, dy = _DIRECTION_DELTA.get(direction, (0, 0))
            x = (state.drone_x + dx) % state.world_size
            y = (state.drone_y + dy) % state.world_size
            t = state.grid[x][y]
        else:
            t = state._current_tile()
        # *** calibrated: measure() returns None for grass (and all non-special entities)
        # Docs list only Sunflower, Maze, Cactus, Dinosaur as returning non-None values.
        return None

    def get_companion():
        # Returns companion preference for the plant under the drone.
        # Format: (companion_type, (companion_x, companion_y))
        # For grass: companion is Bush, Tree, or Carrot (never Grass itself).
        # Returns None if tile has no plant or no companion preference.
        state.advance_ticks(1)
        t = state._current_tile()
        if t.entity is None or t.companion_type is None:
            return None
        return (t.companion_type, (t.companion_x, t.companion_y))

    def get_time():
        return state.sim_time  # 0 ticks

    def get_tick_count():
        return state.tick_count  # 0 ticks

    def num_unlocked(thing):
        state.advance_ticks(1)
        return 1  # all unlocks active on leaderboard

    def get_cost(thing, level=None):
        state.advance_ticks(1)
        return {}

    def unlock(unlock_item):
        state.advance_ticks(1)
        return False  # already at max on leaderboard

    def clear():
        state.advance_ticks(200)
        state.drone_x = 0
        state.drone_y = 0
        # Reset farm to all grassland with fresh grass
        for x in range(state.world_size):
            for y in range(state.world_size):
                t = state.grid[x][y]
                t.entity = Entities.Grass
                t.ground = Grounds.Grassland
                t.grow_progress = 0.0
                t.grow_time = GRASS_GROW_TIME
                t.water = 0.0
                t.infected = False
                t.companion_type, t.companion_x, t.companion_y = \
                    state._roll_companion(x, y)

    def can_move(direction):
        state.advance_ticks(1)
        return True  # Farm wraps -- always can move

    def set_execution_speed(speed):
        state.advance_ticks(200, is_action=False)

    def set_world_size(size):
        # Docs: size < 3 resets to full size; min active size is 3.
        # Also clears the farm and resets drone position.
        int_size = int(size)
        if int_size < 3:
            state.world_size = WORLD_SIZE
        else:
            state.world_size = min(int_size, WORLD_SIZE)
        # Clear farm: reset all tiles in new active area to fresh grassland
        state.drone_x = 0
        state.drone_y = 0
        for x in range(state.world_size):
            for y in range(state.world_size):
                t = state.grid[x][y]
                t.entity = Entities.Grass
                t.ground = Grounds.Grassland
                t.grow_progress = 0.0
                t.grow_time = GRASS_GROW_TIME
                t.water = 0.0
                t.infected = False
                t.companion_type, t.companion_x, t.companion_y = \
                    state._roll_companion(x, y)
        state.advance_ticks(200, is_action=False)

    def do_a_flip():
        state.advance_ticks(200)

    def pet_the_piggy():
        state.advance_ticks(200)

    def sim_print(*args):
        state.advance_ticks(200)

    def quick_print(*args):
        pass  # 0 ticks

    def leaderboard_run(leaderboard, filename, speedup=1):
        state.advance_ticks(200)

    def simulate(filename, sim_unlocks, sim_items, sim_globals, seed, speedup):
        state.advance_ticks(200)
        return 0.0

    def spawn_drone(function):
        state.advance_ticks(200, is_action=True)
        return None  # single drone only in Hay_Single

    def wait_for(drone):
        state.advance_ticks(1)
        return None

    def has_finished(drone):
        state.advance_ticks(1)
        return True

    def max_drones():
        state.advance_ticks(1)
        return 1

    def num_drones():
        state.advance_ticks(1)
        return 1

    def change_hat(hat):
        state.advance_ticks(200)

    def reset():
        state.advance_ticks(200)

    # Standard tick-counting function overrides
    def _range(*args):
        state.advance_ticks(1)
        return range(*args)

    def _len(collection):
        state.advance_ticks(1)
        return len(collection)

    def _abs(x):
        state.advance_ticks(1)
        return abs(x)

    def _max(*args):
        if len(args) == 1:
            seq = list(args[0])
            state.advance_ticks(max(0, len(seq) - 1))
            return max(seq)
        state.advance_ticks(max(0, len(args) - 1))
        return max(args)

    def _min(*args):
        if len(args) == 1:
            seq = list(args[0])
            state.advance_ticks(max(0, len(seq) - 1))
            return min(seq)
        state.advance_ticks(max(0, len(args) - 1))
        return min(args)

    def _str(obj):
        state.advance_ticks(1)
        return str(obj)

    def _random():
        state.advance_ticks(1)
        return state.rng.random()

    return {
        "North": North, "East": East, "South": South, "West": West,
        "Entities": Entities, "Items": Items, "Grounds": Grounds,
        "Unlocks": Unlocks, "Hats": Hats, "Leaderboards": Leaderboards,
        # Core drone actions
        "move": move, "till": till, "plant": plant,
        "harvest": harvest, "can_harvest": can_harvest,
        "can_move": can_move,
        # Sensing
        "get_entity_type": get_entity_type,
        "get_ground_type": get_ground_type,
        "get_pos_x": get_pos_x, "get_pos_y": get_pos_y,
        "get_world_size": get_world_size,
        "get_water": get_water, "use_item": use_item,
        "measure": measure, "get_companion": get_companion,
        # Inventory
        "num_items": num_items, "get_cost": get_cost,
        "num_unlocked": num_unlocked, "unlock": unlock,
        # Misc
        "change_hat": change_hat, "clear": clear,
        "set_execution_speed": set_execution_speed,
        "set_world_size": set_world_size,
        "do_a_flip": do_a_flip, "pet_the_piggy": pet_the_piggy,
        "leaderboard_run": leaderboard_run, "simulate": simulate,
        "spawn_drone": spawn_drone, "wait_for": wait_for,
        "has_finished": has_finished, "max_drones": max_drones,
        "num_drones": num_drones,
        "print": sim_print, "quick_print": quick_print,
        "get_time": get_time, "get_tick_count": get_tick_count,
        "reset": reset,
        # Standard functions (tick-counting overrides)
        "range": _range, "len": _len, "abs": _abs,
        "max": _max, "min": _min, "str": _str,
        "random": _random,
        "list": list, "dict": dict, "set": set, "tuple": tuple,
        "isinstance": isinstance, "type": type,
        "True": True, "False": False, "None": None,
        "__name__": "__main__",
        "__builtins__": __builtins__,
    }


# ============================================================
# LINE-LEVEL TICK COSTS (Python operators and control flow)
# Mirrors pumpkins_simulator.py cost model.
# ============================================================

def _line_tick_costs(script_code: str) -> Dict[int, int]:
    try:
        tree = ast.parse(script_code, filename="<script>", mode="exec")
    except SyntaxError:
        return {}

    costs: Dict[int, int] = {}

    def add(node: ast.AST, n: int = 1) -> None:
        lineno = getattr(node, "lineno", None)
        if lineno is None or n <= 0:
            return
        costs[lineno] = costs.get(lineno, 0) + n

    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            add(node, 1)
        elif isinstance(node, ast.BoolOp):
            add(node, max(0, len(node.values) - 1))
        elif isinstance(node, ast.Compare):
            add(node, max(1, len(node.ops)))
        elif isinstance(node, ast.If):
            add(node, 1)
        elif isinstance(node, ast.FunctionDef):
            add(node, 1)
        elif isinstance(node, ast.Pass):
            add(node, 1)
        elif isinstance(node, ast.Subscript):
            add(node, 1)

    return costs


def _make_line_tracer(state: GameState, line_costs: Dict[int, int]):
    def _trace(frame, event, arg):
        if event == "line" and frame.f_code.co_filename == "<script>":
            ticks = line_costs.get(frame.f_lineno, 0)
            if ticks > 0:
                state.advance_ticks(ticks)
        return _trace
    return _trace


# ============================================================
# SIMULATION RUNNER
# ============================================================

def run_simulation(
    script_code: str,
    seed: Optional[int],
    timeout_seconds: float,
) -> Dict[str, Any]:
    state = GameState(seed=seed, timeout_seconds=timeout_seconds)
    namespace = build_namespace(state)
    line_costs = _line_tick_costs(script_code)
    tracer = _make_line_tracer(state, line_costs)

    timed_out = False
    error: Optional[str] = None

    try:
        sys.settrace(tracer)
        exec(compile(script_code, "<script>", "exec"), namespace)
    except SimulationTimeout as e:
        timed_out = True
        error = str(e)
    except SystemExit:
        pass
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    finally:
        sys.settrace(None)

    hay = int(state.inventory.get(Items.Hay, 0))
    ws  = int(state.inventory.get(Items.Weird_Substance, 0))
    won = hay >= WIN_CONDITION_HAY

    return {
        "won":                    won,
        "timed_out":              timed_out,
        "error":                  error,
        "time_seconds":           state.sim_time,
        "tick_count":             state.tick_count,
        "hay_collected":          hay,
        "weird_substance":        ws,
        "total_harvests":         state.stat_harvests,
        "total_actions":          state.stat_total_actions,
        "polyculture_bonuses":    state.stat_polyculture_bonuses,
        "ticks_per_sec_unpowered": TICKS_PER_SECOND_UNPOWERED,
        "ticks_per_sec_powered":   TICKS_PER_SECOND_POWERED,
    }


# ============================================================
# MULTI-RUN HARNESS
# ============================================================

def run_multiple(
    script_path: str,
    n_iterations: int,
    seed: Optional[int],
    timeout_seconds: float,
    quiet: bool,
) -> Dict[str, Any]:
    with open(script_path) as f:
        script_code = f.read()

    if seed is None:
        seed = random.randint(0, 10**9)

    runs = []
    won_count = 0
    script_name = script_path.split("/")[-1]

    if not quiet:
        print(f"Simulating '{script_name}' for {n_iterations} iteration(s) "
              f"(timeout={timeout_seconds:.0f}s, seed={seed})")

    for i in range(n_iterations):
        result = run_simulation(script_code, seed + i, timeout_seconds)
        result["iteration"] = i + 1
        result["seed"] = seed + i
        runs.append(result)

        if result["won"]:
            won_count += 1

        if not quiet:
            status = "WON   " if result["won"] else ("TIMEOUT" if result["timed_out"] else "FAILED ")
            print(
                f"  [{i+1:4d}/{n_iterations}] {status}  "
                f"time={result['time_seconds']:12.3f}s  "
                f"hay={result['hay_collected']:12d}"
            )

    times = [r["time_seconds"] for r in runs if r["won"]]
    all_times = [r["time_seconds"] for r in runs]

    summary = {
        "script": script_path,
        "n_iterations": n_iterations,
        "seed": seed,
        "timeout_seconds": timeout_seconds,
        "win_rate": won_count / n_iterations,
        "runs": runs,
    }

    if times:
        summary["mean_time_seconds"]   = statistics.mean(times)
        summary["stdev_time_seconds"]  = statistics.stdev(times) if len(times) > 1 else 0.0
        summary["min_time_seconds"]    = min(times)
        summary["max_time_seconds"]    = max(times)
        summary["median_time_seconds"] = statistics.median(times)

    if not quiet and times:
        print(
            f"\nResults written to output (if --output specified)"
        )
        print(
            f"Completed {won_count}/{n_iterations} runs ({100*won_count/n_iterations:.0f}%)  "
            f"mean={statistics.mean(all_times):.3f}s  "
            f"std={statistics.stdev(all_times) if len(all_times) > 1 else 0:.3f}s"
        )

    return summary


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Hay_Single leaderboard simulator for The Farmer Was Replaced"
    )
    parser.add_argument("--script",     required=True,  help="Path to script file")
    parser.add_argument("--iterations", type=int, default=1, help="Number of runs")
    parser.add_argument("--output",     default="output.json",  help="Output JSON path")
    parser.add_argument("--timeout",    type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--seed",       type=int, default=None)
    parser.add_argument("--quiet",      action="store_true")
    args = parser.parse_args()

    results = run_multiple(
        script_path=args.script,
        n_iterations=args.iterations,
        seed=args.seed,
        timeout_seconds=args.timeout,
        quiet=args.quiet,
    )

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    if not args.quiet:
        print(f"Results written to '{args.output}'")


if __name__ == "__main__":
    main()
