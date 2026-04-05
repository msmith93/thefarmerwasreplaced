using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
using UnityEngine;

namespace TFWRRemoteAPI
{
    public static class GameBridge
    {
        private static int _mainThreadId;

        public static int MainThreadId
        {
            get
            {
                if (_mainThreadId == 0)
                    _mainThreadId = Thread.CurrentThread.ManagedThreadId;
                return _mainThreadId;
            }
        }

        // Initialize on first Update call from Plugin
        public static void EnsureMainThread()
        {
            if (_mainThreadId == 0)
                _mainThreadId = Thread.CurrentThread.ManagedThreadId;
        }

        /// <summary>
        /// Get the path to the active save directory.
        /// </summary>
        public static string GetActiveSavePath()
        {
            // The game stores persistent data in Unity's persistentDataPath,
            // which on Linux/Proton is under the compat data folder.
            // We can get it the same way the game does.
            string persistentPath = Application.persistentDataPath;
            string activeSave = OptionHolder.GetString("activeSave", "Save0");
            string savePath = Path.Combine(persistentPath, "Saves", activeSave);

            if (!Directory.Exists(savePath))
                Directory.CreateDirectory(savePath);

            return savePath;
        }

        /// <summary>
        /// Open a code file in the workspace as a new CodeWindow.
        /// Signature: OpenCodeWindow(string fileName, string code, Vector2 offset, Vector2 size)
        /// </summary>
        public static void OpenCodeFile(MainSim mainSim, string filename, string code = "")
        {
            try
            {
                var workspace = mainSim.workspace;
                workspace.OpenCodeWindow(filename, code, new Vector2(100f, -100f));
                Plugin.Log.LogInfo($"Opened code window '{filename}'");
            }
            catch (Exception ex)
            {
                Plugin.Log.LogError($"Failed to open code file '{filename}': {ex}");
            }
        }

        /// <summary>
        /// Get the active Simulation object (handles simulate-in-simulate nesting).
        /// </summary>
        public static Simulation GetActiveSim(MainSim mainSim)
        {
            // If there's a stored sim, the game is in simulate() mode;
            // the active sim is accessible via a private field.
            try
            {
                var simField = typeof(MainSim).GetField("sim",
                    BindingFlags.NonPublic | BindingFlags.Instance);

                if (simField != null)
                {
                    return (Simulation)simField.GetValue(mainSim);
                }
            }
            catch (Exception ex)
            {
                Plugin.Log.LogError($"GetActiveSim error: {ex.Message}");
            }
            return null;
        }

        /// <summary>
        /// Parse items from JSON body into an ItemBlock.
        /// Expects an "items" key with sub-object like {"cactus": 1000000000, "power": 1000000000}
        /// </summary>
        public static ItemBlock ParseItems(string json)
        {
            var items = ItemBlock.CreateEmpty();

            // Find the "items" object
            int idx = json.IndexOf("\"items\"");
            if (idx < 0) return items;

            idx = json.IndexOf('{', idx + 7);
            if (idx < 0) return items;

            int depth = 1;
            int start = idx + 1;
            int end = start;
            while (end < json.Length && depth > 0)
            {
                if (json[end] == '{') depth++;
                else if (json[end] == '}') depth--;
                if (depth > 0) end++;
            }

            string itemsStr = json.Substring(start, end - start);

            // Parse key-value pairs
            var itemMap = new Dictionary<string, double>(StringComparer.OrdinalIgnoreCase)
            {
                { "bone", 0 }, { "cactus", 0 }, { "carrot", 0 },
                { "hay", 0 }, { "wood", 0 }, { "pumpkin", 0 },
                { "power", 0 }, { "gold", 0 }, { "water", 0 },
                { "fertilizer", 0 }, { "weird_substance", 0 }
            };

            foreach (var pair in itemsStr.Split(','))
            {
                var parts = pair.Split(':');
                if (parts.Length != 2) continue;

                string key = parts[0].Trim().Trim('"').ToLowerInvariant();
                string valStr = parts[1].Trim().Trim('"');
                if (double.TryParse(valStr, out double val) && itemMap.ContainsKey(key))
                {
                    itemMap[key] = val;
                }
            }

            // Map to ItemBlock using ResourceManager
            // First, build a name->index lookup from all game items
            var nameToId = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            try
            {
                foreach (var item in ResourceManager.GetAllItems())
                {
                    if (item != null && !string.IsNullOrEmpty(item.itemName))
                    {
                        nameToId[item.itemName] = item.itemId;
                    }
                }
                Plugin.Log.LogInfo($"Item name lookup built: {string.Join(", ", nameToId.Keys)}");
            }
            catch (Exception ex)
            {
                Plugin.Log.LogError($"Failed to build item lookup: {ex.Message}");
            }

            foreach (var kvp in itemMap)
            {
                if (kvp.Value > 0)
                {
                    if (nameToId.TryGetValue(kvp.Key, out int id))
                    {
                        if (id >= 0 && id < items.items.Length)
                        {
                            items.items[id] = kvp.Value;
                            Plugin.Log.LogInfo($"Set item '{kvp.Key}' (id={id}) = {kvp.Value}");
                        }
                        else
                        {
                            Plugin.Log.LogWarning($"Item '{kvp.Key}' id={id} out of range (max={items.items.Length})");
                        }
                    }
                    else
                    {
                        Plugin.Log.LogWarning($"Could not map item '{kvp.Key}' to game item. Known items: {string.Join(", ", nameToId.Keys)}");
                    }
                }
            }

            return items;
        }

        /// <summary>
        /// Build a JSON object of the current inventory.
        /// </summary>
        public static string GetInventoryJson(Simulation sim)
        {
            try
            {
                if (sim?.farm == null) return "{}";

                var itemBlock = sim.farm.Items;
                if (itemBlock == null) return "{}";

                var sb = new StringBuilder("{");
                bool first = true;

                foreach (var itemSO in ResourceManager.GetAllItems())
                {
                    double amount = 0;
                    if (itemSO.itemId >= 0 && itemSO.itemId < itemBlock.items.Length)
                    {
                        amount = itemBlock.items[itemSO.itemId];
                    }

                    if (amount != 0 || itemSO.itemName == "bone" || itemSO.itemName == "cactus" || itemSO.itemName == "power")
                    {
                        if (!first) sb.Append(",");
                        sb.Append($"\"{itemSO.itemName}\":{amount}");
                        first = false;
                    }
                }

                sb.Append("}");
                return sb.ToString();
            }
            catch (Exception ex)
            {
                Plugin.Log.LogError($"GetInventoryJson error: {ex.Message}");
                return "{}";
            }
        }
    }
}
