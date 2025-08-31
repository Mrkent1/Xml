using AntiFakeXML.Core;
using System.ServiceProcess;
using System.Diagnostics;

namespace BotGuard;

public class BotGuardWorker : BackgroundService
{
    private AppConfig _cfg = new();
    private readonly Dictionary<string, DateTime> _lastRestartTimes = new();
    private readonly Dictionary<string, int> _restartCounts = new();
    private readonly Dictionary<string, DateTime> _lastTelegramAlerts = new();
    private TelegramBot? _telegramBot;
    
    // Anti-spam: chỉ gửi cảnh báo mỗi 5 phút cho cùng một service
    private const int TELEGRAM_ALERT_COOLDOWN_MINUTES = 5;
    // Giới hạn số lần khởi động lại: tối đa 3 lần trong 10 phút
    private const int MAX_RESTARTS_PER_WINDOW = 3;
    private const int RESTART_WINDOW_MINUTES = 10;
    
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        Log.LogDirectory = _cfg.LogDir;
        Directory.CreateDirectory(_cfg.LogDir);
        
        // Load configuration from environment
        _cfg.LoadFromEnvironment();
        
        // Initialize Telegram Bot if configured
        if (!string.IsNullOrEmpty(_cfg.TelegramBotToken))
        {
            _telegramBot = new TelegramBot(_cfg);
            Log.Info("telegram-bot-initialized");
        }
        else
        {
            Log.Info("telegram-bot-not-configured");
        }
        
        Log.Info("botguard-start");
        
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                // 1. Giám sát SyncGuard service (Test case 8)
                EnsureService("SyncGuard", "SyncGuard");
                
                // 2. Giám sát Syncthing process
                EnsureProcess("syncthing", "Syncthing");
                
                // 3. Giám sát BotGuard service (Test case 9 - tự giám sát)
                // Note: BotGuard không thể tự khởi động lại, chỉ log cảnh báo
                CheckBotGuardStatus();
            }
            catch (Exception ex)
            {
                Log.Warn($"botguard-ensure-error {ex.Message}");
            }
            
            await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
        }
    }

    private void EnsureService(string serviceName, string displayName)
    {
        try
        {
            using var sc = new ServiceController(serviceName);
            if (sc.Status != ServiceControllerStatus.Running && sc.Status != ServiceControllerStatus.StartPending)
            {
                var now = DateTime.UtcNow;
                var serviceKey = $"service_{serviceName}";
                
                // Kiểm tra giới hạn khởi động lại
                if (CanRestart(serviceKey, now))
                {
                    Log.Warn($"service-restart {serviceName} status={sc.Status}");
                    
                    try
                    {
                        sc.Start();
                        sc.WaitForStatus(ServiceControllerStatus.Running, TimeSpan.FromSeconds(30));
                        
                        // Ghi nhận khởi động lại thành công
                        RecordRestart(serviceKey, now);
                        
                        // Gửi cảnh báo Telegram (với anti-spam)
                        SendTelegramAlert(serviceKey, $"🔄 {displayName} đã được khởi động lại thành công", "WARN");
                        
                        // Gửi cảnh báo qua Telegram Bot nếu có
                        if (_telegramBot != null)
                        {
                            await _telegramBot.SendAlertAsync($"🔄 {displayName} đã được khởi động lại thành công", "WARN");
                        }
                    }
                    catch (Exception ex)
                    {
                        Log.Error($"service-start-failed {serviceName} error={ex.Message}");
                        SendTelegramAlert(serviceKey, $"❌ Không thể khởi động {displayName}: {ex.Message}", "ERROR");
                        
                        // Gửi cảnh báo qua Telegram Bot nếu có
                        if (_telegramBot != null)
                        {
                            await _telegramBot.SendAlertAsync($"❌ Không thể khởi động {displayName}: {ex.Message}", "ERROR");
                        }
                    }
                }
                else
                {
                    Log.Warn($"service-restart-skipped {serviceName} - đã vượt quá giới hạn khởi động lại");
                    SendTelegramAlert(serviceKey, $"⚠️ {displayName} bị dừng nhưng đã vượt quá giới hạn khởi động lại", "WARN");
                }
            }
        }
        catch (Exception ex)
        {
            Log.Warn($"service-check-fail name={serviceName} err={ex.Message}");
        }
    }

    private void EnsureProcess(string processNameNoExt, string displayName)
    {
        try
        {
            var procs = System.Diagnostics.Process.GetProcessesByName(processNameNoExt);
            if (procs.Length == 0)
            {
                var now = DateTime.UtcNow;
                var processKey = $"process_{processNameNoExt}";
                
                // Kiểm tra giới hạn khởi động lại
                if (CanRestart(processKey, now))
                {
                    Log.Warn($"process-restart {processNameNoExt}");
                    
                    try
                    {
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
                            
                            // Ghi nhận khởi động lại thành công
                            RecordRestart(processKey, now);
                            
                                                    // Gửi cảnh báo Telegram
                        SendTelegramAlert(processKey, $"🔄 {displayName} đã được khởi động lại thành công", "WARN");
                        
                        // Gửi cảnh báo qua Telegram Bot nếu có
                        if (_telegramBot != null)
                        {
                            await _telegramBot.SendAlertAsync($"🔄 {displayName} đã được khởi động lại thành công", "WARN");
                        }
                        }
                        else
                        {
                            Log.Warn($"syncthing-not-found path={synPath}");
                            SendTelegramAlert(processKey, $"⚠️ Không tìm thấy {displayName} tại {synPath}", "WARN");
                        
                        // Gửi cảnh báo qua Telegram Bot nếu có
                        if (_telegramBot != null)
                        {
                            await _telegramBot.SendAlertAsync($"⚠️ Không tìm thấy {displayName} tại {synPath}", "WARN");
                        }
                        }
                    }
                    catch (Exception ex)
                    {
                        Log.Error($"process-start-failed {processNameNoExt} error={ex.Message}");
                        SendTelegramAlert(processKey, $"❌ Không thể khởi động {displayName}: {ex.Message}", "ERROR");
                        
                        // Gửi cảnh báo qua Telegram Bot nếu có
                        if (_telegramBot != null)
                        {
                            await _telegramBot.SendAlertAsync($"❌ Không thể khởi động {displayName}: {ex.Message}", "ERROR");
                        }
                    }
                }
                else
                {
                    Log.Warn($"process-restart-skipped {processNameNoExt} - đã vượt quá giới hạn khởi động lại");
                    SendTelegramAlert(processKey, $"⚠️ {displayName} bị dừng nhưng đã vượt quá giới hạn khởi động lại", "WARN");
                }
            }
        }
        catch (Exception ex)
        {
            Log.Warn($"process-check-fail name={processNameNoExt} err={ex.Message}");
        }
    }

    private void CheckBotGuardStatus()
    {
        try
        {
            // BotGuard tự giám sát trạng thái
            var now = DateTime.UtcNow;
            var botGuardKey = "botguard_self";
            
            // Log heartbeat mỗi 5 phút
            if (!_lastTelegramAlerts.ContainsKey(botGuardKey) || 
                (now - _lastTelegramAlerts[botGuardKey]).TotalMinutes >= 5)
            {
                Log.Info("botguard-heartbeat OK");
                _lastTelegramAlerts[botGuardKey] = now;
            }
        }
        catch (Exception ex)
        {
            Log.Error($"botguard-self-check-error {ex.Message}");
        }
    }

    private bool CanRestart(string key, DateTime now)
    {
        if (!_restartCounts.ContainsKey(key))
        {
            _restartCounts[key] = 0;
            _lastRestartTimes[key] = now;
            return true;
        }

        var timeSinceLastRestart = now - _lastRestartTimes[key];
        
        // Reset counter nếu đã qua window
        if (timeSinceLastRestart.TotalMinutes >= RESTART_WINDOW_MINUTES)
        {
            _restartCounts[key] = 0;
            _lastRestartTimes[key] = now;
            return true;
        }

        // Kiểm tra giới hạn
        return _restartCounts[key] < MAX_RESTARTS_PER_WINDOW;
    }

    private void RecordRestart(string key, DateTime now)
    {
        _restartCounts[key] = _restartCounts.GetValueOrDefault(key, 0) + 1;
        _lastRestartTimes[key] = now;
    }

    private void SendTelegramAlert(string key, string message, string level)
    {
        try
        {
            var now = DateTime.UtcNow;
            
            // Anti-spam: chỉ gửi mỗi 5 phút cho cùng một key
            if (_lastTelegramAlerts.ContainsKey(key))
            {
                var timeSinceLastAlert = now - _lastTelegramAlerts[key];
                if (timeSinceLastAlert.TotalMinutes < TELEGRAM_ALERT_COOLDOWN_MINUTES)
                {
                    Log.Info($"telegram-alert-skipped {key} - anti-spam cooldown");
                    return;
                }
            }

            // Gửi cảnh báo Telegram
            if (!string.IsNullOrEmpty(_cfg.TelegramBotToken) && !string.IsNullOrEmpty(_cfg.TelegramChatId))
            {
                // TODO: Implement Telegram Bot API call
                Log.Info($"telegram-alert {key} level={level} message={message}");
                _lastTelegramAlerts[key] = now;
            }
            else
            {
                Log.Info($"telegram-config-missing token={_cfg.TelegramBotToken} chatId={_cfg.TelegramChatId}");
            }
        }
        catch (Exception ex)
        {
            Log.Error($"telegram-alert-error {ex.Message}");
        }
    }
}