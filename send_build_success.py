#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script gửi thông báo build thành công
"""

import icon3

def send_build_success():
    """Gửi thông báo build thành công"""
    message = """🎉 <b>GITHUB ACTIONS BUILD THÀNH CÔNG!</b>

✅ <b>XMLProcessor EXE đã được build!</b>

📊 <b>Thông tin Build:</b>
• Run ID: 17292105377
• Workflow: Build XMLProcessor EXE
• Status: completed
• Conclusion: success
• Thời gian: 2025-08-28 09:44:37 UTC

📁 <b>File được tạo:</b>
• Tên: XMLProcessor.exe
• Kích thước: ~20.5 MB
• Platform: Windows 64-bit

🚀 <b>Quy trình tự động hoạt động hoàn hảo!</b>
• Bot nhận XML → Auto commit → GitHub build → EXE sẵn sàng

📥 <b>Tải EXE:</b>
• Vào <a href="https://github.com/Mrkent1/Xml/actions/runs/17292105377">Run Details</a>
• Tải artifact "XMLProcessor-EXE"

🎯 <b>Build hoàn tất và sẵn sàng sử dụng!</b>"""
    
    icon3.send_telegram_message(message)
    print("✅ Đã gửi thông báo build thành công!")

if __name__ == "__main__":
    send_build_success()
