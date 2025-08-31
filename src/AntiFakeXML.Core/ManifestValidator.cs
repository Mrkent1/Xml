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

    public static ValidationResult ValidateXmlFile(string xmlPath)
    {
        try
        {
            // 1. Kiểm tra chữ ký số
            var signatureResult = XmlSignatureValidator.ValidateSignature(xmlPath);
            if (!signatureResult.IsValid)
            {
                return signatureResult;
            }

            // 2. Trích xuất key từ XML
            if (!XmlFieldsExtractor.TryExtractKey(xmlPath, out var key, out var error))
            {
                return new ValidationResult(false, "extract-failed", $"Không thể trích xuất thông tin: {error}");
            }

            // 3. Kiểm tra key có trong manifest không
            if (!_index.ContainsKey(key.ToString()))
            {
                return new ValidationResult(false, "key-not-found", $"Không tìm thấy thông tin trong manifest: {key}");
            }

            // 4. Kiểm tra hash nội dung (nếu có trong manifest)
            var entry = _index[key.ToString()];
            if (!string.IsNullOrEmpty(entry.sha256))
            {
                var currentHash = XmlSignatureValidator.CalculateContentHash(xmlPath);
                if (!string.IsNullOrEmpty(currentHash) && !currentHash.Equals(entry.sha256, StringComparison.OrdinalIgnoreCase))
                {
                    return new ValidationResult(false, "content-hash-mismatch", "Hash nội dung không khớp với manifest");
                }
            }

            // 5. Kiểm tra nội dung XML có khớp với manifest không
            var contentValidationResult = ValidateXmlContent(xmlPath, entry);
            if (!contentValidationResult.IsValid)
            {
                return contentValidationResult;
            }

            // 6. Kiểm tra file có phải là file gốc không (so sánh với file gốc trong manifest)
            var originalValidationResult = ValidateAgainstOriginalFile(xmlPath, entry);
            if (!originalValidationResult.IsValid)
            {
                return originalValidationResult;
            }

            return new ValidationResult(true, "valid", "File XML hợp lệ");
        }
        catch (Exception ex)
        {
            return new ValidationResult(false, "validation-error", $"Lỗi kiểm tra: {ex.Message}");
        }
    }

    /// <summary>
    /// Kiểm tra nội dung XML có khớp với manifest không
    /// </summary>
    private static ValidationResult ValidateXmlContent(string xmlPath, ManifestEntry entry)
    {
        try
        {
            // Trích xuất key từ XML để so sánh
            if (!XmlFieldsExtractor.TryExtractKey(xmlPath, out var xmlKey, out var error))
            {
                return new ValidationResult(false, "content-extract-failed", $"Không thể trích xuất nội dung: {error}");
            }

            // Kiểm tra MST
            if (!string.IsNullOrEmpty(entry.mst) && !xmlKey.MST.Equals(entry.mst, StringComparison.OrdinalIgnoreCase))
            {
                return new ValidationResult(false, "mst-mismatch", $"MST trong XML ({xmlKey.MST}) không khớp với manifest ({entry.mst})");
            }

            // Kiểm tra mã tờ khai
            if (!string.IsNullOrEmpty(entry.maToKhai) && !xmlKey.MaToKhai.Equals(entry.maToKhai, StringComparison.OrdinalIgnoreCase))
            {
                return new ValidationResult(false, "matokhai-mismatch", $"Mã tờ khai trong XML ({xmlKey.MaToKhai}) không khớp với manifest ({entry.maToKhai})");
            }

            // Kiểm tra kỳ kê khai
            if (!string.IsNullOrEmpty(entry.ky) && !xmlKey.Ky.Equals(entry.ky, StringComparison.OrdinalIgnoreCase))
            {
                return new ValidationResult(false, "ky-mismatch", $"Kỳ kê khai trong XML ({xmlKey.Ky}) không khớp với manifest ({entry.ky})");
            }

            // Kiểm tra số lần
            if (xmlKey.SoLan != entry.soLan)
            {
                return new ValidationResult(false, "solan-mismatch", $"Số lần trong XML ({xmlKey.SoLan}) không khớp với manifest ({entry.soLan})");
            }

            // Kiểm tra hash nội dung chi tiết
            var contentHash = XmlSignatureValidator.CalculateContentHash(xmlPath);
            if (!string.IsNullOrEmpty(entry.sha256) && !string.IsNullOrEmpty(contentHash))
            {
                if (!contentHash.Equals(entry.sha256, StringComparison.OrdinalIgnoreCase))
                {
                    return new ValidationResult(false, "content-hash-mismatch", "Hash nội dung XML không khớp với manifest");
                }
            }

            return new ValidationResult(true, "content-valid", "Nội dung XML khớp với manifest");
        }
        catch (Exception ex)
        {
            return new ValidationResult(false, "content-validation-error", $"Lỗi kiểm tra nội dung: {ex.Message}");
        }
    }

    /// <summary>
    /// Kiểm tra file có phải là file gốc không (so sánh với file gốc trong manifest)
    /// </summary>
    private static ValidationResult ValidateAgainstOriginalFile(string xmlPath, ManifestEntry entry)
    {
        try
        {
            // Tìm file gốc từ manifest
            string? originalPath = null;
            
            // Thử tìm ở thư mục dự án trước
            var projectPath = Path.Combine(_projectRoot, entry.relative_path);
            if (File.Exists(projectPath))
            {
                originalPath = projectPath;
            }
            else
            {
                // Nếu không có, thử ở masterFolder
                var masterPath = Path.Combine(_masterFolder, entry.relative_path);
                if (File.Exists(masterPath))
                {
                    originalPath = masterPath;
                }
            }

            if (string.IsNullOrEmpty(originalPath))
            {
                // Không tìm thấy file gốc, nhưng vẫn cho phép (có thể file gốc chưa được đồng bộ)
                Log.Warn($"original-file-not-found entry={entry.relative_path}");
                return new ValidationResult(true, "original-not-found", "Không tìm thấy file gốc để so sánh");
            }

            // So sánh hash nội dung
            var xmlHash = XmlSignatureValidator.CalculateContentHash(xmlPath);
            var originalHash = XmlSignatureValidator.CalculateContentHash(originalPath);

            if (string.IsNullOrEmpty(xmlHash) || string.IsNullOrEmpty(originalHash))
            {
                Log.Warn($"hash-calculation-failed xmlPath={xmlPath} originalPath={originalPath}");
                return new ValidationResult(true, "hash-calculation-failed", "Không thể tính hash để so sánh");
            }

            if (!xmlHash.Equals(originalHash, StringComparison.OrdinalIgnoreCase))
            {
                Log.Warn($"content-differs-from-original xmlPath={xmlPath} originalPath={originalPath}");
                return new ValidationResult(false, "content-differs-from-original", "Nội dung file khác với file gốc - có thể là file fake");
            }

            return new ValidationResult(true, "matches-original", "File khớp với file gốc");
        }
        catch (Exception ex)
        {
            Log.Error($"original-comparison-error xmlPath={xmlPath} error={ex.Message}");
            return new ValidationResult(false, "original-comparison-error", $"Lỗi so sánh với file gốc: {ex.Message}");
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