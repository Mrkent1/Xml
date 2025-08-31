using System;

namespace AntiFakeXML.Core;

public class MachineInfo
{
    public string DeviceId { get; set; } = "";
    public string IpAddress { get; set; } = "";
    public string Region { get; set; } = "";
    public string Status { get; set; } = "Không xác định";
    public DateTime LastSeen { get; set; }
    public string Department { get; set; } = "";
    public string Description { get; set; } = "";
    
    public bool IsActive => (DateTime.Now - LastSeen).TotalMinutes < 5;
    
    public string GetStatusEmoji()
    {
        return Status switch
        {
            "Đang hoạt động" => "🟢",
            "Không xác định" => "🟡", 
            "Mất kết nối" => "🔴",
            _ => "⚪"
        };
    }
    
    public string GetRegionEmoji()
    {
        return Region switch
        {
            "Hà Nội" => "🏛️",
            "TP.HCM" => "🏙️",
            "Đà Nẵng" => "🏖️",
            "Cần Thơ" => "🌾",
            "Quảng Ninh" => "⛰️",
            "Thanh Hóa" => "🏔️",
            _ => "🌍"
        };
    }
}
