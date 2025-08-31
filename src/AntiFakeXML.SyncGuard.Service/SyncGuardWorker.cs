using AntiFakeXML.Core;
using System.IO;

namespace SyncGuard;

public class SyncGuardWorker : BackgroundService
{
    private AppConfig _cfg = new();
    private FileSystemWatcher? _xmlWatcher;
    
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        Log.LogDirectory = _cfg.LogDir;
        Directory.CreateDirectory(_cfg.LogDir);
        Log.Info("syncguard-start");

        ManifestValidator.Load(_cfg.ManifestPath, _cfg.MasterSyncFolder);

        if (_cfg.InitialFullScan)
        {
            try
            {
                await Task.Run(() => InitialScan(stoppingToken), stoppingToken);
            }
            catch (Exception ex)
            {
                Log.Error($"initial-scan-error {ex}");
            }
        }

        // Watch manifest changes and master folder to hot-reload
        using var fswManifest = new FileSystemWatcher(Path.GetDirectoryName(_cfg.ManifestPath) ?? ".", Path.GetFileName(_cfg.ManifestPath));
        fswManifest.NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size | NotifyFilters.FileName;
        fswManifest.Changed += (_, __) => SafeReloadManifest();
        fswManifest.Created += (_, __) => SafeReloadManifest();
        fswManifest.Renamed += (_, __) => SafeReloadManifest();
        fswManifest.EnableRaisingEvents = true;

        // Watch XML files in all scan roots for real-time overwrite
        SetupXmlWatchers();

        // Idle loop
        while (!stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(3000, stoppingToken);
        }
    }

    private void SetupXmlWatchers()
    {
        try
        {
            foreach (var root in _cfg.InitialScanRoots.Where(Directory.Exists))
            {
                var watcher = new FileSystemWatcher(root, "*.xml");
                watcher.NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.CreationTime | NotifyFilters.FileName;
                watcher.Created += OnXmlFileChanged;
                watcher.Changed += OnXmlFileChanged;
                watcher.EnableRaisingEvents = true;
                
                // Lưu reference để tránh bị dispose
                _xmlWatcher = watcher;
                
                Log.Info($"xml-watcher-setup root={root}");
            }
        }
        catch (Exception ex)
        {
            Log.Error($"xml-watcher-setup-error {ex.Message}");
        }
    }

    private void OnXmlFileChanged(object sender, FileSystemEventArgs e)
    {
        try
        {
            Log.Info($"xml-file-detected path={e.FullPath} change={e.ChangeType}");
            
            // Đợi file hoàn tất ghi
            Task.Delay(100).Wait();
            
            if (TryOverwriteFile(e.FullPath))
            {
                Log.Info($"xml-file-overwritten path={e.FullPath}");
            }
        }
        catch (Exception ex)
        {
            Log.Error($"xml-file-process-error path={e.FullPath} error={ex.Message}");
        }
    }

    private bool TryOverwriteFile(string xmlPath)
    {
        try
        {
            if (!XmlFieldsExtractor.TryExtractKey(xmlPath, out var key, out var error))
            {
                Log.Warn($"xml-extract-failed path={xmlPath} error={error}");
                return false;
            }

            if (!ManifestValidator.TryGetOriginal(key, out var original, out var entry))
            {
                Log.Warn($"xml-no-original-found key={key} path={xmlPath}");
                return false;
            }

            var origBytes = File.ReadAllBytes(original);
            FileTimeUtil.OverwriteBytesKeepTimes(xmlPath, origBytes);
            Log.Info($"xml-overwrite-success key={key} original={original} target={xmlPath}");
            return true;
        }
        catch (Exception ex)
        {
            Log.Error($"xml-overwrite-error path={xmlPath} error={ex.Message}");
            return false;
        }
    }

    private void SafeReloadManifest()
    {
        try
        {
            ManifestValidator.Load(_cfg.ManifestPath, _cfg.MasterSyncFolder);
            Log.Info("manifest-reloaded");
        }
        catch (Exception ex)
        {
            Log.Error($"manifest-reload-fail {ex.Message}");
        }
    }

    private void InitialScan(CancellationToken ct)
    {
        Log.Info("initial-scan-begin");
        int processed = 0, overwritten = 0;

        IEnumerable<string> roots = _cfg.InitialScanRoots.Where(Directory.Exists);
        foreach (var root in roots)
        {
            foreach (var path in EnumerateXmlSafe(root))
            {
                if (ct.IsCancellationRequested) return;
                processed++;
                try
                {
                    if (TryOverwriteFile(path))
                    {
                        overwritten++;
                    }
                }
                catch (Exception ex) 
                { 
                    Log.Error($"initial-scan-item-error path={path} error={ex.Message}");
                }
            }
        }
        Log.Info($"initial-scan-end processed={processed} overwritten={overwritten}");
    }

    private IEnumerable<string> EnumerateXmlSafe(string root)
    {
        var stack = new Stack<string>();
        stack.Push(root);
        while (stack.Count > 0)
        {
            var dir = stack.Pop();
            string[] subs = Array.Empty<string>();
            try { subs = Directory.GetDirectories(dir); } catch {}
            foreach (var s in subs) stack.Push(s);

            string[] files = Array.Empty<string>();
            try { files = Directory.GetFiles(dir, "*.xml"); } catch {}
            foreach (var f in files) yield return f;
        }
    }
}