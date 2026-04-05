#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/TFWRRemoteAPI"
GAME_DIR="$HOME/.local/share/Steam/steamapps/common/The Farmer Was Replaced"
PLUGIN_DIR="$GAME_DIR/BepInEx/plugins"

echo "Building TFWRRemoteAPI..."
cd "$PROJECT_DIR"

# Build with .NET SDK targeting net46
dotnet build -c Release 2>&1

# Find the output DLL
DLL_PATH="$PROJECT_DIR/bin/Release/TFWRRemoteAPI.dll"
if [ ! -f "$DLL_PATH" ]; then
    echo "ERROR: Build output not found at $DLL_PATH"
    echo "Checking for DLL in other locations..."
    find "$PROJECT_DIR/bin" -name "TFWRRemoteAPI.dll" 2>/dev/null
    exit 1
fi

# Copy to BepInEx plugins
cp "$DLL_PATH" "$PLUGIN_DIR/TFWRRemoteAPI.dll"
echo "Installed to $PLUGIN_DIR/TFWRRemoteAPI.dll"
echo "Done! Restart the game to load the mod."
