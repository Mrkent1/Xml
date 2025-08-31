using System.Xml;
using System.Xml.XPath;

namespace AntiFakeXML.Core;

public record XmlKey(string MST, string MaToKhai, string Ky, int SoLan)
{
    public override string ToString() => $"{MST}|{MaToKhai}|{Ky}|{SoLan}";
}

public static class XmlFieldsExtractor
{
    // Try to extract required fields using multiple XPath candidates to tolerate schema variance
    public static bool TryExtractKey(string xmlPath, out XmlKey key, out string error)
    {
        key = new XmlKey("", "", "", 0);
        error = "";
        try
        {
            var doc = new XmlDocument();
            doc.PreserveWhitespace = true;
            doc.Load(xmlPath);

            var nav = doc.CreateNavigator();

            string? mst = FirstValue(nav,
                "//NNT/mst",
                "//mst",
                "//*[local-name()='NNT']/*[local-name()='mst']",
                "//*[local-name()='MST']");

            string? ma = FirstValue(nav,
                "//TKhaiThue/maTKhai",
                "//maTKhai",
                "//*[local-name()='TKhaiThue']/*[local-name()='maTKhai']");

            string? ky = FirstValue(nav,
                "//KyKKhaiThue/kyKKhai",
                "//kyKKhai",
                "//*[local-name()='KyKKhaiThue']/*[local-name()='kyKKhai']");

            string? solanStr = FirstValue(nav,
                "//TKhaiThue/soLan",
                "//soLan",
                "//*[local-name()='TKhaiThue']/*[local-name()='soLan']");

            if (string.IsNullOrWhiteSpace(mst) || string.IsNullOrWhiteSpace(ma) || string.IsNullOrWhiteSpace(ky) || string.IsNullOrWhiteSpace(solanStr))
            {
                error = "missing-required-fields";
                return false;
            }
            if (!int.TryParse(solanStr, out var soLan))
            {
                error = "invalid-soLan";
                return false;
            }

            key = new XmlKey(mst.Trim(), ma.Trim(), ky.Trim(), soLan);
            return true;
        }
        catch (Exception ex)
        {
            error = ex.Message;
            return false;
        }
    }

    private static string? FirstValue(XPathNavigator nav, params string[] xpaths)
    {
        foreach (var xp in xpaths)
        {
            var it = nav.Select(xp);
            if (it.MoveNext())
            {
                var s = it.Current?.Value?.Trim();
                if (!string.IsNullOrEmpty(s))
                    return s;
            }
        }
        return null;
    }
}