using System.Text.Json;
using System.ServiceProcess;
using System.Diagnostics;

namespace AntiFakeXML.Core;

public class TelegramBot
{
    private readonly AppConfig _config;
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;
    
    public TelegramBot(AppConfig config)
    {
        _config = config;
        _httpClient = new HttpClient();
        _baseUrl = $"https://api.telegram.org/bot{_config.TelegramBotToken}";
    }
    
    public async Task SendMessageAsync(string chatId, string message, string? parseMode = null)
    {
        if (string.IsNullOrEmpty(_config.TelegramBotToken))
        {
            Log.Warn("telegram-bot-token-missing");
            return;
        }
        
        try
        {
            var data = new
            {
                chat_id = chatId,
                text = message,
                parse_mode = parseMode ?? "HTML"
            };
            
            var json = JsonSerializer.Serialize(data);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
            
            var response = await _httpClient.PostAsync($"{_baseUrl}/sendMessage", content);
            if (response.IsSuccessStatusCode)
            {
                Log.Info($"telegram-message-sent chatId={chatId}");
            }
            else
            {
                Log.Warn($"telegram-message-failed status={response.StatusCode}");
            }
        }
        catch (Exception ex)
        {
            Log.Error($"telegram-send-error {ex.Message}");
        }
    }
    
    public async Task SendAlertAsync(string message, string level = "INFO")
    {
        if (!string.IsNullOrEmpty(_config.TelegramChatId))
        {
            var formattedMessage = $"[{level}] {message}";
            await SendMessageAsync(_config.TelegramChatId, formattedMessage);
        }
    }
    
    public Task<bool> IsAuthorizedUserAsync(string userId)
    {
        return Task.FromResult(_config.AdminIds.Contains(userId));
    }
    
    public async Task<string> ProcessCommandAsync(string userId, string command, string[] args)
    {
        if (!await IsAuthorizedUserAsync(userId))
        {
            return "❌ Bạn không có quyền thực hiện lệnh này.";
        }
        
        return command.ToLower() switch
        {
            "status" => await GetStatusAsync(),
            "restart sync" => await RestartSyncthingAsync(),
            "logs" => await GetRecentLogsAsync(),
            "help" => GetHelpText(),
            _ => $"❌ Lệnh không hợp lệ: {command}. Gõ 'help' để xem danh sách lệnh."
        };
    }
    
    private Task<string> GetStatusAsync()
    {
        try
        {
            var services = new List<string>();
            
            // Kiểm tra SyncGuard service
            try
            {
                using var sc = new ServiceController("SyncGuard");
                services.Add($"🔄 SyncGuard: {sc.Status}");
            }
            catch
            {
                services.Add("❌ SyncGuard: Không tìm thấy");
            }
            
            // Kiểm tra BotGuard service
            try
            {
                using var sc = new ServiceController("BotGuard");
                services.Add($"🔄 BotGuard: {sc.Status}");
            }
            catch
            {
                services.Add("❌ BotGuard: Không tìm thấy");
            }
            
            // Kiểm tra Syncthing process
            var syncthingProcs = Process.GetProcessesByName("syncthing");
            if (syncthingProcs.Length > 0)
            {
                services.Add($"🔄 Syncthing: Đang chạy ({syncthingProcs.Length} process)");
            }
            else
            {
                services.Add("❌ Syncthing: Không chạy");
            }
            
            var statusText = string.Join("\n", services);
            return Task.FromResult($"📊 **TRẠNG THÁI HỆ THỐNG**\n\n{statusText}");
        }
        catch (Exception ex)
        {
            return Task.FromResult($"❌ Lỗi khi lấy trạng thái: {ex.Message}");
        }
    }
    
    private Task<string> RestartSyncthingAsync()
    {
        try
        {
            // Tắt Syncthing hiện tại
            var procs = Process.GetProcessesByName("syncthing");
            foreach (var proc in procs)
            {
                proc.Kill();
            }
            
            // Khởi động lại
            var psi = new ProcessStartInfo
            {
                FileName = _config.SyncthingPath,
                Arguments = $"--no-browser --home={_config.SyncthingConfigPath}",
                UseShellExecute = true,
                WorkingDirectory = Path.GetDirectoryName(_config.SyncthingPath)
            };
            
            Process.Start(psi);
            
            return Task.FromResult("✅ Syncthing đã được khởi động lại thành công.");
        }
        catch (Exception ex)
        {
            return Task.FromResult($"❌ Lỗi khi khởi động lại Syncthing: {ex.Message}");
        }
    }
    
    private Task<string> GetRecentLogsAsync()
    {
        try
        {
            var logFile = Path.Combine(_config.LogDir, $"{DateTime.Now:yyyyMMdd}.log");
            if (File.Exists(logFile))
            {
                var lines = File.ReadAllLines(logFile);
                var recentLines = lines.TakeLast(10).ToArray();
                var logText = string.Join("\n", recentLines);
                return Task.FromResult($"📝 **LOG GẦN NHẤT**\n\n```\n{logText}\n```");
            }
            else
            {
                return Task.FromResult("❌ Không tìm thấy file log.");
            }
        }
        catch (Exception ex)
        {
            return Task.FromResult($"❌ Lỗi khi đọc log: {ex.Message}");
        }
    }
    
    private string GetHelpText()
    {
        return @"📚 **DANH SÁCH LỆNH**

• `status` - Xem trạng thái các service
• `restart sync` - Khởi động lại Syncthing
• `logs` - Xem log gần nhất
• `help` - Hiển thị danh sách lệnh

💡 **Lưu ý**: Chỉ admin mới có quyền thực hiện các lệnh này.";
    }
}
