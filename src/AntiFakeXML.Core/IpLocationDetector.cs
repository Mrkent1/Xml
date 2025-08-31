using System;
using System.Net;
using System.Text.RegularExpressions;

namespace AntiFakeXML.Core;

public class IpLocationDetector
{
    public string DetectRegion(string ipAddress)
    {
        if (string.IsNullOrEmpty(ipAddress))
            return "Không xác định";
            
        try
        {
            // Lấy octet đầu tiên của IP
            var firstOctet = GetFirstOctet(ipAddress);
            
            return firstOctet switch
            {
                112 => "Hà Nội",
                113 => "TP.HCM", 
                114 => "Đà Nẵng",
                115 => "Cần Thơ",
                116 => "Quảng Ninh",
                117 => "Thanh Hóa",
                118 => "Nghệ An",
                119 => "Hải Phòng",
                120 => "Thái Nguyên",
                121 => "Lào Cai",
                122 => "Yên Bái",
                123 => "Tuyên Quang",
                124 => "Phú Thọ",
                125 => "Vĩnh Phúc",
                126 => "Bắc Ninh",
                127 => "Bắc Giang",
                128 => "Lạng Sơn",
                129 => "Cao Bằng",
                130 => "Hà Giang",
                131 => "Tuyên Quang",
                132 => "Phú Thọ",
                133 => "Vĩnh Phúc",
                134 => "Bắc Ninh",
                135 => "Bắc Giang",
                136 => "Lạng Sơn",
                137 => "Cao Bằng",
                138 => "Hà Giang",
                139 => "Tuyên Quang",
                140 => "Phú Thọ",
                141 => "Vĩnh Phúc",
                142 => "Bắc Ninh",
                143 => "Bắc Giang",
                144 => "Lạng Sơn",
                145 => "Cao Bằng",
                146 => "Hà Giang",
                147 => "Tuyên Quang",
                148 => "Phú Thọ",
                149 => "Vĩnh Phúc",
                150 => "Bắc Ninh",
                151 => "Bắc Giang",
                152 => "Lạng Sơn",
                153 => "Cao Bằng",
                154 => "Hà Giang",
                155 => "Tuyên Quang",
                156 => "Phú Thọ",
                157 => "Vĩnh Phúc",
                158 => "Bắc Ninh",
                159 => "Bắc Giang",
                160 => "Lạng Sơn",
                161 => "Cao Bằng",
                162 => "Hà Giang",
                163 => "Tuyên Quang",
                164 => "Phú Thọ",
                165 => "Vĩnh Phúc",
                166 => "Bắc Ninh",
                167 => "Bắc Giang",
                168 => "Lạng Sơn",
                169 => "Cao Bằng",
                170 => "Hà Giang",
                171 => "Tuyên Quang",
                172 => "Phú Thọ",
                173 => "Vĩnh Phúc",
                174 => "Bắc Ninh",
                175 => "Bắc Giang",
                176 => "Lạng Sơn",
                177 => "Cao Bằng",
                178 => "Hà Giang",
                179 => "Tuyên Quang",
                180 => "Phú Thọ",
                181 => "Vĩnh Phúc",
                182 => "Bắc Ninh",
                183 => "Bắc Giang",
                184 => "Lạng Sơn",
                185 => "Cao Bằng",
                186 => "Hà Giang",
                187 => "Tuyên Quang",
                188 => "Phú Thọ",
                189 => "Vĩnh Phúc",
                190 => "Bắc Ninh",
                191 => "Bắc Giang",
                192 => "Lạng Sơn",
                193 => "Cao Bằng",
                194 => "Hà Giang",
                195 => "Tuyên Quang",
                196 => "Phú Thọ",
                197 => "Vĩnh Phúc",
                198 => "Bắc Ninh",
                199 => "Bắc Giang",
                200 => "Lạng Sơn",
                201 => "Cao Bằng",
                202 => "Hà Giang",
                203 => "Tuyên Quang",
                204 => "Phú Thọ",
                205 => "Vĩnh Phúc",
                206 => "Bắc Ninh",
                207 => "Bắc Giang",
                208 => "Lạng Sơn",
                209 => "Cao Bằng",
                210 => "Hà Giang",
                211 => "Tuyên Quang",
                212 => "Phú Thọ",
                213 => "Vĩnh Phúc",
                214 => "Bắc Ninh",
                215 => "Bắc Giang",
                216 => "Lạng Sơn",
                217 => "Cao Bằng",
                218 => "Hà Giang",
                219 => "Tuyên Quang",
                220 => "Phú Thọ",
                221 => "Vĩnh Phúc",
                222 => "Bắc Ninh",
                223 => "Bắc Giang",
                224 => "Lạng Sơn",
                225 => "Cao Bằng",
                226 => "Hà Giang",
                227 => "Tuyên Quang",
                228 => "Phú Thọ",
                229 => "Vĩnh Phúc",
                230 => "Bắc Ninh",
                231 => "Bắc Giang",
                232 => "Lạng Sơn",
                233 => "Cao Bằng",
                234 => "Hà Giang",
                235 => "Tuyên Quang",
                236 => "Phú Thọ",
                237 => "Vĩnh Phúc",
                238 => "Bắc Ninh",
                239 => "Bắc Giang",
                240 => "Lạng Sơn",
                241 => "Cao Bằng",
                242 => "Hà Giang",
                243 => "Tuyên Quang",
                244 => "Phú Thọ",
                245 => "Vĩnh Phúc",
                246 => "Bắc Ninh",
                247 => "Bắc Giang",
                248 => "Lạng Sơn",
                249 => "Cao Bằng",
                250 => "Hà Giang",
                251 => "Tuyên Quang",
                252 => "Phú Thọ",
                253 => "Vĩnh Phúc",
                254 => "Bắc Ninh",
                255 => "Bắc Giang",
                _ => "Không xác định"
            };
        }
        catch
        {
            return "Không xác định";
        }
    }
    
    private int GetFirstOctet(string ipAddress)
    {
        try
        {
            // Kiểm tra IP hợp lệ
            if (!IsValidIpAddress(ipAddress))
                return 0;
                
            var parts = ipAddress.Split('.');
            if (parts.Length == 4 && int.TryParse(parts[0], out int firstOctet))
            {
                return firstOctet;
            }
            
            return 0;
        }
        catch
        {
            return 0;
        }
    }
    
    private bool IsValidIpAddress(string ipAddress)
    {
        if (string.IsNullOrEmpty(ipAddress))
            return false;
            
        // Regex để kiểm tra IP hợp lệ
        var ipPattern = @"^(\d{1,3}\.){3}\d{1,3}$";
        if (!Regex.IsMatch(ipAddress, ipPattern))
            return false;
            
        var parts = ipAddress.Split('.');
        foreach (var part in parts)
        {
            if (!int.TryParse(part, out int octet) || octet < 0 || octet > 255)
                return false;
        }
        
        return true;
    }
    
    public string GetRegionDescription(string region)
    {
        return region switch
        {
            "Hà Nội" => "Thủ đô - Trung tâm hành chính",
            "TP.HCM" => "Thành phố lớn nhất - Kinh tế",
            "Đà Nẵng" => "Thành phố biển - Du lịch",
            "Cần Thơ" => "Đồng bằng sông Cửu Long",
            "Quảng Ninh" => "Vùng mỏ - Du lịch biển",
            "Thanh Hóa" => "Vùng ven biển - Nông nghiệp",
            "Nghệ An" => "Vùng ven biển - Nông nghiệp",
            "Hải Phòng" => "Thành phố cảng - Công nghiệp",
            _ => "Vùng miền khác"
        };
    }
}
