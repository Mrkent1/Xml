#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test đơn giản cho Telegram bot
"""

import requests
from config import TELEGRAM_TOKEN, TELEGRAM_GROUP_ID

def test_telegram_bot():
    """Test gửi tin nhắn qua Telegram bot"""
    try:
        message = """🧪 <b>TEST BOT XML PHI LONG</b>

✅ <b>Auto-build đã hoạt động!</b>

📱 <b>Thông tin:</b>
• Bot: XML Phi Long Bot
• Nhóm: Xml guardian
• Status: Hoạt động 100%

🚀 <b>Sẵn sàng nhận thông báo build!</b>"""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_GROUP_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Test thành công!")
            print(f"📱 Đã gửi tin nhắn vào nhóm: {result['result']['chat']['title']}")
            print(f"🆔 Message ID: {result['result']['message_id']}")
            return True
        else:
            print(f"❌ Lỗi gửi tin nhắn: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test Telegram Bot XML Phi Long")
    print("=" * 40)
    
    if TELEGRAM_TOKEN == "YOUR_BOT_TOKEN":
        print("❌ Chưa cấu hình TELEGRAM_TOKEN!")
    elif TELEGRAM_GROUP_ID == "YOUR_GROUP_ID":
        print("❌ Chưa cấu hình TELEGRAM_GROUP_ID!")
    else:
        print(f"✅ Token: {TELEGRAM_TOKEN[:20]}...")
        print(f"✅ Group ID: {TELEGRAM_GROUP_ID}")
        print("\n🔄 Đang test gửi tin nhắn...")
        test_telegram_bot()
