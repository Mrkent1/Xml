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
    public string TelegramBotToken { get; set; } = "";
    public string TelegramChatId { get; set; } = "";
}