using System.Diagnostics;
using System.Windows.Forms;
using AntiFakeXML.Core;

namespace XmlProxy;

static class Program
{
    [STAThread]
    static void Main(string[] args)
    {
        Application.SetHighDpiMode(HighDpiMode.SystemAware);
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        var cfg = new AppConfig();
        Log.LogDirectory = cfg.LogDir;

        if (args.Length == 0)
        {
            MessageBox.Show("Không có tệp XML.", "XmlProxy");
            return;
        }

        var target = args[0];
        try
        {
            ManifestValidator.Load(cfg.ManifestPath, cfg.MasterSyncFolder);

            if (!XmlFieldsExtractor.TryExtractKey(target, out var key, out var err))
            {
                Log.Warn($"proxy-open denied key-extract-fail path={target} err={err}");
                MessageBox.Show("Từ chối mở: thiếu trường định danh.", "XmlProxy");
                return;
            }

            if (!ManifestValidator.TryGetOriginal(key, out var original, out var entry))
            {
                Log.Warn($"proxy-open denied not-in-manifest key={key} path={target}");
                MessageBox.Show("Từ chối mở: không khớp danh mục gốc.", "XmlProxy");
                return;
            }

            // Optional: verify hash match with manifest to be safe
            var sha = ManifestValidator.Sha256File(original);
            if (!string.Equals(sha, entry!.sha256, StringComparison.OrdinalIgnoreCase))
            {
                Log.Error($"proxy-open denied hash-mismatch key={key} orig={original}");
                MessageBox.Show("Từ chối mở: bản gốc không đúng hash.", "XmlProxy");
                return;
            }

            // Open the ORIGINAL file for viewing
            Log.Info($"proxy-open OK key={key} orig={original}");
            var psi = new ProcessStartInfo
            {
                FileName = original,
                UseShellExecute = true
            };
            Process.Start(psi);
        }
        catch (Exception ex)
        {
            Log.Error($"proxy-open exception path={target} ex={ex}");
            MessageBox.Show("Lỗi hệ thống khi kiểm tra tệp.", "XmlProxy");
        }
    }
}