using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading;
using BepInEx;
using BepInEx.Logging;
using UnityEngine;

namespace TFWRRemoteAPI
{
    [BepInPlugin(PluginGuid, PluginName, PluginVersion)]
    public class Plugin : BaseUnityPlugin
    {
        public const string PluginGuid = "com.claudecode.tfwrapi";
        public const string PluginName = "TFWR Remote API";
        public const string PluginVersion = "1.0.0";
        public const int Port = 8787;

        public static Plugin Instance { get; private set; }
        public static ManualLogSource Log { get; private set; }

        private HttpListener _listener;
        private Thread _listenerThread;
        private volatile bool _running;

        // Main-thread dispatch queue
        private readonly ConcurrentQueue<Action> _mainThreadQueue = new ConcurrentQueue<Action>();

        // For synchronous main-thread calls from HTTP threads
        private readonly ConcurrentDictionary<string, ManualResetEventSlim> _pendingEvents
            = new ConcurrentDictionary<string, ManualResetEventSlim>();
        private readonly ConcurrentDictionary<string, string> _pendingResults
            = new ConcurrentDictionary<string, string>();

        // Track active run
        private volatile string _activeRunId = null;
        private volatile bool _runFinished = false;
        private volatile string _runMode = null;

        private void Awake()
        {
            Instance = this;
            Log = Logger;
            Log.LogInfo("TFWR Remote API plugin loaded!");

            try
            {
                _listener = new HttpListener();
                _listener.Prefixes.Add($"http://localhost:{Port}/");
                _listener.Start();
                _running = true;

                _listenerThread = new Thread(ListenLoop)
                {
                    IsBackground = true,
                    Name = "TFWRRemoteAPI-HTTP"
                };
                _listenerThread.Start();

                Log.LogInfo($"HTTP API listening on http://localhost:{Port}/");
            }
            catch (Exception ex)
            {
                Log.LogError($"Failed to start HTTP listener: {ex.Message}");
            }
        }

        private void OnDestroy()
        {
            _running = false;
            try { _listener?.Stop(); } catch { }
            try { _listener?.Close(); } catch { }
        }

        private void Update()
        {
            // Drain main-thread queue
            while (_mainThreadQueue.TryDequeue(out var action))
            {
                try
                {
                    action();
                }
                catch (Exception ex)
                {
                    Log.LogError($"Main thread action error: {ex}");
                }
            }

            // Check if a run has finished
            if (_activeRunId != null && !_runFinished)
            {
                try
                {
                    var mainSim = MainSim.Inst;
                    if (mainSim != null)
                    {
                        bool finished;
                        if (_runMode == "simulate")
                        {
                            finished = !mainSim.MightBeSimulating();
                        }
                        else
                        {
                            finished = !mainSim.IsExecuting();
                        }
                        if (finished)
                        {
                            _runFinished = true;
                        }
                    }
                }
                catch { }
            }
        }

        // ── HTTP Listener Loop ──────────────────────────────────

        private void ListenLoop()
        {
            while (_running)
            {
                try
                {
                    var ctx = _listener.GetContext();
                    ThreadPool.QueueUserWorkItem(_ => HandleRequest(ctx));
                }
                catch (HttpListenerException) when (!_running)
                {
                    break;
                }
                catch (Exception ex)
                {
                    if (_running) Log.LogError($"Listener error: {ex.Message}");
                }
            }
        }

        private void HandleRequest(HttpListenerContext ctx)
        {
            try
            {
                var path = ctx.Request.Url.AbsolutePath.TrimEnd('/');
                var method = ctx.Request.HttpMethod;

                string responseJson;
                switch (path)
                {
                    case "/status":
                        responseJson = HandleStatus();
                        break;
                    case "/run-script":
                        if (method != "POST")
                        {
                            responseJson = JsonError("POST required");
                            break;
                        }
                        responseJson = HandleRunScript(ctx.Request);
                        break;
                    case "/poll":
                        responseJson = HandlePoll();
                        break;
                    case "/output":
                        responseJson = HandleOutput();
                        break;
                    case "/inventory":
                        responseJson = HandleInventory();
                        break;
                    case "/stop":
                        responseJson = HandleStop();
                        break;
                    default:
                        responseJson = JsonError($"Unknown endpoint: {path}");
                        break;
                }

                SendResponse(ctx.Response, responseJson);
            }
            catch (Exception ex)
            {
                try
                {
                    SendResponse(ctx.Response, JsonError(ex.Message), 500);
                }
                catch { }
            }
        }

        // ── Endpoint Handlers ───────��───────────────────────────

        private string HandleStatus()
        {
            string result = RunOnMainThreadSync(() =>
            {
                var mainSim = MainSim.Inst;
                if (mainSim == null)
                    return "{\"ready\":false}";

                bool executing = mainSim.IsExecuting();
                bool simulating = mainSim.MightBeSimulating();
                string activeRun = _activeRunId ?? "";
                bool runDone = _runFinished;

                return $"{{\"ready\":true,\"executing\":{Bool(executing)},\"simulating\":{Bool(simulating)},"
                     + $"\"active_run_id\":\"{Escape(activeRun)}\",\"run_finished\":{Bool(runDone)}}}";
            });
            return result;
        }

        private string HandleRunScript(HttpListenerRequest request)
        {
            string body;
            using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
            {
                body = reader.ReadToEnd();
            }

            // Simple JSON parsing (no external deps in .NET 4.6 BepInEx)
            var code = ExtractJsonString(body, "code");
            var filename = ExtractJsonString(body, "filename") ?? "claude_diag";
            var mode = ExtractJsonString(body, "mode") ?? "execute";
            var seedStr = ExtractJsonString(body, "seed");
            int seed = -1;
            if (seedStr != null) int.TryParse(seedStr, out seed);

            if (string.IsNullOrEmpty(code))
                return JsonError("'code' field is required");

            string runId = Guid.NewGuid().ToString("N").Substring(0, 8);

            string result = RunOnMainThreadSync(() =>
            {
                try
                {
                    var mainSim = MainSim.Inst;
                    if (mainSim == null)
                        return JsonError("MainSim not ready");

                    // Stop any existing execution
                    if (mainSim.IsExecuting())
                        mainSim.StopMainExecution();
                    if (mainSim.MightBeSimulating())
                        mainSim.RestoreMainSim();

                    // Write code to save file
                    string savePath = GameBridge.GetActiveSavePath();
                    string filePath = Path.Combine(savePath, filename + ".py");
                    File.WriteAllText(filePath, code);

                    // Let file watcher pick it up, or apply directly
                    Saver.ApplyCodeChanges(mainSim.workspace);

                    // Ensure code window exists with our code
                    if (!mainSim.workspace.codeWindows.ContainsKey(filename))
                    {
                        // Open the file as a code window
                        GameBridge.OpenCodeFile(mainSim, filename, code);
                    }

                    // Update the code in the window
                    if (mainSim.workspace.codeWindows.TryGetValue(filename, out var cw))
                    {
                        cw.CodeInput.text = code;
                    }
                    else
                    {
                        return JsonError($"Could not create code window '{filename}'");
                    }

                    // Clear output
                    global::Logger.Clear();

                    _activeRunId = runId;
                    _runFinished = false;
                    _runMode = mode;

                    if (mode == "simulate")
                    {
                        var unlockList = GameBridge.ParseUnlocks(body);
                        var items = GameBridge.ParseItems(body);

                        var args = new MainSim.LeaderboardStartArgs(
                            filename,
                            unlockList,
                            items,
                            new List<KeyValuePair<string, IPyObject>>(),
                            "",  // leaderboardName
                            "",  // steamLeaderboardName
                            LeaderboardType.simulation,
                            seed
                        );
                        Log.LogInfo($"Scheduling leaderboard start for '{filename}' with {unlockList.Count} unlocks, seed={seed}");
                        Log.LogInfo($"Items: cactus={items.items[4]}, power={items.items[10]}");
                        mainSim.ScheduleLeaderboardStart(args);
                        Log.LogInfo("ScheduleLeaderboardStart called successfully");
                    }
                    else
                    {
                        // Direct execution
                        if (mainSim.workspace.codeWindows.TryGetValue(filename, out var codeWindow))
                        {
                            var node = codeWindow.Parse();
                            if (node != null)
                            {
                                mainSim.StartMainExecution(codeWindow, node);
                            }
                            else
                            {
                                return JsonError("Parse error in script");
                            }
                        }
                    }

                    return $"{{\"started\":true,\"run_id\":\"{runId}\",\"mode\":\"{Escape(mode)}\"}}";
                }
                catch (Exception ex)
                {
                    return JsonError($"Run failed: {ex.Message}\n{ex.StackTrace}");
                }
            });

            return result;
        }

        private string HandlePoll()
        {
            string result = RunOnMainThreadSync(() =>
            {
                try
                {
                    string runId = _activeRunId ?? "";
                    bool finished = _runFinished;
                    string output = global::Logger.GetOutputString() ?? "";

                    var mainSim = MainSim.Inst;
                    double timeSeconds = 0;
                    string itemsJson = "{}";

                    if (mainSim != null)
                    {
                        // Try to read sim time from current or stored sim
                        var sim = GameBridge.GetActiveSim(mainSim);
                        if (sim != null)
                        {
                            timeSeconds = sim.CurrentTime.Seconds;
                            itemsJson = GameBridge.GetInventoryJson(sim);
                        }
                    }

                    return $"{{\"run_id\":\"{Escape(runId)}\",\"finished\":{Bool(finished)},"
                         + $"\"time_seconds\":{timeSeconds:F6},"
                         + $"\"output\":\"{Escape(output)}\","
                         + $"\"items\":{itemsJson}}}";
                }
                catch (Exception ex)
                {
                    return JsonError($"Poll error: {ex.Message}");
                }
            });
            return result;
        }

        private string HandleOutput()
        {
            string result = RunOnMainThreadSync(() =>
            {
                string output = global::Logger.GetOutputString() ?? "";
                return $"{{\"output\":\"{Escape(output)}\"}}";
            });
            return result;
        }

        private string HandleInventory()
        {
            string result = RunOnMainThreadSync(() =>
            {
                try
                {
                    var mainSim = MainSim.Inst;
                    if (mainSim == null)
                        return JsonError("MainSim not ready");

                    var sim = GameBridge.GetActiveSim(mainSim);
                    if (sim == null)
                        return JsonError("No active simulation");

                    return $"{{\"items\":{GameBridge.GetInventoryJson(sim)}}}";
                }
                catch (Exception ex)
                {
                    return JsonError($"Inventory error: {ex.Message}");
                }
            });
            return result;
        }

        private string HandleStop()
        {
            string result = RunOnMainThreadSync(() =>
            {
                try
                {
                    var mainSim = MainSim.Inst;
                    if (mainSim == null)
                        return JsonError("MainSim not ready");

                    if (mainSim.MightBeSimulating())
                        mainSim.RestoreMainSim();
                    if (mainSim.IsExecuting())
                        mainSim.StopMainExecution();

                    _activeRunId = null;
                    _runFinished = true;
                    return "{\"stopped\":true}";
                }
                catch (Exception ex)
                {
                    return JsonError($"Stop error: {ex.Message}");
                }
            });
            return result;
        }

        // ── Main Thread Sync ────────────────────────────────────

        private string RunOnMainThreadSync(Func<string> func, int timeoutMs = 10000)
        {
            if (Thread.CurrentThread.ManagedThreadId == GameBridge.MainThreadId)
            {
                return func();
            }

            string callId = Guid.NewGuid().ToString("N");
            var evt = new ManualResetEventSlim(false);
            _pendingEvents[callId] = evt;

            _mainThreadQueue.Enqueue(() =>
            {
                try
                {
                    _pendingResults[callId] = func();
                }
                catch (Exception ex)
                {
                    _pendingResults[callId] = JsonError(ex.Message);
                }
                finally
                {
                    evt.Set();
                }
            });

            if (!evt.Wait(timeoutMs))
            {
                _pendingEvents.TryRemove(callId, out _);
                return JsonError("Main thread call timed out");
            }

            _pendingEvents.TryRemove(callId, out _);
            _pendingResults.TryRemove(callId, out var result);
            evt.Dispose();
            return result ?? JsonError("No result");
        }

        // ── JSON Helpers ───────────��────────────────────────────

        private static string JsonError(string msg)
        {
            return $"{{\"error\":\"{Escape(msg)}\"}}";
        }

        private static string Bool(bool v) => v ? "true" : "false";

        private static string Escape(string s)
        {
            if (s == null) return "";
            return s.Replace("\\", "\\\\")
                    .Replace("\"", "\\\"")
                    .Replace("\n", "\\n")
                    .Replace("\r", "\\r")
                    .Replace("\t", "\\t");
        }

        // Minimal JSON string extractor (no external JSON lib in .NET 4.6)
        internal static string ExtractJsonString(string json, string key)
        {
            string pattern = "\"" + key + "\"";
            int idx = json.IndexOf(pattern);
            if (idx < 0) return null;
            idx += pattern.Length;

            // Skip whitespace and colon
            while (idx < json.Length && (json[idx] == ' ' || json[idx] == ':' || json[idx] == '\t'))
                idx++;

            if (idx >= json.Length) return null;

            if (json[idx] == '"')
            {
                // String value
                idx++;
                var sb = new StringBuilder();
                while (idx < json.Length && json[idx] != '"')
                {
                    if (json[idx] == '\\' && idx + 1 < json.Length)
                    {
                        idx++;
                        switch (json[idx])
                        {
                            case 'n': sb.Append('\n'); break;
                            case 'r': sb.Append('\r'); break;
                            case 't': sb.Append('\t'); break;
                            case '\\': sb.Append('\\'); break;
                            case '"': sb.Append('"'); break;
                            default: sb.Append(json[idx]); break;
                        }
                    }
                    else
                    {
                        sb.Append(json[idx]);
                    }
                    idx++;
                }
                return sb.ToString();
            }
            else
            {
                // Number or literal
                var sb = new StringBuilder();
                while (idx < json.Length && json[idx] != ',' && json[idx] != '}' && json[idx] != ' ')
                {
                    sb.Append(json[idx]);
                    idx++;
                }
                return sb.ToString();
            }
        }

        private static void SendResponse(HttpListenerResponse response, string json, int statusCode = 200)
        {
            response.StatusCode = statusCode;
            response.ContentType = "application/json";
            response.Headers.Add("Access-Control-Allow-Origin", "*");
            var buffer = Encoding.UTF8.GetBytes(json);
            response.ContentLength64 = buffer.Length;
            response.OutputStream.Write(buffer, 0, buffer.Length);
            response.OutputStream.Close();
        }
    }
}
