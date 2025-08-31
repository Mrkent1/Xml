using AntiFakeXML.Core;
using System.ServiceProcess;

namespace BotGuard;

public class BotGuardWorker : BackgroundService
{
    private AppConfig _cfg = new();
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        Log.LogDirectory = _cfg.LogDir;
        Log.Info("botguard-start");
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                EnsureService("SyncGuard");
                EnsureProcess("syncthing");
            }
            catch (Exception ex)
            {
                Log.Warn($"botguard-ensure-error {ex.Message}");
            }
            await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
        }
    }

    private void EnsureService(string serviceName)
    {
        try
        {
            using var sc = new ServiceController(serviceName);
            if (sc.Status != ServiceControllerStatus.Running && sc.Status != ServiceControllerStatus.StartPending)
            {
                Log.Warn($"service-restart {serviceName}");
                sc.Start();
            }
        }
        catch (Exception ex)
        {
            Log.Warn($"service-check-fail name={serviceName} err={ex.Message}");
        }
    }

    private void EnsureProcess(string processNameNoExt)
    {
        try
        {
            var procs = System.Diagnostics.Process.GetProcessesByName(processNameNoExt);
            if (procs.Length == 0)
            {
                Log.Warn($"process-restart {processNameNoExt}");
                // Try to start syncthing if we know its location
                var synPath = @"C:\AntiFakeXML\syncthing\syncthing.exe";
                if (File.Exists(synPath))
                {
                    var psi = new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = synPath,
                        UseShellExecute = true,
                        WorkingDirectory = Path.GetDirectoryName(synPath) ?? @"C:\AntiFakeXML\syncthing"
                    };
                    System.Diagnostics.Process.Start(psi);
                }
            }
        }
        catch (Exception ex)
        {
            Log.Warn($"process-check-fail name={processNameNoExt} err={ex.Message}");
        }
    }
}