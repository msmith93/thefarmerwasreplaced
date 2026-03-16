#!/usr/bin/env python3
"""
sunflowers_simulator.py — Sunflowers_Single Leaderboard Simulator
for "The Farmer Was Replaced"

Simulates the Sunflowers_Single leaderboard conditions:
  - 8×8 farm, single drone, all unlocks at max level
  - Starting inventory: 0 power, 1 billion carrots
  - Win condition: num_items(Items.Power) >= 10000 (script must terminate itself)

Usage:
    python sunflowers_simulator.py --script myscript.py --iterations 100 --output details.json

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
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ============================================================
# CONFIGURATION (from documentation — all values confirmed)
# ============================================================

WORLD_SIZE = 8
WIN_CONDITION_POWER = 10_000

# Sunflower mechanics (from documentation/Sunflowers/sunflower.txt)
SUNFLOWER_GROW_TIME_MIN = 5.6     # seconds at water=0, no fertilizer
SUNFLOWER_GROW_TIME_MAX = 8.4     # seconds at water=0, no fertilizer
SUNFLOWER_PETAL_MIN = 7
SUNFLOWER_PETAL_MAX = 15
SUNFLOWER_POWER_BASE = 1          # confirmed: 1 power per harvest (no bonus)
SUNFLOWER_POWER_BONUS = 8         # confirmed: 8 power per harvest (8× bonus)
SUNFLOWER_PLANT_COST_CARROT = 1   # confirmed: 1 carrot per plant

# Leaderboard starting inventory (Sunflowers_Single)
STARTING_POWER = 0                # confirmed: starts with 0 power
STARTING_CARROTS = 1_000_000_000  # leaderboard provides large carrot supply

# Tick / speed system (calibrated from in-game diagnostics)
# Empirically observed in user's game build:
#   - unpowered effective rate ≈ 3037 ticks/sec
#   - powered effective rate   ≈ 6030 ticks/sec
#
# Documentation states 3200 / 6400 at full upgrades; however, measured
# leaderboard behavior is consistently lower. We model the measured values
# so expected runtime predictions match the actual game.
TICKS_PER_SECOND_UNPOWERED = 3037.0
TICKS_PER_SECOND_POWERED   = 6030.0
POWER_CONSUMPTION_ACTIONS  = 30   # 1 power consumed every 30 drone actions

# Water system (all Watering upgrades at max)
#   1 tank/10s base, doubles 9 times = 512 tanks/10s
WATER_TANK_SIZE      = 0.25
WATER_TANKS_PER_10S  = 512
WATER_DECAY_RATE     = 0.01       # fraction of current level lost per second
WATER_GROWTH_MIN     = 1.0        # growth multiplier at water=0
WATER_GROWTH_MAX     = 5.0        # growth multiplier at water=1

# Fertilizer (all Fertilizer upgrades at max)
FERTILIZER_PER_10S        = 512
FERTILIZER_GROW_REDUCTION = 2.0   # seconds removed from remaining grow time per use

# Default per-run timeout (simulated seconds)
DEFAULT_TIMEOUT_SECONDS = 3600.0


# ============================================================
# GAME ENUMERATIONS
# (These are injected into the user script's namespace so that
#  Entities.Sunflower, Items.Power, Grounds.Soil, etc. all work.)
# ============================================================

class _Entities:
    Grass     = "Entities.Grass"
    Bush      = "Entities.Bush"
    Tree      = "Entities.Tree"
    Carrot    = "Entities.Carrot"
    Pumpkin   = "Entities.Pumpkin"
    Sunflower = "Entities.Sunflower"
    Cactus    = "Entities.Cactus"
    Hedge     = "Entities.Hedge"
    Treasure  = "Entities.Treasure"
    Apple     = "Entities.Apple"

    def __iter__(self):
        return iter([
            self.Grass, self.Bush, self.Tree, self.Carrot, self.Pumpkin,
            self.Sunflower, self.Cactus, self.Hedge, self.Treasure, self.Apple,
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
    Straw_Hat   = "Hats.Straw_Hat"
    Dinosaur_Hat = "Hats.Dinosaur_Hat"
    Gray_Hat    = "Hats.Gray_Hat"
    Purple_Hat  = "Hats.Purple_Hat"
    Green_Hat   = "Hats.Green_Hat"
    Brown_Hat   = "Hats.Brown_Hat"

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
            self.Cactus, self.Cactus_Single, self.Sunflowers, self.Sunflowers_Single,
            self.Pumpkins, self.Pumpkins_Single, self.Wood, self.Wood_Single,
            self.Carrots, self.Carrots_Single, self.Hay, self.Hay_Single,
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


# Singleton instances used in both the simulator internals and the user namespace
Entities    = _Entities()
Items       = _Items()
Grounds     = _Grounds()
Hats        = _Hats()
Leaderboards = _Leaderboards()
Unlocks     = _Unlocks()

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
    entity:       Optional[str] = None
    ground:       str           = "Grounds.Grassland"
    water:        float         = 0.0
    petals:       Optional[int] = None   # 7–15 for sunflowers; None otherwise
    grow_progress: float        = 0.0   # accumulated growth-seconds
    grow_time:    float         = 0.0   # base grow time in seconds (at water=0)
    infected:     bool          = False

    def is_grown(self) -> bool:
        return (
            self.entity is not None
            and self.grow_time > 0
            and self.grow_progress >= self.grow_time
        )


# ============================================================
# EXCEPTIONS
# ============================================================

class SimulationTimeout(Exception):
    pass


# ============================================================
# GAME STATE
# ============================================================

class GameState:
    """
    Holds all mutable game world state for one simulation run.

    Grid indexing: grid[x][y] where x=0 is west, y=0 is south.
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.rng = random.Random(seed)
        self.timeout_seconds = timeout_seconds

        # 8×8 grid
        self.grid: List[List[Tile]] = [
            [Tile(ground=Grounds.Grassland) for _ in range(WORLD_SIZE)]
            for _ in range(WORLD_SIZE)
        ]

        # Inventory: item-constant string → float quantity
        self.inventory: Dict[str, float] = {
            Items.Power:     float(STARTING_POWER),
            Items.Carrot:    float(STARTING_CARROTS),
            Items.Water:     0.0,
            Items.Fertilizer: 0.0,
        }

        # Drone position
        self.drone_x: int = 0
        self.drone_y: int = 0

        # Simulation time tracking
        self.tick_count: int  = 0
        self.sim_time:  float = 0.0

        # Power consumption counter (resets every POWER_CONSUMPTION_ACTIONS actions)
        self.action_count: int = 0

        # Harvest penalty: True means the next sunflower harvest won't get 8× bonus.
        # Set when a non-max-petal sunflower is harvested while ≥10 are on the farm.
        self.harvest_penalty: bool = False

        # Statistics for this run
        self.stat_total_actions: int  = 0
        self.stat_harvests:      int  = 0
        self.stat_bonus_harvests: int = 0
        self.stat_plants:        int  = 0
        self.stat_moves:         int  = 0

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    def current_tile(self) -> Tile:
        return self.grid[self.drone_x][self.drone_y]

    def _tps(self) -> float:
        """Effective ticks per second: calibrated powered/unpowered values."""
        return TICKS_PER_SECOND_POWERED if self.inventory.get(Items.Power, 0) > 0 \
               else TICKS_PER_SECOND_UNPOWERED

    # ----------------------------------------------------------
    # Core time engine
    # ----------------------------------------------------------

    def advance_ticks(self, n: int, is_action: bool = False) -> None:
        """
        Advance simulation by n ticks.

        Computes dt from current speed, then:
          1. Auto-accumulates water/fertilizer inventory
          2. Decays water levels on all tiles
          3. Advances growth progress on all growing tiles
          4. Optionally increments action counter and deducts power

        Raises SimulationTimeout if sim_time exceeds the per-run timeout.
        """
        if n <= 0:
            return

        tps = self._tps()
        dt = n / tps

        self.tick_count += n
        self.sim_time   += dt

        if self.sim_time > self.timeout_seconds:
            raise SimulationTimeout(
                f"Script exceeded {self.timeout_seconds:.0f}s simulated timeout "
                f"(tick {self.tick_count})"
            )

        # Auto-accumulate water and fertilizer
        water_per_sec = WATER_TANKS_PER_10S / 10.0        # tanks/sec
        fert_per_sec  = FERTILIZER_PER_10S  / 10.0        # units/sec
        self.inventory[Items.Water]     += water_per_sec * dt
        self.inventory[Items.Fertilizer] += fert_per_sec * dt

        # Update all tiles
        for col in self.grid:
            for tile in col:
                # Water decay: w(t+dt) = w(t) × e^(−rate×dt)
                if tile.water > 0.0:
                    tile.water *= math.exp(-WATER_DECAY_RATE * dt)
                    if tile.water < 1e-9:
                        tile.water = 0.0

                # Growth: rate scales linearly 1× (dry) to 5× (fully watered)
                if (
                    tile.entity is not None
                    and tile.grow_time > 0
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

        # Power consumption: 1 power every POWER_CONSUMPTION_ACTIONS drone actions
        if is_action:
            self.action_count    += 1
            self.stat_total_actions += 1
            if self.action_count >= POWER_CONSUMPTION_ACTIONS:
                self.action_count -= POWER_CONSUMPTION_ACTIONS
                cur = self.inventory.get(Items.Power, 0.0)
                if cur > 0:
                    self.inventory[Items.Power] = cur - 1.0

    # ----------------------------------------------------------
    # Farm queries (used internally by harvest logic)
    # ----------------------------------------------------------

    def count_sunflowers(self) -> int:
        return sum(
            1
            for col in self.grid
            for tile in col
            if tile.entity == Entities.Sunflower
        )

    def max_petals_on_farm(self, grown_only: bool = False) -> int:
        return max(
            (
                tile.petals
                for col in self.grid
                for tile in col
                if (
                    tile.entity == Entities.Sunflower
                    and tile.petals is not None
                    and (not grown_only or tile.is_grown())
                )
            ),
            default=0,
        )

    def _clear_tile_entity(self, tile: Tile) -> None:
        tile.entity       = None
        tile.grow_progress = 0.0
        tile.grow_time    = 0.0
        tile.petals       = None
        tile.infected     = False


# ============================================================
# MOCK GAME API — injected into the user script's namespace
# ============================================================

def build_namespace(state: GameState) -> Dict[str, Any]:
    """
    Returns a dict suitable for use as globals in exec().
    Every function closes over `state` and faithfully implements
    the tick costs and game mechanics documented for the leaderboard.
    """

    # ── Movement ──────────────────────────────────────────────

    def move(direction):
        dx, dy = _DIRECTION_DELTA.get(direction, (0, 0))
        state.drone_x = (state.drone_x + dx) % WORLD_SIZE
        state.drone_y = (state.drone_y + dy) % WORLD_SIZE
        state.stat_moves += 1
        state.advance_ticks(200, is_action=True)
        return True

    def can_move(direction):
        # No walls in the sunflower leaderboard
        state.advance_ticks(1)
        return True

    # ── Position ──────────────────────────────────────────────

    def get_pos_x():
        state.advance_ticks(1)
        return state.drone_x

    def get_pos_y():
        state.advance_ticks(1)
        return state.drone_y

    def get_world_size():
        state.advance_ticks(1)
        return WORLD_SIZE

    # ── Ground ────────────────────────────────────────────────

    def get_ground_type():
        state.advance_ticks(1)
        return state.current_tile().ground

    def till():
        t = state.current_tile()
        if t.ground == Grounds.Grassland:
            t.ground = Grounds.Soil
        else:
            # Soil → Grassland: any plant requiring soil is destroyed
            t.ground = Grounds.Grassland
            if t.entity in (
                Entities.Sunflower, Entities.Carrot,
                Entities.Pumpkin, Entities.Cactus,
            ):
                state._clear_tile_entity(t)
        state.advance_ticks(200, is_action=True)
        return None

    # ── Entity sensing ─────────────────────────────────────────

    def get_entity_type():
        state.advance_ticks(1)
        return state.current_tile().entity

    def can_harvest():
        state.advance_ticks(1)
        t = state.current_tile()
        if t.entity is None or t.grow_time <= 0:
            return False
        return t.grow_progress >= t.grow_time

    # ── Harvest ───────────────────────────────────────────────

    def harvest():
        t = state.current_tile()

        if t.entity is None:
            state.advance_ticks(1)
            return False

        entity = t.entity

        # Tick cost is paid before yield is calculated (action runs at current speed)
        state.advance_ticks(200, is_action=True)

        if entity == Entities.Sunflower:
            _do_sunflower_harvest(state, t)
        elif entity == Entities.Grass:
            state.inventory[Items.Hay] = state.inventory.get(Items.Hay, 0.0) + 1
        elif entity == Entities.Bush:
            state.inventory[Items.Wood] = state.inventory.get(Items.Wood, 0.0) + 1
        elif entity == Entities.Carrot:
            if t.is_grown():
                state.inventory[Items.Carrot] = state.inventory.get(Items.Carrot, 0.0) + 1
        # All other entities: destroyed with no yield (pumpkin, cactus, etc.)

        state._clear_tile_entity(t)
        state.stat_harvests += 1
        return True

    # ── Planting ──────────────────────────────────────────────

    def plant(entity):
        t = state.current_tile()

        # Cannot plant on occupied tile
        if t.entity is not None:
            state.advance_ticks(1)
            return False

        if entity == Entities.Sunflower:
            if t.ground != Grounds.Soil:
                state.advance_ticks(1)
                return False
            if state.inventory.get(Items.Carrot, 0) < SUNFLOWER_PLANT_COST_CARROT:
                state.advance_ticks(1)
                return False
            state.inventory[Items.Carrot] -= SUNFLOWER_PLANT_COST_CARROT
            t.entity        = Entities.Sunflower
            t.grow_time     = state.rng.uniform(SUNFLOWER_GROW_TIME_MIN, SUNFLOWER_GROW_TIME_MAX)
            t.grow_progress = 0.0
            t.petals        = state.rng.randint(SUNFLOWER_PETAL_MIN, SUNFLOWER_PETAL_MAX)
            t.infected      = False

        elif entity == Entities.Grass:
            if t.ground != Grounds.Grassland:
                state.advance_ticks(1)
                return False
            t.entity        = Entities.Grass
            t.grow_time     = state.rng.uniform(1.0, 3.0)
            t.grow_progress = 0.0

        elif entity == Entities.Bush:
            t.entity        = Entities.Bush
            t.grow_time     = state.rng.uniform(2.0, 6.0)
            t.grow_progress = 0.0

        elif entity == Entities.Carrot:
            if t.ground != Grounds.Soil:
                state.advance_ticks(1)
                return False
            t.entity        = Entities.Carrot
            t.grow_time     = state.rng.uniform(5.0, 10.0)
            t.grow_progress = 0.0

        else:
            # Unsupported entity in this simulator
            state.advance_ticks(1)
            return False

        state.stat_plants += 1
        state.advance_ticks(200, is_action=True)
        return True

    # ── Water ─────────────────────────────────────────────────

    def get_water():
        state.advance_ticks(1)
        return state.current_tile().water

    def use_item(item, n=1):
        n = int(n)
        if n <= 0:
            state.advance_ticks(1)
            return False

        if item == Items.Water:
            available = int(state.inventory.get(Items.Water, 0.0))
            use_count = min(n, available)
            if use_count <= 0:
                state.advance_ticks(1)
                return False
            state.inventory[Items.Water] -= use_count
            t = state.current_tile()
            t.water = min(1.0, t.water + use_count * WATER_TANK_SIZE)
            state.advance_ticks(200, is_action=True)
            return True

        if item == Items.Fertilizer:
            available = int(state.inventory.get(Items.Fertilizer, 0.0))
            use_count = min(n, available)
            if use_count <= 0:
                state.advance_ticks(1)
                return False
            t = state.current_tile()
            if t.entity is None:
                state.advance_ticks(1)
                return False
            state.inventory[Items.Fertilizer] -= use_count
            # Each fertilizer use removes 2s from remaining grow time
            reduction = use_count * FERTILIZER_GROW_REDUCTION
            t.grow_progress = min(t.grow_time, t.grow_progress + reduction)
            t.infected = True
            state.advance_ticks(200, is_action=True)
            return True

        # Other items not simulated
        state.advance_ticks(1)
        return False

    # ── Measure ───────────────────────────────────────────────

    def measure(direction=None):
        state.advance_ticks(1)
        if direction is not None:
            dx, dy = _DIRECTION_DELTA.get(direction, (0, 0))
            tx = (state.drone_x + dx) % WORLD_SIZE
            ty = (state.drone_y + dy) % WORLD_SIZE
            t = state.grid[tx][ty]
        else:
            t = state.current_tile()

        if t.entity == Entities.Sunflower:
            return t.petals
        # Pumpkin, cactus, maze etc. return None in this simulator
        return None

    # ── Swap ──────────────────────────────────────────────────

    def swap(direction):
        dx, dy = _DIRECTION_DELTA.get(direction, (0, 0))
        nx = state.drone_x + dx
        ny = state.drone_y + dy
        # swap() does not wrap — fails at farm boundaries
        if nx < 0 or nx >= WORLD_SIZE or ny < 0 or ny >= WORLD_SIZE:
            state.advance_ticks(1)
            return False
        t1 = state.current_tile()
        t2 = state.grid[nx][ny]
        (
            t1.entity, t2.entity,
            t1.petals, t2.petals,
            t1.grow_progress, t2.grow_progress,
            t1.grow_time, t2.grow_time,
            t1.infected, t2.infected,
        ) = (
            t2.entity, t1.entity,
            t2.petals, t1.petals,
            t2.grow_progress, t1.grow_progress,
            t2.grow_time, t1.grow_time,
            t2.infected, t1.infected,
        )
        state.advance_ticks(200, is_action=True)
        return True

    # ── Inventory ─────────────────────────────────────────────

    def num_items(item):
        state.advance_ticks(1)
        val = state.inventory.get(item, 0.0)
        return int(val)

    # ── Companion (polyculture — not applicable to sunflowers) ─

    def get_companion():
        state.advance_ticks(1)
        return None

    # ── Cost ──────────────────────────────────────────────────

    def get_cost(thing, level=None):
        state.advance_ticks(1)
        if thing == Entities.Sunflower:
            return {Items.Carrot: SUNFLOWER_PLANT_COST_CARROT}
        if thing == Entities.Carrot:
            return {Items.Wood: 1, Items.Hay: 1}
        return {}

    # ── Timing ────────────────────────────────────────────────

    def get_time():
        return state.sim_time   # free (0 ticks)

    def get_tick_count():
        return state.tick_count  # free (0 ticks)

    # ── Unlocks ───────────────────────────────────────────────

    def num_unlocked(thing):
        state.advance_ticks(1)
        return 1   # all unlocks at max in the leaderboard

    def unlock(thing):
        state.advance_ticks(200, is_action=False)
        return True

    # ── Misc farm ops ─────────────────────────────────────────

    def change_hat(hat):
        state.advance_ticks(200, is_action=True)

    def clear():
        for col in state.grid:
            for tile in col:
                tile.entity       = None
                tile.ground       = Grounds.Grassland
                tile.water        = 0.0
                tile.petals       = None
                tile.grow_progress = 0.0
                tile.grow_time    = 0.0
                tile.infected     = False
        state.drone_x = 0
        state.drone_y = 0
        state.advance_ticks(200, is_action=False)

    def set_execution_speed(speed):
        # Noted but not dynamically enforced in the simulator
        state.advance_ticks(200)

    def set_world_size(size):
        # Simulator always uses the leaderboard-fixed 8×8
        state.advance_ticks(200)

    # Stubs for functions that won't be used in leaderboard scripts
    def do_a_flip():
        # 1 real second — modelled as 1 simulated second
        state.sim_time += 1.0
        if state.sim_time > state.timeout_seconds:
            raise SimulationTimeout("Timeout during do_a_flip")

    def pet_the_piggy():
        state.sim_time += 1.0
        if state.sim_time > state.timeout_seconds:
            raise SimulationTimeout("Timeout during pet_the_piggy")

    def leaderboard_run(leaderboard, filename, speedup=1):
        # No-op: the script being simulated IS the leaderboard script
        state.advance_ticks(200)

    def simulate(*args, **kwargs):
        state.advance_ticks(200)
        return 0.0

    def spawn_drone(function):
        # Multi-drone not applicable to the Single leaderboard
        state.advance_ticks(1)
        return None

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

    # ── Debug output ──────────────────────────────────────────

    def quick_print(*args):
        # 0 ticks, 0 wall-clock time — silent in simulator
        pass

    def sim_print(*args):
        # 1 real second in the game; we advance 1 simulated second
        state.sim_time += 1.0
        if state.sim_time > state.timeout_seconds:
            raise SimulationTimeout("Timeout during print")

    # ── Standard library replacements with tick costs ─────────

    def _random():
        state.advance_ticks(1)
        return state.rng.random()

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

    # ── Namespace dict ────────────────────────────────────────

    return {
        # Directions
        "North": North, "East": East, "South": South, "West": West,
        # Enum namespaces
        "Entities": Entities, "Items": Items, "Grounds": Grounds,
        "Hats": Hats, "Leaderboards": Leaderboards, "Unlocks": Unlocks,
        # Movement
        "move": move, "can_move": can_move,
        # Position
        "get_pos_x": get_pos_x, "get_pos_y": get_pos_y,
        "get_world_size": get_world_size,
        # Ground
        "get_ground_type": get_ground_type, "till": till,
        # Entity
        "get_entity_type": get_entity_type,
        "can_harvest": can_harvest, "harvest": harvest,
        # Planting
        "plant": plant,
        # Water / fertilizer
        "get_water": get_water, "use_item": use_item,
        # Measure / swap
        "measure": measure, "swap": swap,
        # Inventory
        "num_items": num_items,
        # Companion
        "get_companion": get_companion,
        # Cost
        "get_cost": get_cost,
        # Timing
        "get_time": get_time, "get_tick_count": get_tick_count,
        # Unlocks
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
        # Debug
        "print": sim_print, "quick_print": quick_print,
        # Standard functions (tick-counting overrides)
        "range": range, "len": _len, "abs": _abs,
        "max": _max, "min": _min, "str": _str,
        "random": _random,
        "list": list, "dict": dict, "set": set, "tuple": tuple,
        "isinstance": isinstance, "type": type,
        "True": True, "False": False, "None": None,
        # Allow the __name__ == "__main__" guard pattern
        "__name__": "__main__",
        # Provide full builtins so int(), float(), bool(), etc. work
        "__builtins__": __builtins__,
    }


# ============================================================
# SUNFLOWER HARVEST LOGIC
# (separated to keep build_namespace readable)
# ============================================================

def _do_sunflower_harvest(state: GameState, tile: Tile) -> None:
    """
    Compute and add power yield for harvesting the sunflower on `tile`.

    8× bonus rules (from docs):
      - Requires ≥10 sunflowers currently on the farm
      - AND this tile has the maximum petal count among all sunflowers
      - AND no harvest_penalty is active
    Harvesting non-max when ≥10 sunflowers are present sets harvest_penalty,
    which causes the NEXT sunflower harvest to also yield only base power.
    """
    sf_count = state.count_sunflowers()                  # count before removal
    max_p    = state.max_petals_on_farm(grown_only=True) # compare against grown flowers

    if state.harvest_penalty:
        # Penalty active: base power, penalty consumed
        power_gained = SUNFLOWER_POWER_BASE
        state.harvest_penalty = False

    elif sf_count >= 10 and tile.petals is not None and tile.petals == max_p:
        # 8× bonus: ≥10 sunflowers, this is a max-petal sunflower
        power_gained = SUNFLOWER_POWER_BONUS
        state.stat_bonus_harvests += 1

    elif sf_count >= 10 and tile.petals is not None and tile.petals < max_p:
        # Harvested non-max while ≥10 on farm: base power + set penalty
        power_gained = SUNFLOWER_POWER_BASE
        state.harvest_penalty = True

    else:
        # Fewer than 10 sunflowers on farm: base power, no penalty effects
        power_gained = SUNFLOWER_POWER_BASE

    state.inventory[Items.Power] = state.inventory.get(Items.Power, 0.0) + power_gained


# ============================================================
# SCRIPT OPERATOR/CONTROL TICK MODEL
# ============================================================

def _line_tick_costs(script_code: str) -> Dict[int, int]:
    """
    Approximate non-API code ticks from game docs and map them per line.
    These ticks are charged via a Python trace hook while user code runs.
    """
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
        # Binary operators (+,-,*,/,//,%, and similar) cost 1 each
        if isinstance(node, ast.BinOp):
            add(node, 1)
        # Boolean ops (and/or): one op between each pair of values
        elif isinstance(node, ast.BoolOp):
            add(node, max(0, len(node.values) - 1))
        # Comparisons: one per comparator
        elif isinstance(node, ast.Compare):
            add(node, max(1, len(node.ops)))
        # if branch costs 1 (condition expression costs counted separately)
        elif isinstance(node, ast.If):
            add(node, 1)
        # Function definitions cost 1
        elif isinstance(node, ast.FunctionDef):
            add(node, 1)
        # pass costs 1
        elif isinstance(node, ast.Pass):
            add(node, 1)
        # Indexing costs 1
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
    """
    Execute `script_code` once in a fresh game world.
    Returns a dict with timing, power, and diagnostic stats.
    """
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

    power = int(state.inventory.get(Items.Power, 0.0))
    won   = power >= WIN_CONDITION_POWER and not timed_out and error is None

    return {
        "time_seconds":    round(state.sim_time, 6),
        "power_collected": power,
        "won":             won,
        "timed_out":       timed_out,
        "error":           error,
        "total_actions":   state.stat_total_actions,
        "total_harvests":  state.stat_harvests,
        "bonus_harvests":  state.stat_bonus_harvests,
        "total_plants":    state.stat_plants,
        "total_moves":     state.stat_moves,
        "tick_count":      state.tick_count,
    }


# ============================================================
# CLI ENTRY POINT
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sunflowers_Single leaderboard simulator for 'The Farmer Was Replaced'",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python sunflowers_simulator.py --script myscript.py "
            "--iterations 100 --output details.json"
        ),
    )
    parser.add_argument(
        "--script", required=True, metavar="PATH",
        help="Path to the farming script (.py) to simulate",
    )
    parser.add_argument(
        "--iterations", type=int, default=1, metavar="N",
        help="Number of simulation runs (default: 1)",
    )
    parser.add_argument(
        "--output", default="output.json", metavar="PATH",
        help="Output JSON file (default: output.json)",
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS, metavar="SECONDS",
        help=f"Per-run simulated time limit in seconds (default: {DEFAULT_TIMEOUT_SECONDS:.0f})",
    )
    parser.add_argument(
        "--seed", type=int, default=None, metavar="N",
        help="Base random seed; run i uses seed+i (default: random each run)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress per-iteration progress output",
    )
    args = parser.parse_args()

    # Load script
    try:
        with open(args.script, "r") as f:
            script_code = f.read()
    except FileNotFoundError:
        print(f"Error: script file '{args.script}' not found.", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(
            f"Simulating '{args.script}' for {args.iterations} iteration(s) "
            f"(timeout={args.timeout:.0f}s, seed={'auto' if args.seed is None else args.seed})",
            file=sys.stderr,
        )

    # Run iterations
    results: List[Dict[str, Any]] = []
    for i in range(args.iterations):
        seed = (args.seed + i) if args.seed is not None else None
        result = run_simulation(script_code, seed=seed, timeout_seconds=args.timeout)
        result["iteration"] = i + 1
        result["seed"]      = seed
        results.append(result)

        if not args.quiet:
            if result["timed_out"]:
                status = "TIMEOUT"
            elif result["error"]:
                status = f"ERROR({result['error'][:40]})"
            elif result["won"]:
                status = "WON"
            else:
                status = "FAILED"
            print(
                f"  [{i+1:>4}/{args.iterations}] {status:10s} "
                f"time={result['time_seconds']:>10.3f}s  "
                f"power={result['power_collected']:>6}  "
                f"bonus_harvests={result['bonus_harvests']}",
                file=sys.stderr,
            )

    # Aggregate statistics (over successful/completed runs only)
    won_results    = [r for r in results if r["won"]]
    timed_out_runs = [r for r in results if r["timed_out"]]
    error_runs     = [r for r in results if r["error"] and not r["timed_out"]]
    times          = [r["time_seconds"] for r in won_results]

    summary: Dict[str, Any] = {
        "iterations":          args.iterations,
        "won":                 len(won_results),
        "timed_out":           len(timed_out_runs),
        "errored":             len(error_runs),
        "mean_time_seconds":   round(statistics.mean(times),   6) if times else None,
        "std_time_seconds":    round(statistics.stdev(times),  6) if len(times) > 1 else None,
        "min_time_seconds":    round(min(times),               6) if times else None,
        "max_time_seconds":    round(max(times),               6) if times else None,
        "median_time_seconds": round(statistics.median(times), 6) if times else None,
    }

    config: Dict[str, Any] = {
        "script":                  args.script,
        "world_size":              WORLD_SIZE,
        "win_condition_power":     WIN_CONDITION_POWER,
        "grow_time_range_seconds": [SUNFLOWER_GROW_TIME_MIN, SUNFLOWER_GROW_TIME_MAX],
        "power_yield_base":        SUNFLOWER_POWER_BASE,
        "power_yield_bonus":       SUNFLOWER_POWER_BONUS,
        "starting_power":          STARTING_POWER,
        "starting_carrots":        STARTING_CARROTS,
        "ticks_per_sec_unpowered": TICKS_PER_SECOND_UNPOWERED,
        "ticks_per_sec_powered":   TICKS_PER_SECOND_POWERED,
        "power_consumption_per_actions": POWER_CONSUMPTION_ACTIONS,
        "water_tanks_per_10s":     WATER_TANKS_PER_10S,
        "fertilizer_per_10s":      FERTILIZER_PER_10S,
        "timeout_seconds":         args.timeout,
    }

    output = {
        "summary": summary,
        "config":  config,
        "runs":    results,
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    if not args.quiet:
        print(f"\nResults written to '{args.output}'", file=sys.stderr)
        if times:
            mean_s = summary["mean_time_seconds"]
            std_s  = summary["std_time_seconds"]
            pct    = len(won_results) / args.iterations * 100
            print(
                f"Completed {len(won_results)}/{args.iterations} runs ({pct:.0f}%)  "
                + (f"mean={mean_s:.3f}s  std={std_s:.3f}s" if std_s is not None
                   else f"time={mean_s:.3f}s"),
                file=sys.stderr,
            )
        if timed_out_runs:
            print(
                f"WARNING: {len(timed_out_runs)} run(s) timed out after "
                f"{args.timeout:.0f}s — script may not terminate correctly.",
                file=sys.stderr,
            )
        if error_runs:
            print(
                f"WARNING: {len(error_runs)} run(s) raised errors.",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
