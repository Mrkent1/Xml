using System.Text.Json.Serialization;

namespace AntiFakeXML.Core;

// Telegram Bot API Models
public class TelegramApiResponse
{
    [JsonPropertyName("ok")]
    public bool Ok { get; set; }
    
    [JsonPropertyName("result")]
    public List<TelegramUpdate>? Result { get; set; }
}

public class TelegramUpdate
{
    [JsonPropertyName("update_id")]
    public long UpdateId { get; set; }
    
    [JsonPropertyName("message")]
    public TelegramMessage? Message { get; set; }
}

public class TelegramMessage
{
    [JsonPropertyName("message_id")]
    public long MessageId { get; set; }
    
    [JsonPropertyName("from")]
    public TelegramUser? From { get; set; }
    
    [JsonPropertyName("chat")]
    public TelegramChat? Chat { get; set; }
    
    [JsonPropertyName("date")]
    public long Date { get; set; }
    
    [JsonPropertyName("text")]
    public string? Text { get; set; }
}

public class TelegramUser
{
    [JsonPropertyName("id")]
    public long Id { get; set; }
    
    [JsonPropertyName("is_bot")]
    public bool IsBot { get; set; }
    
    [JsonPropertyName("first_name")]
    public string? FirstName { get; set; }
    
    [JsonPropertyName("username")]
    public string? Username { get; set; }
}

public class TelegramChat
{
    [JsonPropertyName("id")]
    public long Id { get; set; }
    
    [JsonPropertyName("type")]
    public string? Type { get; set; }
    
    [JsonPropertyName("title")]
    public string? Title { get; set; }
    
    [JsonPropertyName("first_name")]
    public string? FirstName { get; set; }
    
    [JsonPropertyName("username")]
    public string? Username { get; set; }
}
