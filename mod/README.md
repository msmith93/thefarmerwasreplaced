# TFWR Remote API - BepInEx Mod

A BepInEx plugin for **The Farmer Was Replaced** that exposes an HTTP API on `localhost:8787`, allowing external tools (like Claude Code) to run scripts, trigger simulations, and read results from the game in real time.

## Prerequisites

- **The Farmer Was Replaced** (Steam, Unity 6)
- **BepInEx 5.4.23** installed in the game directory
- **.NET SDK** (for building; any version that supports `net46` target)

## Building

```bash
cd mod/
bash build.sh
```

This compiles the plugin and copies `TFWRRemoteAPI.dll` to `BepInEx/plugins/`. Restart the game to load the mod.

## Verifying It Works

After launching the game, check the BepInEx log or run:

```bash
curl http://localhost:8787/status
```

Expected response:

```json
{
  "ready": true,
  "executing": false,
  "simulating": false,
  "active_run_id": "",
  "run_finished": false
}
```

## API Endpoints

### `GET /status`

Returns the current game state.

```json
{
  "ready": true,
  "executing": false,
  "simulating": false,
  "active_run_id": "",
  "run_finished": false
}
```

- `ready` - whether `MainSim` is initialized
- `executing` - whether code is currently executing (direct mode)
- `simulating` - whether a simulation is running
- `active_run_id` - ID of the current run (empty if none)
- `run_finished` - whether the active run has completed

### `POST /run-script`

Runs a script in the game. Accepts JSON body:

```json
{
  "code": "quick_print(\"hello world\")",
  "filename": "my_script",
  "mode": "execute",
  "seed": 1,
  "items": {
    "cactus": 1000000000,
    "power": 1000000000
  }
}
```

**Parameters:**

| Field      | Required | Default       | Description                                                               |
| ---------- | -------- | ------------- | ------------------------------------------------------------------------- |
| `code`     | Yes      | -             | Python-like script code to run                                            |
| `filename` | No       | `claude_diag` | Name for the code file (without `.py`)                                    |
| `mode`     | No       | `execute`     | `"execute"` for direct run, `"simulate"` for leaderboard-style simulation |
| `seed`     | No       | `-1`          | RNG seed for simulate mode (-1 = random)                                  |
| `items`    | No       | `{}`          | Starting items for simulate mode (e.g. `{"cactus": 1000000000}`)          |
| `unlocks`  | No       | all at max    | Unlocks for simulate mode (e.g. `{"speed": 3, "expand": 1}`)             |

**Modes:**

- **`execute`** - Runs the script directly in the current game state. Fast, good for quick tests. Uses the game's live farm.
- **`simulate`** - Runs via `ScheduleLeaderboardStart` with `LeaderboardType.simulation`. Starts a fresh farm with the specified unlocks and items. By default all unlocks are at max level. This is the same as calling `simulate()` from in-game code.

**Response:**

```json
{ "started": true, "run_id": "a1b2c3d4", "mode": "simulate" }
```

### `GET /poll`

Polls the current run for completion status, output, timing, and inventory.

```json
{
  "run_id": "a1b2c3d4",
  "finished": true,
  "time_seconds": 42.5,
  "output": "hello world\nresult: 123",
  "items": { "bone": 33488928, "cactus": 500000 }
}
```

- `finished` - whether the run has completed
- `time_seconds` - simulation time elapsed (in-game seconds)
- `output` - all `quick_print()` output captured so far
- `items` - current inventory snapshot

### `GET /output`

Returns just the `quick_print()` output buffer. Useful for streaming output during long runs.

```json
{ "output": "line 1\nline 2\nline 3" }
```

### `GET /inventory`

Returns the current farm inventory.

```json
{ "items": { "bone": 1024, "cactus": 999999000, "power": 999998000 } }
```

### `POST /stop`

Stops any active execution or simulation and resets the run state.

```json
{ "stopped": true }
```

## Usage Examples

### Run a simple script

```bash
curl -X POST http://localhost:8787/run-script \
  -d '{"code":"quick_print(\"hello\")", "mode":"execute"}'

# Poll for result
sleep 1
curl http://localhost:8787/poll
```

### Run a simulation script in the game

```bash
curl -X POST http://localhost:8787/run-script -d '{
  "code": "simulate(\"dino_test\", Unlocks, {Items.Carrot : 10000, Items.Hay : 50}, {\"a\" : 13}, 0, 1)",
  "mode": "execute" 
}'
```

This will run a `simulate` script in the game. This will allow testing of many different scenarios.
For example, you can set up a for loop that tests a script with various different water thresholds
(set with the globals that are injected into the simulation). 

### Run a simulation directly
Normally executing a simulation directly is sufficient for troubleshooting. However, if there is a
need to run the `simulate` functionality directly, that is also supported:

```bash
curl -X POST http://localhost:8787/run-script -d '{
  "code": "change_hat(Hats.Dinosaur_Hat)\nfor i in range(31):\n    move(North)\nmove(East)\nfor i in range(31):\n    move(South)\nchange_hat(Hats.Gray_Hat)\nquick_print(\"bones: \", num_items(Items.Bone))",
  "filename": "dino_test",
  "mode": "simulate",
  "seed": 1,
  "items": {"cactus": 1000000000, "power": 1000000000}
}'

# Poll until finished
while true; do
  result=$(curl -s http://localhost:8787/poll)
  echo "$result" | python3 -m json.tool
  echo "$result" | grep -q '"finished":true' && break
  sleep 2
done
```

#### Run a simulation with specific unlocks

```bash
curl -X POST http://localhost:8787/run-script -d '{
  "code": "quick_print(\"speed test\")",
  "mode": "simulate",
  "seed": 1,
  "unlocks": {"debug": 1, "speed": 3, "plant": 1},
  "items": {"cactus": 1000000000, "power": 1000000000}
}'
```

If `unlocks` is omitted, all unlocks default to max level. Values are levels for multi-unlocks (clamped to the unlock's max); any value >= 1 means "unlocked" for non-multi-unlocks. Unknown unlock names are logged as warnings.

### Run a diagnostic script from file

```bash
python3 -c "
import json
with open('iterations/diag_apple_cactus_cost.py') as f:
    code = f.read()
payload = {
    'code': code,
    'filename': 'claude_diag',
    'mode': 'simulate',
    'seed': 1,
    'items': {'cactus': 1000000000, 'power': 1000000000}
}
print(json.dumps(payload))
" > /tmp/payload.json

curl -X POST http://localhost:8787/run-script -d @/tmp/payload.json
sleep 5
curl http://localhost:8787/poll
```

## Architecture

```
Plugin.cs          - BepInEx plugin entry point, HTTP listener, endpoint routing
GameBridge.cs      - Safe wrappers around game APIs (save paths, code windows, inventory)
```

- HTTP listener runs on a background thread
- All game state access is dispatched to Unity's main thread via a `ConcurrentQueue<Action>` drained in `Update()`
- Simulate mode uses `MainSim.ScheduleLeaderboardStart()` with configurable unlocks (defaults to all at max level)
- Output is read from the game's `Logger` static class (`quick_print()` output)

## Notes

- The game must be running and fully loaded (past the main menu into a save) for the API to work
- Simulate mode runs at the game's simulation speed; long scripts may take real-world time to complete
- Each `/run-script` call stops any previous execution before starting a new one
- The mod listens on `localhost` only; it is not accessible from other machines
- Items in simulate mode are specified by name (lowercase): `bone`, `cactus`, `carrot`, `hay`, `wood`, `pumpkin`, `power`, `gold`, `water`, `fertilizer`, `weird_substance`

## Troubleshooting

- **"Main thread call timed out"** - The game's main thread is busy (e.g., during a heavy simulation). Try `/stop` first.
- **No output from simulate mode** - Make sure your script uses `quick_print()`. Regular `print()` is not captured.
- **Build errors about missing types** - Ensure the game DLLs are accessible at the paths in `TFWRRemoteAPI.csproj`. The paths assume a standard Linux/Steam installation.
