#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động kiểm tra trạng thái GitHub Actions build
và gửi thông báo về nhóm Telegram
"""

import requests
import time
import json
import os
from datetime import datetime

# Import config từ file config.py
try:
    from config import (
        TELEGRAM_TOKEN, 
        TELEGRAM_GROUP_ID, 
        GITHUB_REPO, 
        GITHUB_TOKEN,
        CHECK_INTERVAL,
        MAX_CHECKS
    )
except ImportError:
    print("❌ Không thể import config.py. Vui lòng kiểm tra file config!")
    exit(1)

def send_telegram_message(message):
    """Gửi tin nhắn đến nhóm Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_GROUP_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"✅ Đã gửi thông báo Telegram: {message[:50]}...")
        else:
            print(f"❌ Lỗi gửi Telegram: {response.status_code}")
    except Exception as e:
        print(f"❌ Lỗi gửi Telegram: {e}")

def get_workflow_runs():
    """Lấy danh sách workflow runs"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()["workflow_runs"]
        else:
            print(f"❌ Lỗi lấy workflow runs: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Lỗi API GitHub: {e}")
        return []

def check_build_status():
    """Kiểm tra trạng thái build và gửi thông báo"""
    print("🔍 Đang kiểm tra trạng thái build...")
    
    runs = get_workflow_runs()
    if not runs:
        print("❌ Không thể lấy thông tin workflow")
        return
    
    latest_run = runs[0]  # Run mới nhất
    
    run_id = latest_run["id"]
    status = latest_run["status"]
    conclusion = latest_run.get("conclusion", "unknown")
    workflow_name = latest_run["name"]
    event = latest_run["event"]
    created_at = latest_run["created_at"]
    
    print(f"📊 Run ID: {run_id}")
    print(f"📋 Workflow: {workflow_name}")
    print(f"📈 Status: {status}")
    print(f"🎯 Conclusion: {conclusion}")
    print(f"🔔 Event: {event}")
    
    # Gửi thông báo dựa trên trạng thái
    if status == "completed":
        if conclusion == "success":
            message = f"""🎉 <b>BUILD THÀNH CÔNG!</b>

🚀 <b>XMLProcessor EXE</b> đã được build thành công!

📊 <b>Thông tin Build:</b>
• Run ID: <code>{run_id}</code>
• Workflow: {workflow_name}
• Event: {event}
• Thời gian: {created_at}

📥 <b>Tải EXE:</b>
• Vào <a href="https://github.com/{GITHUB_REPO}/actions">Actions tab</a>
• Tải artifact "XMLProcessor-EXE"

✅ <b>Tính năng:</b>
• No Console (--noconsole)
• Single File (--onefile)
• Templates included
• Smart XML overwrite
• Telegram bot integration

🎯 <b>Build hoàn tất!</b>"""
            
            send_telegram_message(message)
            print("🎉 Đã gửi thông báo BUILD THÀNH CÔNG!")
            
        elif conclusion == "failure":
            message = f"""❌ <b>BUILD THẤT BẠI!</b>

🚨 <b>XMLProcessor EXE</b> build thất bại!

📊 <b>Thông tin Build:</b>
• Run ID: <code>{run_id}</code>
• Workflow: {workflow_name}
• Event: {event}
• Thời gian: {created_at}

🔍 <b>Kiểm tra lỗi:</b>
• Vào <a href="https://github.com/{GITHUB_REPO}/actions/runs/{run_id}">Run details</a>
• Xem log lỗi chi tiết

⚠️ <b>Cần xử lý lỗi trước khi build lại!</b>"""
            
            send_telegram_message(message)
            print("❌ Đã gửi thông báo BUILD THẤT BẠI!")
            
    elif status == "in_progress":
        message = f"""⏳ <b>BUILD ĐANG CHẠY...</b>

🔄 <b>XMLProcessor EXE</b> đang được build!

📊 <b>Thông tin Build:</b>
• Run ID: <code>{run_id}</code>
• Workflow: {workflow_name}
• Event: {event}
• Thời gian: {created_at}

⏱️ <b>Trạng thái:</b> Đang xử lý...

📱 <b>Theo dõi:</b>
• Vào <a href="https://github.com/{GITHUB_REPO}/actions/runs/{run_id}">Run details</a>
• Xem log real-time

🔄 <b>Vui lòng chờ...</b>"""
        
        send_telegram_message(message)
        print("⏳ Đã gửi thông báo BUILD ĐANG CHẠY...")

def main():
    """Hàm chính"""
    print("🚀 Script kiểm tra GitHub Actions Build Status")
    print("=" * 50)
    
    # Kiểm tra cấu hình
    if TELEGRAM_TOKEN == "YOUR_BOT_TOKEN":
        print("⚠️ Cần cấu hình TELEGRAM_TOKEN thật!")
        return
    
    if TELEGRAM_GROUP_ID == "YOUR_GROUP_ID":
        print("⚠️ Cần cấu hình TELEGRAM_GROUP_ID thật!")
        return
    
    if GITHUB_TOKEN == "YOUR_GITHUB_TOKEN":
        print("⚠️ Cần cấu hình GITHUB_TOKEN thật!")
        return
    
    # Kiểm tra trạng thái build
    check_build_status()
    
    print("\n✅ Hoàn tất kiểm tra build status!")

if __name__ == "__main__":
    main()
