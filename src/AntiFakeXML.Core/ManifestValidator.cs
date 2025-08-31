using System.Security.Cryptography;
using System.Text.Json;

namespace AntiFakeXML.Core;

public class ManifestEntry
{
    public string mst { get; set; } = "";
    public string maToKhai { get; set; } = "";
    public string ky { get; set; } = "";
    public int soLan { get; set; }
    public string sha256 { get; set; } = "";
    public string relative_path { get; set; } = "";
}

public class Manifest
{
    public int version { get; set; } = 1;
    public string issued_at { get; set; } = "";
    public List<ManifestEntry> entries { get; set; } = new();
}

public static class ManifestValidator
{
    private static readonly object _gate = new();
    private static Dictionary<string, ManifestEntry> _index = new();
    private static string _manifestPath = "";
    private static string _masterFolder = "";
    private static string _projectRoot = "";

    public static void Load(string manifestPath, string masterSyncFolder)
    {
        lock (_gate)
        {
            _manifestPath = manifestPath;
            _masterFolder = masterSyncFolder;
            
            // Sử dụng đường dẫn tuyệt đối của thư mục dự án
            // manifestPath: C:\AntiFakeXML\config\manifest.json
            // Cần tìm: C:\Users\Administrator\Pictures\AntiFakeXML_P1_Project\AntiFakeXML_P1
            var configDir = Path.GetDirectoryName(manifestPath) ?? ""; // C:\AntiFakeXML\config
            var antiFakeDir = Path.GetDirectoryName(configDir) ?? ""; // C:\AntiFakeXML
            var parentDir = Path.GetDirectoryName(antiFakeDir) ?? ""; // C:\
            
            // Tìm thư mục dự án bằng cách tìm thư mục chứa các thư mục công ty
            _projectRoot = FindProjectRootFromParent(parentDir);
            
            Log.Info($"manifest-loaded entries={_index.Count} projectRoot={_projectRoot}");
            
            var txt = File.ReadAllText(manifestPath);
            var mani = JsonSerializer.Deserialize<Manifest>(txt, new JsonSerializerOptions{PropertyNameCaseInsensitive = true}) ?? new Manifest();
            _index = mani.entries.ToDictionary(k => $"{k.mst}|{k.maToKhai}|{k.ky}|{k.soLan}", v => v, StringComparer.OrdinalIgnoreCase);
        }
    }

    private static string FindProjectRootFromParent(string parentDir)
    {
        try
        {
            // Tìm thư mục dự án từ thư mục cha của AntiFakeXML
            // Bắt đầu từ C:\ và tìm xuống dưới
            var searchDirs = new[]
            {
                Path.Combine(parentDir, "Users", "Administrator", "Pictures", "AntiFakeXML_P1_Project", "AntiFakeXML_P1"),
                Path.Combine(parentDir, "Users", "Administrator", "Pictures", "AntiFakeXML_P1_Project"),
                Path.Combine(parentDir, "Users", "Administrator", "Pictures"),
                Path.Combine(parentDir, "Users", "Administrator"),
                Path.Combine(parentDir, "Users"),
                parentDir
            };
            
            foreach (var searchDir in searchDirs)
            {
                Log.Info($"debug-search-dir {searchDir}");
                
                // Kiểm tra xem có phải thư mục dự án không (chứa các thư mục công ty)
                if (Directory.Exists(Path.Combine(searchDir, "cty Bình Nguyễn Derco")) ||
                    Directory.Exists(Path.Combine(searchDir, "Cty Tiến Bình Yến")))
                {
                    Log.Info($"debug-found-project-root {searchDir}");
                    return searchDir;
                }
            }
            
            // Fallback: sử dụng thư mục hiện tại
            var fallbackDir = Environment.CurrentDirectory;
            Log.Warn($"debug-fallback-project-root {fallbackDir}");
            return fallbackDir;
        }
        catch (Exception ex)
        {
            Log.Error($"debug-find-project-root-error {ex.Message}");
            return Environment.CurrentDirectory;
        }
    }

    public static bool TryGetOriginal(XmlKey key, out string originalPath, out ManifestEntry? entry)
    {
        entry = null;
        originalPath = "";
        lock (_gate)
        {
            if (_index.TryGetValue(key.ToString(), out var e))
            {
                entry = e;
                
                // Thử tìm file gốc ở thư mục dự án trước
                var projectPath = Path.Combine(_projectRoot, e.relative_path);
                Log.Info($"debug-try-project-path projectRoot={_projectRoot} relativePath={e.relative_path} fullPath={projectPath} exists={File.Exists(projectPath)}");
                
                if (File.Exists(projectPath))
                {
                    originalPath = projectPath;
                    Log.Info($"debug-found-project-path {originalPath}");
                    return true;
                }
                
                // Nếu không có, thử ở masterFolder
                var masterPath = Path.Combine(_masterFolder, e.relative_path);
                Log.Info($"debug-try-master-path masterFolder={_masterFolder} relativePath={e.relative_path} fullPath={masterPath} exists={File.Exists(masterPath)}");
                
                if (File.Exists(masterPath))
                {
                    originalPath = masterPath;
                    Log.Info($"debug-found-master-path {originalPath}");
                    return true;
                }
                
                Log.Warn($"debug-no-file-found key={key} projectPath={projectPath} masterPath={masterPath}");
            }
            return false;
        }
    }

    public static string Sha256File(string path)
    {
        using var s = File.OpenRead(path);
        using var sha = SHA256.Create();
        var b = sha.ComputeHash(s);
        return Convert.ToHexString(b);
    }
}