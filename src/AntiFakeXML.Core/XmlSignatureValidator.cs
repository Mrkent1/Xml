using System.Security.Cryptography;
using System.Text;
using System.Xml;

namespace AntiFakeXML.Core;

public static class XmlSignatureValidator
{
    public static ValidationResult ValidateSignature(string xmlPath)
    {
        try
        {
            var doc = new XmlDocument();
            doc.PreserveWhitespace = true;
            doc.Load(xmlPath);

            // Kiểm tra có chữ ký số không
            var signatureNodes = doc.SelectNodes("//ds:Signature", GetNamespaceManager(doc));
            if (signatureNodes?.Count == 0)
            {
                return new ValidationResult(false, "missing-signature", "Không tìm thấy chữ ký số");
            }

            // Kiểm tra cấu trúc chữ ký cơ bản
            foreach (XmlNode signatureNode in signatureNodes!)
            {
                var result = ValidateBasicSignature(doc, signatureNode);
                if (!result.IsValid)
                {
                    return result;
                }
            }

            return new ValidationResult(true, "valid", "Chữ ký số hợp lệ");
        }
        catch (Exception ex)
        {
            return new ValidationResult(false, "validation-error", $"Lỗi kiểm tra chữ ký: {ex.Message}");
        }
    }

    private static ValidationResult ValidateBasicSignature(XmlDocument doc, XmlNode signatureNode)
    {
        try
        {
            // Kiểm tra cấu trúc chữ ký cơ bản
            var signedInfo = signatureNode.SelectSingleNode("ds:SignedInfo", GetNamespaceManager(doc));
            var signatureValue = signatureNode.SelectSingleNode("ds:SignatureValue", GetNamespaceManager(doc));
            var keyInfo = signatureNode.SelectSingleNode("ds:KeyInfo", GetNamespaceManager(doc));

            if (signedInfo == null)
            {
                return new ValidationResult(false, "missing-signedinfo", "Thiếu thông tin SignedInfo");
            }

            if (signatureValue == null)
            {
                return new ValidationResult(false, "missing-signaturevalue", "Thiếu giá trị chữ ký");
            }

            if (keyInfo == null)
            {
                return new ValidationResult(false, "missing-keyinfo", "Thiếu thông tin khóa");
            }

            // Kiểm tra MST trong certificate có khớp với XML không
            var mstFromXml = ExtractMSTFromXml(doc);
            var mstFromCert = ExtractMSTFromCertificate(keyInfo);
            
            if (!string.IsNullOrEmpty(mstFromXml) && !string.IsNullOrEmpty(mstFromCert))
            {
                if (!mstFromXml.Equals(mstFromCert, StringComparison.OrdinalIgnoreCase))
                {
                    return new ValidationResult(false, "mst-mismatch", $"MST trong certificate ({mstFromCert}) không khớp với MST trong XML ({mstFromXml})");
                }
            }

            return new ValidationResult(true, "valid", "Chữ ký số hợp lệ");
        }
        catch (Exception ex)
        {
            return new ValidationResult(false, "signature-validation-error", $"Lỗi kiểm tra chữ ký: {ex.Message}");
        }
    }

    private static string? ExtractMSTFromXml(XmlDocument doc)
    {
        try
        {
            var mstNode = doc.SelectSingleNode("//NNT/mst", GetNamespaceManager(doc));
            return mstNode?.InnerText?.Trim();
        }
        catch
        {
            return null;
        }
    }

    private static string? ExtractMSTFromCertificate(XmlNode keyInfo)
    {
        try
        {
            // Tìm X509SubjectName trong KeyInfo
            var subjectNameNode = keyInfo.SelectSingleNode(".//ds:X509SubjectName", GetNamespaceManager(keyInfo.OwnerDocument!));
            if (subjectNameNode != null)
            {
                var subject = subjectNameNode.InnerText;
                // Tìm MST trong subject: UID=MST:5702126556
                var mstMatch = System.Text.RegularExpressions.Regex.Match(subject, @"UID=MST:(\d+)");
                if (mstMatch.Success)
                {
                    return mstMatch.Groups[1].Value;
                }
            }
            return null;
        }
        catch
        {
            return null;
        }
    }

    private static XmlNamespaceManager GetNamespaceManager(XmlDocument doc)
    {
        var nsManager = new XmlNamespaceManager(doc.NameTable);
        nsManager.AddNamespace("ds", "http://www.w3.org/2000/09/xmldsig#");
        return nsManager;
    }

    public static string CalculateContentHash(string xmlPath)
    {
        try
        {
            var doc = new XmlDocument();
            doc.PreserveWhitespace = true;
            doc.Load(xmlPath);

            // Loại bỏ tất cả chữ ký số trước khi tính hash
            var signatureNodes = doc.SelectNodes("//ds:Signature", GetNamespaceManager(doc));
            if (signatureNodes != null)
            {
                foreach (XmlNode sigNode in signatureNodes)
                {
                    sigNode.ParentNode?.RemoveChild(sigNode);
                }
            }

            // Tính SHA256 hash
            using var sha256 = SHA256.Create();
            var xmlBytes = Encoding.UTF8.GetBytes(doc.OuterXml);
            var hashBytes = sha256.ComputeHash(xmlBytes);
            return Convert.ToBase64String(hashBytes);
        }
        catch (Exception ex)
        {
            Log.Error($"hash-calculation-error path={xmlPath} error={ex.Message}");
            return "";
        }
    }
}

public record ValidationResult(bool IsValid, string Code, string Message);
