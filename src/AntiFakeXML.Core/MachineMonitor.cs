using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Text.Json;
using System.IO;

namespace AntiFakeXML.Core;

public class MachineMonitor
{
    private readonly IpLocationDetector _ipDetector;
    private readonly SyncthingApiClient _syncthingClient;
    private readonly string _configPath;
    private List<MachineInfo> _machines;
    
    public MachineMonitor(string configPath, AppConfig? appConfig = null)
    {
        _ipDetector = new IpLocationDetector();
        
        if (appConfig != null)
        {
            _syncthingClient = new SyncthingApiClient(appConfig.SyncthingBaseUrl, appConfig.SyncthingApiKey);
        }
        else
        {
            // Fallback về hardcoded values
            _syncthingClient = new SyncthingApiClient("http://127.0.0.1:8384", "NyetNTwfaWTmwgHyu75QK6Ykn34VzejW");
        }
        
        _configPath = configPath;
        _machines = new List<MachineInfo>();
        LoadMachines();
    }
    
    public async Task<List<MachineInfo>> GetActiveMachinesAsync()
    {
        try
        {
            // Gọi Syncthing API để lấy danh sách thiết bị thật
            var syncthingDevices = await _syncthingClient.GetDevicesAsync();
            
            if (syncthingDevices.Any())
            {
                // Chuyển đổi Syncthing devices thành MachineInfo
                var realMachines = new List<MachineInfo>();
                
                foreach (var device in syncthingDevices)
                {
                    var ipAddress = device.GetPrimaryAddress();
                    var region = _ipDetector.DetectRegion(ipAddress);
                    
                    var machine = new MachineInfo
                    {
                        DeviceId = device.Id,
                        IpAddress = ipAddress,
                        Region = region,
                        Status = device.Connected ? "Đang hoạt động" : "Mất kết nối",
                        LastSeen = DateTime.Now,
                        Department = GetDepartmentFromDeviceName(device.GetDisplayName()),
                        Description = $"Máy {device.GetDisplayName()} - {device.Type} - {device.Version}"
                    };
                    
                    realMachines.Add(machine);
                }
                
                _machines = realMachines;
                await SaveMachinesAsync();
                
                Log.Info($"syncthing-devices-found count={realMachines.Count}");
                
                return _machines.Where(m => m.IsActive).ToList();
            }
            else
            {
                // Fallback về mock data nếu không có thiết bị nào
                Log.Warn("syncthing-no-devices-found using-mock-data");
                return await GetMockMachinesAsync();
            }
        }
        catch (Exception ex)
        {
            Log.Error($"syncthing-api-error {ex.Message} using-mock-data");
            return await GetMockMachinesAsync();
        }
    }
    
    private async Task<List<MachineInfo>> GetMockMachinesAsync()
    {
        var mockMachines = new List<MachineInfo>
        {
            new MachineInfo
            {
                DeviceId = "ABC123",
                IpAddress = "112.168.1.100",
                Region = _ipDetector.DetectRegion("112.168.1.100"),
                Status = "Đang hoạt động",
                LastSeen = DateTime.Now.AddMinutes(-2),
                Department = "Kế toán",
                Description = "Máy xử lý XML thuế Hà Nội (Mock Data)"
            },
            new MachineInfo
            {
                DeviceId = "DEF456",
                IpAddress = "116.168.1.100",
                Region = _ipDetector.DetectRegion("116.168.1.100"),
                Status = "Đang hoạt động",
                LastSeen = DateTime.Now.AddMinutes(-1),
                Department = "Kế toán",
                Description = "Máy xử lý XML thuế Quảng Ninh (Mock Data)"
            },
            new MachineInfo
            {
                DeviceId = "GHI789",
                IpAddress = "113.168.1.100",
                Region = _ipDetector.DetectRegion("113.168.1.100"),
                Status = "Đang hoạt động",
                LastSeen = DateTime.Now.AddMinutes(-3),
                Department = "Nhân sự",
                Description = "Máy xử lý XML thuế TP.HCM (Mock Data)"
            }
        };
        
        _machines = mockMachines;
        await SaveMachinesAsync();
        
        return _machines.Where(m => m.IsActive).ToList();
    }
    
    private string GetDepartmentFromDeviceName(string deviceName)
    {
        // Logic đơn giản để xác định phòng ban từ tên thiết bị
        if (deviceName.Contains("ke-toan", StringComparison.OrdinalIgnoreCase) || 
            deviceName.Contains("accounting", StringComparison.OrdinalIgnoreCase))
            return "Kế toán";
        else if (deviceName.Contains("nhan-su", StringComparison.OrdinalIgnoreCase) || 
                 deviceName.Contains("hr", StringComparison.OrdinalIgnoreCase))
            return "Nhân sự";
        else if (deviceName.Contains("kinh-doanh", StringComparison.OrdinalIgnoreCase) || 
                 deviceName.Contains("sales", StringComparison.OrdinalIgnoreCase))
            return "Kinh doanh";
        else
            return "Chung";
    }
    
    public async Task<MachineInfo?> AddMachineAsync(string deviceId, string ipAddress, string department = "", string description = "")
    {
        var region = _ipDetector.DetectRegion(ipAddress);
        
        var machine = new MachineInfo
        {
            DeviceId = deviceId,
            IpAddress = ipAddress,
            Region = region,
            Status = "Đang hoạt động",
            LastSeen = DateTime.Now,
            Department = department,
            Description = description
        };
        
        // Kiểm tra xem máy đã tồn tại chưa
        var existingMachine = _machines.FirstOrDefault(m => m.DeviceId == deviceId);
        if (existingMachine != null)
        {
            // Cập nhật thông tin máy cũ
            existingMachine.IpAddress = ipAddress;
            existingMachine.Region = region;
            existingMachine.Status = "Đang hoạt động";
            existingMachine.LastSeen = DateTime.Now;
            existingMachine.Department = department;
            existingMachine.Description = description;
            
            await SaveMachinesAsync();
            return existingMachine;
        }
        else
        {
            // Thêm máy mới
            _machines.Add(machine);
            await SaveMachinesAsync();
            
            // Ghi log máy mới
            Log.Info($"machine-connected deviceId={deviceId} ip={ipAddress} region={region}");
            
            return machine;
        }
    }
    
    public async Task UpdateMachineStatusAsync(string deviceId, string status)
    {
        var machine = _machines.FirstOrDefault(m => m.DeviceId == deviceId);
        if (machine != null)
        {
            machine.Status = status;
            machine.LastSeen = DateTime.Now;
            await SaveMachinesAsync();
            
            Log.Info($"machine-status-updated deviceId={deviceId} status={status}");
        }
    }
    
    public async Task<string> GetRegionalReportAsync()
    {
        var activeMachines = await GetActiveMachinesAsync();
        
        if (!activeMachines.Any())
        {
            return "❌ **KHÔNG CÓ MÁY NÀO ĐANG HOẠT ĐỘNG**\n\n" +
                   "💡 Kiểm tra kết nối Syncthing và cấu hình máy con.";
        }
        
        var report = "🌍 **BÁO CÁO MÁY CON THEO VÙNG MIỀN**\n\n";
        
        // Nhóm máy theo vùng miền
        var regionalMachines = activeMachines
            .GroupBy(m => m.Region)
            .OrderBy(g => g.Key)
            .ToList();
        
        var totalMachines = activeMachines.Count;
        report += $"📊 **Tổng cộng: {totalMachines} máy đang hoạt động**\n\n";
        
        foreach (var region in regionalMachines)
        {
            var regionEmoji = GetRegionEmoji(region.Key);
            var machineCount = region.Count();
            
            report += $"{regionEmoji} **{region.Key} ({machineCount} máy):**\n";
            
            foreach (var machine in region.OrderBy(m => m.IpAddress))
            {
                var statusEmoji = machine.GetStatusEmoji();
                var timeAgo = GetTimeAgo(machine.LastSeen);
                
                report += $"  {statusEmoji} **{machine.IpAddress}**";
                
                if (!string.IsNullOrEmpty(machine.Department))
                {
                    report += $" - {machine.Department}";
                }
                
                report += $"\n     └─ Kết nối: {timeAgo}\n";
                
                if (!string.IsNullOrEmpty(machine.Description))
                {
                    report += $"     └─ Mô tả: {machine.Description}\n";
                }
                
                report += "\n";
            }
        }
        
        // Thống kê theo vùng
        report += "📈 **THỐNG KÊ THEO VÙNG:**\n";
        foreach (var region in regionalMachines)
        {
            var percentage = (double)region.Count() / totalMachines * 100;
            report += $"• {region.Key}: {region.Count()} máy ({percentage:F1}%)\n";
        }
        
        return report;
    }
    
    public async Task<string> GetMachineDetailsAsync(string deviceId)
    {
        var machine = _machines.FirstOrDefault(m => m.DeviceId == deviceId);
        if (machine == null)
        {
            return $"❌ **KHÔNG TÌM THẤY MÁY**\n\nDevice ID: `{deviceId}`";
        }
        
        var report = $"💻 **CHI TIẾT MÁY**\n\n";
        report += $"🆔 **Device ID:** `{machine.DeviceId}`\n";
        report += $"🌐 **IP Address:** `{machine.IpAddress}`\n";
        report += $"🏛️ **Vùng miền:** {machine.GetRegionEmoji()} {machine.Region}\n";
        report += $"📊 **Trạng thái:** {machine.GetStatusEmoji()} {machine.Status}\n";
        report += $"⏰ **Lần cuối:** {machine.LastSeen:dd/MM/yyyy HH:mm:ss}\n";
        
        if (!string.IsNullOrEmpty(machine.Department))
        {
            report += $"🏢 **Phòng ban:** {machine.Department}\n";
        }
        
        if (!string.IsNullOrEmpty(machine.Description))
        {
            report += $"📝 **Mô tả:** {machine.Description}\n";
        }
        
        var regionDesc = _ipDetector.GetRegionDescription(machine.Region);
        report += $"\n🌍 **Thông tin vùng:** {regionDesc}";
        
        return report;
    }
    
    private string GetTimeAgo(DateTime lastSeen)
    {
        var timeSpan = DateTime.Now - lastSeen;
        
        if (timeSpan.TotalMinutes < 1)
            return "Vừa xong";
        else if (timeSpan.TotalMinutes < 60)
            return $"{(int)timeSpan.TotalMinutes} phút trước";
        else if (timeSpan.TotalHours < 24)
            return $"{(int)timeSpan.TotalHours} giờ trước";
        else
            return $"{(int)timeSpan.TotalDays} ngày trước";
    }
    
    private string GetRegionEmoji(string region)
    {
        return region switch
        {
            "Hà Nội" => "🏛️",
            "TP.HCM" => "🏙️",
            "Đà Nẵng" => "🏖️",
            "Cần Thơ" => "🌾",
            "Quảng Ninh" => "⛰️",
            "Thanh Hóa" => "🏔️",
            "Nghệ An" => "🌊",
            "Hải Phòng" => "🚢",
            _ => "🌍"
        };
    }
    
    private void LoadMachines()
    {
        try
        {
            if (File.Exists(_configPath))
            {
                var json = File.ReadAllText(_configPath);
                _machines = JsonSerializer.Deserialize<List<MachineInfo>>(json) ?? new List<MachineInfo>();
            }
        }
        catch (Exception ex)
        {
            Log.Error($"machine-load-error {ex.Message}");
            _machines = new List<MachineInfo>();
        }
    }
    
    private async Task SaveMachinesAsync()
    {
        try
        {
            var json = JsonSerializer.Serialize(_machines, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(_configPath, json);
        }
        catch (Exception ex)
        {
            Log.Error($"machine-save-error {ex.Message}");
        }
    }
}
