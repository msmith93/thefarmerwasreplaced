#!/usr/bin/env python3
"""
pumpkins_simulator.py — Pumpkins_Single Leaderboard Simulator
for "The Farmer Was Replaced"

Simulates the Pumpkins_Single leaderboard conditions:
  - 8×8 farm, single drone, all unlocks at max level
  - Starting inventory: 1 billion power, 1 billion carrots
  - Win condition: num_items(Items.Pumpkin) >= 10_000_000 (script must terminate itself)

Pumpkin mechanics:
  - Planted on tilled soil, costs 1 carrot per plant
  - Average grow time: 2 seconds (range 1.6–2.4s)
  - 20% chance of dying when fully grown → becomes Entities.Dead_Pumpkin
  - Dead pumpkins: can_harvest() always returns False; auto-removed when something new is planted
  - Fully grown adjacent pumpkins merge into a mega pumpkin on harvest
  - Yield formula: count = tiles in connected component, n = floor(sqrt(count))
      n < 6  → yield = n³    (e.g. 3×3 = 27 pumpkins)
      n >= 6 → yield = n²×6  (e.g. 6×6 = 216 pumpkins, 8×8 = 384 pumpkins)

Usage:
    python pumpkins_simulator.py --script myscript.py --iterations 100 --output details.json

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
# CONFIGURATION (from documentation — values confirmed)
# ============================================================

WORLD_SIZE = 8
WIN_CONDITION_PUMPKINS = 10_000_000

# Pumpkin mechanics (from documentation/docs/unlocks/pumpkins.md + builtins.py)
PUMPKIN_GROW_TIME_MIN   = 0.2    # seconds (base range 0.2-3.8s, avg 2.0s)
PUMPKIN_GROW_TIME_MAX   = 3.8    # seconds (calibrated grow time, not scan overhead)
PUMPKIN_DEATH_CHANCE    = 0.20   # 20% chance of dying when fully grown
PUMPKIN_PLANT_COST_CARROT = 512  # calibrated: 32768 carrots / 64 tiles = 512 per plant

# Leaderboard starting inventory (Pumpkins_Single)
# Calibrated from real game: starts with 1 billion power (drone runs at
# powered speed throughout the entire run).
STARTING_POWER   = 1_000_000_000
STARTING_CARROTS = 1_000_000_000

# Tick / speed system (same calibrated values as sunflowers_simulator)
TICKS_PER_SECOND_UNPOWERED = 3037.0
TICKS_PER_SECOND_POWERED   = 6030.0
POWER_CONSUMPTION_ACTIONS  = 30   # 1 power consumed every 30 drone actions

# Water system (all Watering upgrades at max)
WATER_TANK_SIZE      = 0.25
WATER_TANKS_PER_10S  = 256  # calibrated from in-game diagnostic (~255.96)
WATER_DECAY_RATE     = 0.01
WATER_GROWTH_MIN     = 1.0
WATER_GROWTH_MAX     = 5.0

# Fertilizer income rate for Pumpkins_Single leaderboard context.
# Calibrated from in-game diagnostics: ~24 over 30s => ~8 per 10s.
FERTILIZER_PER_10S        = 8
FERTILIZER_GROW_REDUCTION = 2.0   # seconds removed per use

DEFAULT_TIMEOUT_SECONDS = 3600.0


# ============================================================
# GAME ENUMERATIONS
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
    entity:           Optional[str] = None
    ground:           str           = "Grounds.Grassland"
    water:            float         = 0.0
    petals:           Optional[int] = None   # sunflowers only
    grow_progress:    float         = 0.0
    grow_time:        float         = 0.0
    infected:         bool          = False
    pumpkin_will_die: bool          = False  # pre-rolled death outcome for pumpkins
    death_applied:    bool          = False  # True once death check has run
    pumpkin_id:       Optional[int] = None   # unique random ID assigned at plant time

    def is_grown(self) -> bool:
        return (
            self.entity is not None
            and self.entity != Entities.Dead_Pumpkin
            and self.grow_time > 0
            and self.grow_progress >= self.grow_time
        )


# ============================================================
# PUMPKIN YIELD FORMULA
# ============================================================

def _pumpkin_yield(component_size: int) -> int:
    """
    Yield for a mega pumpkin with `component_size` tiles in the connected group.

    Formula (max upgrade level):
      n = floor(sqrt(component_size))   # effective side-length dimension
      n < 6  → n³ × 512
      n >= 6 → n² × 6 × 512

    Note: fertilized pumpkins are infected; half yield goes to Weird Substance.
    Effective yield for infected: n²×6×256 = 98304 for 8x8 (confirmed in-game).
    """
    if component_size <= 0:
        return 0
    import math
    n = int(math.isqrt(component_size))
    if n == 0:
        return 0
    UPGRADE_MULTIPLIER = 512
    if n >= 6:
        return n * n * 6 * UPGRADE_MULTIPLIER
    return n * n * n * UPGRADE_MULTIPLIER


# ============================================================
# EXCEPTIONS
# ============================================================

class SimulationTimeout(Exception):
    pass


# ============================================================
# GAME STATE
# ============================================================

class GameState:
    def __init__(
        self,
        seed: Optional[int] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.rng = random.Random(seed)
        self.timeout_seconds = timeout_seconds

        self.grid: List[List[Tile]] = [
            [Tile(ground=Grounds.Grassland) for _ in range(WORLD_SIZE)]
            for _ in range(WORLD_SIZE)
        ]

        self.inventory: Dict[str, float] = {
            Items.Power:      float(STARTING_POWER),   # 1B — drone runs at powered speed throughout
            Items.Carrot:     float(STARTING_CARROTS),
            Items.Pumpkin:    0.0,
            Items.Water:      0.0,
            Items.Fertilizer: 0.0,
        }

        self.drone_x: int   = 0
        self.drone_y: int   = 0
        self.tick_count: int = 0
        self.sim_time:  float = 0.0
        self.action_count: int = 0

        # Statistics
        self.stat_total_actions:   int = 0
        self.stat_harvests:        int = 0
        self.stat_mega_harvests:   int = 0   # harvests of groups with >1 tile
        self.stat_plants:          int = 0
        self.stat_moves:           int = 0
        self.stat_dead_pumpkins:   int = 0   # total pumpkins that died
        self.stat_max_group_size:  int = 0   # largest connected group ever harvested
        self.stat_python_ticks:    int = 0
        self.stat_line_events:     int = 0
        self.stat_line_hits: Dict[int, int] = defaultdict(int)
        self.stat_line_ticks: Dict[int, int] = defaultdict(int)
        self.stat_api_calls: Dict[str, Dict[str, int]] = {}
        self.stat_measure_wrapped: int = 0

    def current_tile(self) -> Tile:
        return self.grid[self.drone_x][self.drone_y]

    def _tps(self) -> float:
        return TICKS_PER_SECOND_POWERED if self.inventory.get(Items.Power, 0) > 0 \
               else TICKS_PER_SECOND_UNPOWERED

    def advance_ticks(self, n: int, is_action: bool = False, source: Optional[str] = None) -> None:
        if n <= 0:
            return

        tps = self._tps()
        dt  = n / tps

        self.tick_count += n
        if source == "python":
            self.stat_python_ticks += n
        self.sim_time   += dt

        if self.sim_time > self.timeout_seconds:
            raise SimulationTimeout(
                f"Script exceeded {self.timeout_seconds:.0f}s simulated timeout "
                f"(tick {self.tick_count})"
            )

        water_per_sec = WATER_TANKS_PER_10S / 10.0
        fert_per_sec  = FERTILIZER_PER_10S  / 10.0
        self.inventory[Items.Water]      += water_per_sec * dt
        self.inventory[Items.Fertilizer] += fert_per_sec  * dt

        for col in self.grid:
            for tile in col:
                # Water decay
                if tile.water > 0.0:
                    tile.water *= math.exp(-WATER_DECAY_RATE * dt)
                    if tile.water < 1e-9:
                        tile.water = 0.0

                # Growth
                if (
                    tile.entity is not None
                    and tile.entity != Entities.Dead_Pumpkin
                    and tile.grow_time > 0
                    and tile.grow_progress < tile.grow_time
                ):
                    growth_rate = (
                        WATER_GROWTH_MIN
                        + (WATER_GROWTH_MAX - WATER_GROWTH_MIN) * tile.water
                    )
                    new_progress = min(
                        tile.grow_time,
                        tile.grow_progress + dt * growth_rate,
                    )

                    # Pumpkin death check: fires exactly once at the moment of maturity
                    if (
                        tile.entity == Entities.Pumpkin
                        and not tile.death_applied
                        and new_progress >= tile.grow_time
                        and tile.grow_progress < tile.grow_time
                    ):
                        tile.death_applied = True
                        if tile.pumpkin_will_die:
                            tile.entity = Entities.Dead_Pumpkin
                            self.stat_dead_pumpkins += 1
                            # Don't update grow_progress for dead tiles — it's irrelevant
                            continue

                    tile.grow_progress = new_progress

        # Power consumption
        if is_action:
            self.action_count       += 1
            self.stat_total_actions += 1
            if self.action_count >= POWER_CONSUMPTION_ACTIONS:
                self.action_count -= POWER_CONSUMPTION_ACTIONS
                cur = self.inventory.get(Items.Power, 0.0)
                if cur > 0:
                    self.inventory[Items.Power] = cur - 1.0

    def record_api_call(self, name: str, ticks: int, returned_false: bool, errored: bool) -> None:
        entry = self.stat_api_calls.get(name)
        if entry is None:
            entry = {
                "calls": 0,
                "ticks": 0,
                "false_returns": 0,
                "errors": 0,
            }
            self.stat_api_calls[name] = entry
        entry["calls"] += 1
        entry["ticks"] += max(0, ticks)
        if returned_false:
            entry["false_returns"] += 1
        if errored:
            entry["errors"] += 1

    def _clear_tile_entity(self, tile: Tile) -> None:
        tile.entity           = None
        tile.grow_progress    = 0.0
        tile.grow_time        = 0.0
        tile.petals           = None
        tile.infected         = False
        tile.pumpkin_will_die = False
        tile.death_applied    = False
        tile.pumpkin_id       = None


# ============================================================
# PUMPKIN HARVEST — SQUARE-ONLY MERGE MODEL
# ============================================================

def _do_pumpkin_harvest(state: GameState) -> int:
    """
    Harvest the largest fully-grown axis-aligned square that contains
    the drone's current tile. Touching non-square tiles are not included.
    Returns number of pumpkins added to inventory.
    """
    sx, sy = state.drone_x, state.drone_y

    def is_grown_pumpkin(x: int, y: int) -> bool:
        if not (0 <= x < WORLD_SIZE and 0 <= y < WORLD_SIZE):
            return False
        tile = state.grid[x][y]
        return tile.entity == Entities.Pumpkin and tile.is_grown()

    if not is_grown_pumpkin(sx, sy):
        # Should not happen when called from harvest() guard,
        # but keep behavior robust.
        return 0

    best_square: List[Tuple[int, int]] = [(sx, sy)]
    max_k = min(WORLD_SIZE, WORLD_SIZE)

    # Try all square sizes and placements that include (sx, sy).
    for k in range(2, max_k + 1):
        min_x0 = max(0, sx - k + 1)
        max_x0 = min(sx, WORLD_SIZE - k)
        min_y0 = max(0, sy - k + 1)
        max_y0 = min(sy, WORLD_SIZE - k)

        found_for_k = False
        for x0 in range(min_x0, max_x0 + 1):
            for y0 in range(min_y0, max_y0 + 1):
                ok = True
                for dx in range(k):
                    for dy in range(k):
                        if not is_grown_pumpkin(x0 + dx, y0 + dy):
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    square_tiles: List[Tuple[int, int]] = []
                    for dx in range(k):
                        for dy in range(k):
                            square_tiles.append((x0 + dx, y0 + dy))
                    best_square = square_tiles
                    found_for_k = True
                    break
            if found_for_k:
                break

    component = best_square

    count = len(component)
    total_yield = _pumpkin_yield(count)

    # Track stats
    state.stat_harvests += 1
    if count > 1:
        state.stat_mega_harvests += 1
    if count > state.stat_max_group_size:
        state.stat_max_group_size = count

    # Infection affects yield per infected tile, not whole-group all-or-nothing.
    # If k out of N tiles are infected, half of those tiles' proportional yield
    # converts into Weird Substance:
    #   pumpkin = total * (2N - k) / (2N)
    #   ws      = total - pumpkin
    infected_count = 0
    for x, y in component:
        if state.grid[x][y].infected:
            infected_count += 1

    if infected_count > 0 and count > 0:
        numerator = total_yield * (2 * count - infected_count)
        denominator = 2 * count
        pumpkin_yield = numerator // denominator
        ws_yield = total_yield - pumpkin_yield
    else:
        pumpkin_yield = total_yield
        ws_yield = 0

    # Remove all tiles in the mega pumpkin
    for x, y in component:
        state._clear_tile_entity(state.grid[x][y])

    state.inventory[Items.Pumpkin] = state.inventory.get(Items.Pumpkin, 0.0) + pumpkin_yield
    if ws_yield > 0:
        state.inventory[Items.Weird_Substance] = state.inventory.get(Items.Weird_Substance, 0.0) + ws_yield
    return pumpkin_yield


# ============================================================
# MOCK GAME API
# ============================================================

def build_namespace(state: GameState) -> Dict[str, Any]:

    # ── Movement ──────────────────────────────────────────────

    def move(direction):
        dx, dy = _DIRECTION_DELTA.get(direction, (0, 0))
        state.drone_x = (state.drone_x + dx) % WORLD_SIZE
        state.drone_y = (state.drone_y + dy) % WORLD_SIZE
        state.stat_moves += 1
        state.advance_ticks(200, is_action=True)
        return True

    def can_move(direction):
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
            t.ground = Grounds.Grassland
            # Tilling back destroys soil-based plants
            if t.entity in (
                Entities.Pumpkin, Entities.Dead_Pumpkin,
                Entities.Sunflower, Entities.Carrot, Entities.Cactus,
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
        # Dead pumpkins always return False (from docs)
        if t.entity == Entities.Dead_Pumpkin:
            return False
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

        # Dead pumpkins cannot be harvested (docs: can_harvest always False)
        if entity == Entities.Dead_Pumpkin:
            state.advance_ticks(1)
            return False

        # Tick cost paid before yield
        state.advance_ticks(200, is_action=True)

        if entity == Entities.Pumpkin:
            if not t.is_grown():
                # Not yet grown — nothing to harvest
                return False
            _do_pumpkin_harvest(state)

        elif entity == Entities.Grass:
            state.inventory[Items.Hay] = state.inventory.get(Items.Hay, 0.0) + 1
            state._clear_tile_entity(t)
            state.stat_harvests += 1

        elif entity == Entities.Bush:
            state.inventory[Items.Wood] = state.inventory.get(Items.Wood, 0.0) + 1
            state._clear_tile_entity(t)
            state.stat_harvests += 1

        elif entity == Entities.Carrot:
            if t.is_grown():
                state.inventory[Items.Carrot] = state.inventory.get(Items.Carrot, 0.0) + 1
            state._clear_tile_entity(t)
            state.stat_harvests += 1

        elif entity == Entities.Sunflower:
            # Basic sunflower support (no petal bonuses in this simulator)
            state.inventory[Items.Power] = state.inventory.get(Items.Power, 0.0) + 1
            state._clear_tile_entity(t)
            state.stat_harvests += 1

        else:
            state._clear_tile_entity(t)
            state.stat_harvests += 1

        return True

    # ── Planting ──────────────────────────────────────────────

    def plant(entity):
        t = state.current_tile()

        # Auto-remove dead pumpkin when planting (from docs:
        # "Planting a new plant in its place automatically removes the dead pumpkin")
        if t.entity == Entities.Dead_Pumpkin:
            state._clear_tile_entity(t)

        if t.entity is not None:
            state.advance_ticks(1)
            return False

        if entity == Entities.Pumpkin:
            if t.ground != Grounds.Soil:
                state.advance_ticks(1)
                return False
            if state.inventory.get(Items.Carrot, 0) < PUMPKIN_PLANT_COST_CARROT:
                state.advance_ticks(1)
                return False
            state.inventory[Items.Carrot] -= PUMPKIN_PLANT_COST_CARROT
            t.entity           = Entities.Pumpkin
            t.grow_time        = state.rng.uniform(PUMPKIN_GROW_TIME_MIN, PUMPKIN_GROW_TIME_MAX)
            t.grow_progress    = 0.0
            t.pumpkin_will_die = state.rng.random() < PUMPKIN_DEATH_CHANCE
            t.death_applied    = False
            t.infected         = False
            t.pumpkin_id       = state.rng.randint(0, 2**31)

        elif entity == Entities.Sunflower:
            if t.ground != Grounds.Soil:
                state.advance_ticks(1)
                return False
            if state.inventory.get(Items.Carrot, 0) < 1:
                state.advance_ticks(1)
                return False
            state.inventory[Items.Carrot] -= 1
            t.entity        = Entities.Sunflower
            t.grow_time     = state.rng.uniform(5.6, 8.4)
            t.grow_progress = 0.0
            t.petals        = state.rng.randint(7, 15)
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
            reduction = use_count * FERTILIZER_GROW_REDUCTION
            t.grow_progress = min(t.grow_time, t.grow_progress + reduction)
            t.infected = True

            # Check for pumpkin death trigger via fertilizer (instant maturity)
            if (
                t.entity == Entities.Pumpkin
                and not t.death_applied
                and t.grow_progress >= t.grow_time
            ):
                t.death_applied = True
                if t.pumpkin_will_die:
                    t.entity = Entities.Dead_Pumpkin
                    state.stat_dead_pumpkins += 1

            state.advance_ticks(200, is_action=True)
            return True

        if item == Items.Weird_Substance:
            available = int(state.inventory.get(Items.Weird_Substance, 0.0))
            use_count = min(n, available)
            if use_count <= 0:
                state.advance_ticks(1)
                return False
            state.inventory[Items.Weird_Substance] -= use_count
            t = state.current_tile()
            if t.entity is not None:
                t.infected = not t.infected
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx = state.drone_x + dx
                ny = state.drone_y + dy
                if 0 <= nx < WORLD_SIZE and 0 <= ny < WORLD_SIZE:
                    adj = state.grid[nx][ny]
                    if adj.entity is not None:
                        adj.infected = not adj.infected
            state.advance_ticks(200, is_action=True)
            return True

        state.advance_ticks(1)
        return False

    # ── Measure ───────────────────────────────────────────────

    def measure(direction=None):
        state.advance_ticks(1)
        if direction is not None:
            dx, dy = _DIRECTION_DELTA.get(direction, (0, 0))
            raw_tx = state.drone_x + dx
            raw_ty = state.drone_y + dy
            if raw_tx < 0 or raw_tx >= WORLD_SIZE or raw_ty < 0 or raw_ty >= WORLD_SIZE:
                state.stat_measure_wrapped += 1
            tx = raw_tx % WORLD_SIZE
            ty = raw_ty % WORLD_SIZE
            t = state.grid[tx][ty]
        else:
            t = state.current_tile()

        if t.entity == Entities.Sunflower:
            return t.petals

        if t.entity == Entities.Pumpkin:
            # "returns a mysterious number for a pumpkin" (builtins docs)
            # Returns a random unique ID assigned at plant time (grown or not)
            return t.pumpkin_id

        return None

    # ── Swap ──────────────────────────────────────────────────

    def swap(direction):
        dx, dy = _DIRECTION_DELTA.get(direction, (0, 0))
        nx = state.drone_x + dx
        ny = state.drone_y + dy
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
            t1.pumpkin_will_die, t2.pumpkin_will_die,
            t1.death_applied, t2.death_applied,
            t1.pumpkin_id, t2.pumpkin_id,
        ) = (
            t2.entity, t1.entity,
            t2.petals, t1.petals,
            t2.grow_progress, t1.grow_progress,
            t2.grow_time, t1.grow_time,
            t2.infected, t1.infected,
            t2.pumpkin_will_die, t1.pumpkin_will_die,
            t2.death_applied, t1.death_applied,
            t2.pumpkin_id, t1.pumpkin_id,
        )
        state.advance_ticks(200, is_action=True)
        return True

    # ── Inventory ─────────────────────────────────────────────

    def num_items(item):
        state.advance_ticks(1)
        return int(state.inventory.get(item, 0.0))

    # ── Companion ─────────────────────────────────────────────

    def get_companion():
        state.advance_ticks(1)
        return None

    # ── Cost ──────────────────────────────────────────────────

    def get_cost(thing, level=None):
        state.advance_ticks(1)
        if thing == Entities.Pumpkin:
            return {Items.Carrot: PUMPKIN_PLANT_COST_CARROT}
        if thing == Entities.Sunflower:
            return {Items.Carrot: 1}
        if thing == Entities.Carrot:
            return {Items.Wood: 1, Items.Hay: 1}
        return {}

    # ── Timing ────────────────────────────────────────────────

    def get_time():
        return state.sim_time

    def get_tick_count():
        return state.tick_count

    # ── Unlocks ───────────────────────────────────────────────

    def num_unlocked(thing):
        state.advance_ticks(1)
        return 1

    def unlock(thing):
        state.advance_ticks(200, is_action=False)
        return True

    # ── Misc ──────────────────────────────────────────────────

    def change_hat(hat):
        state.advance_ticks(200, is_action=True)

    def clear():
        for col in state.grid:
            for tile in col:
                tile.entity           = None
                tile.ground           = Grounds.Grassland
                tile.water            = 0.0
                tile.petals           = None
                tile.grow_progress    = 0.0
                tile.grow_time        = 0.0
                tile.infected         = False
                tile.pumpkin_will_die = False
                tile.death_applied    = False
                tile.pumpkin_id       = None
        state.drone_x = 0
        state.drone_y = 0
        state.advance_ticks(200, is_action=False)

    def set_execution_speed(speed):
        state.advance_ticks(200)

    def set_world_size(size):
        state.advance_ticks(200)

    def do_a_flip():
        state.sim_time += 1.0
        if state.sim_time > state.timeout_seconds:
            raise SimulationTimeout("Timeout during do_a_flip")

    def pet_the_piggy():
        state.sim_time += 1.0
        if state.sim_time > state.timeout_seconds:
            raise SimulationTimeout("Timeout during pet_the_piggy")

    def leaderboard_run(leaderboard, filename, speedup=1):
        state.advance_ticks(200)

    def simulate(*args, **kwargs):
        state.advance_ticks(200)
        return 0.0

    def spawn_drone(function):
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

    def quick_print(*args):
        pass

    def sim_print(*args):
        state.sim_time += 1.0
        if state.sim_time > state.timeout_seconds:
            raise SimulationTimeout("Timeout during print")

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

    def _range(*args):
        state.advance_ticks(1)
        return range(*args)

    def _instrument(name, fn):
        def _wrapped(*args, **kwargs):
            before = state.tick_count
            try:
                result = fn(*args, **kwargs)
            except Exception:
                after = state.tick_count
                state.record_api_call(name, after - before, returned_false=True, errored=True)
                raise
            after = state.tick_count
            state.record_api_call(name, after - before, returned_false=(result is False), errored=False)
            return result
        return _wrapped

    namespace = {
        "North": North, "East": East, "South": South, "West": West,
        "Entities": Entities, "Items": Items, "Grounds": Grounds,
        "Hats": Hats, "Leaderboards": Leaderboards, "Unlocks": Unlocks,
        "move": move, "can_move": can_move,
        "get_pos_x": get_pos_x, "get_pos_y": get_pos_y,
        "get_world_size": get_world_size,
        "get_ground_type": get_ground_type, "till": till,
        "get_entity_type": get_entity_type,
        "can_harvest": can_harvest, "harvest": harvest,
        "plant": plant,
        "get_water": get_water, "use_item": use_item,
        "measure": measure, "swap": swap,
        "num_items": num_items,
        "get_companion": get_companion,
        "get_cost": get_cost,
        "get_time": get_time, "get_tick_count": get_tick_count,
        "num_unlocked": num_unlocked, "unlock": unlock,
        "change_hat": change_hat, "clear": clear,
        "set_execution_speed": set_execution_speed,
        "set_world_size": set_world_size,
        "do_a_flip": do_a_flip, "pet_the_piggy": pet_the_piggy,
        "leaderboard_run": leaderboard_run, "simulate": simulate,
        "spawn_drone": spawn_drone, "wait_for": wait_for,
        "has_finished": has_finished, "max_drones": max_drones,
        "num_drones": num_drones,
        "print": sim_print, "quick_print": quick_print,
        "range": _range, "len": _len, "abs": _abs,
        "max": _max, "min": _min, "str": _str,
        "random": _random,
        "list": list, "dict": dict, "set": set, "tuple": tuple,
        "isinstance": isinstance, "type": type,
        "True": True, "False": False, "None": None,
        "__name__": "__main__",
        "__builtins__": __builtins__,
    }

    api_fn_names = [
        "move", "can_move",
        "get_pos_x", "get_pos_y", "get_world_size",
        "get_ground_type", "till",
        "get_entity_type", "can_harvest", "harvest", "plant",
        "get_water", "use_item", "measure", "swap", "num_items",
        "get_companion", "get_cost", "get_time", "get_tick_count",
        "num_unlocked", "unlock", "change_hat", "clear",
        "set_execution_speed", "set_world_size",
        "do_a_flip", "pet_the_piggy",
        "leaderboard_run", "simulate",
        "spawn_drone", "wait_for", "has_finished",
        "max_drones", "num_drones",
        "print", "quick_print",
        "range", "len", "abs", "max", "min", "str", "random",
    ]
    for fn_name in api_fn_names:
        namespace[fn_name] = _instrument(fn_name, namespace[fn_name])

    return namespace


# ============================================================
# OPERATOR/CONTROL TICK MODEL (same as sunflowers_simulator)
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
            state.stat_line_events += 1
            state.stat_line_hits[frame.f_lineno] += 1
            ticks = line_costs.get(frame.f_lineno, 0)
            if ticks > 0:
                state.stat_line_ticks[frame.f_lineno] += ticks
                state.advance_ticks(ticks, source="python")
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

    pumpkins = int(state.inventory.get(Items.Pumpkin, 0.0))
    won = pumpkins >= WIN_CONDITION_PUMPKINS and not timed_out and error is None
    python_ticks = state.stat_python_ticks
    non_python_ticks = state.tick_count - python_ticks
    script_lines = script_code.splitlines()
    top_python_lines: List[Dict[str, Any]] = []
    for lineno, ticks in sorted(state.stat_line_ticks.items(), key=lambda item: item[1], reverse=True)[:15]:
        line_text = ""
        if 1 <= lineno <= len(script_lines):
            line_text = script_lines[lineno - 1].strip()
        top_python_lines.append(
            {
                "line": lineno,
                "ticks": ticks,
                "hits": state.stat_line_hits.get(lineno, 0),
                "source": line_text,
            }
        )

    return {
        "time_seconds":      round(state.sim_time, 6),
        "pumpkins_collected": pumpkins,
        "won":               won,
        "timed_out":         timed_out,
        "error":             error,
        "total_actions":     state.stat_total_actions,
        "total_harvests":    state.stat_harvests,
        "mega_harvests":     state.stat_mega_harvests,
        "max_group_size":    state.stat_max_group_size,
        "total_plants":      state.stat_plants,
        "total_moves":       state.stat_moves,
        "dead_pumpkins":     state.stat_dead_pumpkins,
        "tick_count":        state.tick_count,
        "diagnostics": {
            "python_ticks": python_ticks,
            "non_python_ticks": non_python_ticks,
            "python_tick_share": round(python_ticks / state.tick_count, 6) if state.tick_count > 0 else 0.0,
            "line_events": state.stat_line_events,
            "measure_wrapped_calls": state.stat_measure_wrapped,
            "top_python_lines": top_python_lines,
            "api_calls": state.stat_api_calls,
        },
    }


# ============================================================
# CLI ENTRY POINT
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pumpkins_Single leaderboard simulator for 'The Farmer Was Replaced'",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python pumpkins_simulator.py --script myscript.py "
            "--iterations 50 --seed 42 --output results.json"
        ),
    )
    parser.add_argument("--script",     required=True, metavar="PATH")
    parser.add_argument("--iterations", type=int,   default=1,    metavar="N")
    parser.add_argument("--output",     default="output.json",    metavar="PATH")
    parser.add_argument("--timeout",    type=float, default=DEFAULT_TIMEOUT_SECONDS, metavar="SECONDS")
    parser.add_argument("--seed",       type=int,   default=None, metavar="N")
    parser.add_argument("--quiet",      action="store_true")
    args = parser.parse_args()

    try:
        with open(args.script) as f:
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
                f"time={result['time_seconds']:>12.3f}s  "
                f"pumpkins={result['pumpkins_collected']:>12}  "
                f"max_group={result['max_group_size']}",
                file=sys.stderr,
            )

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
        "win_condition_pumpkins":  WIN_CONDITION_PUMPKINS,
        "grow_time_range_seconds": [PUMPKIN_GROW_TIME_MIN, PUMPKIN_GROW_TIME_MAX],
        "death_chance":            PUMPKIN_DEATH_CHANCE,
        "plant_cost_carrot":       PUMPKIN_PLANT_COST_CARROT,
        "starting_power":          STARTING_POWER,
        "starting_carrots":        STARTING_CARROTS,
        "ticks_per_sec_unpowered": TICKS_PER_SECOND_UNPOWERED,
        "ticks_per_sec_powered":   TICKS_PER_SECOND_POWERED,
        "power_consumption_per_actions": POWER_CONSUMPTION_ACTIONS,
        "water_tanks_per_10s":     WATER_TANKS_PER_10S,
        "fertilizer_per_10s":      FERTILIZER_PER_10S,
        "timeout_seconds":         args.timeout,
    }

    output = {"summary": summary, "config": config, "runs": results}

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
                f"{args.timeout:.0f}s",
                file=sys.stderr,
            )
        if error_runs:
            print(f"WARNING: {len(error_runs)} run(s) raised errors.", file=sys.stderr)


if __name__ == "__main__":
    main()
