using System.IO;

namespace AntiFakeXML.Core;

public static class Log
{
    private static readonly object _gate = new();
    public static string LogDirectory { get; set; } = @"C:\AntiFakeXML\logs";

    public static void Info(string message) => Write("INFO", message);
    public static void Warn(string message) => Write("WARN", message);
    public static void Error(string message) => Write("ERROR", message);

    private static void Write(string level, string message)
    {
        try
        {
            lock (_gate)
            {
                Directory.CreateDirectory(LogDirectory);
                var path = Path.Combine(LogDirectory, $"{DateTime.UtcNow:yyyyMMdd}.log");
                File.AppendAllText(path, $"{DateTime.UtcNow:O} [{level}] {message}{Environment.NewLine}");
            }
        }
        catch { /* avoid throwing from logger */ }
    }
}