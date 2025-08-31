namespace AntiFakeXML.Core;

public class AppConfig
{
    public string MasterSyncFolder { get; set; } = @"C:\AntiFakeXML\SyncFolder";
    public string ManifestPath { get; set; } = @"C:\AntiFakeXML\config\manifest.json";
    public string LogDir { get; set; } = @"C:\AntiFakeXML\logs";
    public bool InitialFullScan { get; set; } = true;
    public string[] InitialScanRoots { get; set; } = new[]
    {
        Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
        Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
        @"C:\AntiFakeXML",
        Environment.CurrentDirectory  // Thêm thư mục dự án hiện tại
    };
    
    // Telegram Bot Configuration
    public string TelegramBotToken { get; set; } = "";
    public string TelegramChatId { get; set; } = "";
    public string[] AdminIds { get; set; } = new string[0];
    
    // Syncthing Configuration
    public string SyncthingPath { get; set; } = @"C:\AntiFakeXML\syncthing\syncthing.exe";
    public string SyncthingConfigPath { get; set; } = @"C:\AntiFakeXML\syncthing\config";
    public int SyncthingWebGUIPort { get; set; } = 8384;
    public string SyncthingWebGUIUser { get; set; } = "admin";
    public string SyncthingWebGUIPassword { get; set; } = "admin123";
    
    // Load configuration from environment variables
    public void LoadFromEnvironment()
    {
        TelegramBotToken = Environment.GetEnvironmentVariable("TELEGRAM_TOKEN") ?? "";
        TelegramChatId = Environment.GetEnvironmentVariable("TELEGRAM_GROUP_ID") ?? "";
        var adminIdsStr = Environment.GetEnvironmentVariable("ADMIN_IDS") ?? "";
        AdminIds = adminIdsStr.Split(',', StringSplitOptions.RemoveEmptyEntries);
    }
}