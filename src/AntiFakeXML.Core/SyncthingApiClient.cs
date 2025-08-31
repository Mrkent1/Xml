using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Text.Json.Serialization;
using System.Linq;

namespace AntiFakeXML.Core;

public class SyncthingApiClient
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;
    private readonly string _apiKey;
    
    public SyncthingApiClient(string baseUrl = "http://127.0.0.1:8384", string apiKey = "")
    {
        _httpClient = new HttpClient();
        _baseUrl = baseUrl.TrimEnd('/');
        _apiKey = apiKey;
        
        if (!string.IsNullOrEmpty(_apiKey))
        {
            _httpClient.DefaultRequestHeaders.Add("X-API-Key", _apiKey);
        }
    }
    
    public async Task<SyncthingSystemStatus> GetSystemStatusAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/rest/system/status");
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize<SyncthingSystemStatus>(json) ?? new SyncthingSystemStatus();
            }
        }
        catch (Exception ex)
        {
            Log.Error($"syncthing-api-error system-status {ex.Message}");
        }
        
        return new SyncthingSystemStatus();
    }
    
    public async Task<List<SyncthingDevice>> GetDevicesAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/rest/system/connections");
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                var connections = JsonSerializer.Deserialize<SyncthingConnections>(json);
                return connections?.Devices ?? new List<SyncthingDevice>();
            }
        }
        catch (Exception ex)
        {
            Log.Error($"syncthing-api-error devices {ex.Message}");
        }
        
        return new List<SyncthingDevice>();
    }
    
    public async Task<SyncthingFolderStatus> GetFolderStatusAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/rest/system/folders");
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                var folders = JsonSerializer.Deserialize<List<SyncthingFolder>>(json);
                return new SyncthingFolderStatus { Folders = folders ?? new List<SyncthingFolder>() };
            }
        }
        catch (Exception ex)
        {
            Log.Error($"syncthing-api-error folders {ex.Message}");
        }
        
        return new SyncthingFolderStatus();
    }
    
    public void Dispose()
    {
        _httpClient?.Dispose();
    }
}

// Syncthing API Models
public class SyncthingSystemStatus
{
    [JsonPropertyName("version")]
    public string Version { get; set; } = "";
    
    [JsonPropertyName("startTime")]
    public DateTime StartTime { get; set; }
    
    [JsonPropertyName("myID")]
    public string MyId { get; set; } = "";
    
    [JsonPropertyName("goVersion")]
    public string GoVersion { get; set; } = "";
    
    [JsonPropertyName("os")]
    public string Os { get; set; } = "";
    
    [JsonPropertyName("arch")]
    public string Arch { get; set; } = "";
}

public class SyncthingConnections
{
    [JsonPropertyName("connections")]
    public Dictionary<string, SyncthingDevice> Connections { get; set; } = new();
    
    public List<SyncthingDevice> Devices => Connections.Values.ToList();
}

public class SyncthingDevice
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = "";
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";
    
    [JsonPropertyName("addresses")]
    public List<string> Addresses { get; set; } = new();
    
    [JsonPropertyName("compression")]
    public string Compression { get; set; } = "";
    
    [JsonPropertyName("certName")]
    public string CertName { get; set; } = "";
    
    [JsonPropertyName("version")]
    public string Version { get; set; } = "";
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = "";
    
    [JsonPropertyName("connected")]
    public bool Connected { get; set; }
    
    [JsonPropertyName("inBytesTotal")]
    public long InBytesTotal { get; set; }
    
    [JsonPropertyName("outBytesTotal")]
    public long OutBytesTotal { get; set; }
    
    public string GetPrimaryAddress()
    {
        return Addresses.FirstOrDefault() ?? "Không xác định";
    }
    
    public string GetDisplayName()
    {
        return !string.IsNullOrEmpty(Name) ? Name : Id;
    }
}

public class SyncthingFolderStatus
{
    public List<SyncthingFolder> Folders { get; set; } = new();
}

public class SyncthingFolder
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = "";
    
    [JsonPropertyName("label")]
    public string Label { get; set; } = "";
    
    [JsonPropertyName("path")]
    public string Path { get; set; } = "";
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = "";
    
    [JsonPropertyName("devices")]
    public List<SyncthingFolderDevice> Devices { get; set; } = new();
    
    [JsonPropertyName("rescanIntervalS")]
    public int RescanIntervalS { get; set; }
    
    [JsonPropertyName("fsWatcherEnabled")]
    public bool FsWatcherEnabled { get; set; }
    
    [JsonPropertyName("fsWatcherDelayS")]
    public int FsWatcherDelayS { get; set; }
    
    [JsonPropertyName("ignorePerms")]
    public bool IgnorePerms { get; set; }
    
    [JsonPropertyName("autoNormalize")]
    public bool AutoNormalize { get; set; }
}

public class SyncthingFolderDevice
{
    [JsonPropertyName("deviceID")]
    public string DeviceId { get; set; } = "";
    
    [JsonPropertyName("introducedBy")]
    public string IntroducedBy { get; set; } = "";
    
    [JsonPropertyName("encryptionPassword")]
    public string EncryptionPassword { get; set; } = "";
    
    [JsonPropertyName("skipIntroductionRemoval")]
    public bool SkipIntroductionRemoval { get; set; }
}
