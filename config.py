# -*- coding: utf-8 -*-
"""
File cấu hình cho script kiểm tra GitHub Actions Build Status
Thay đổi các thông tin dưới đây theo nhu cầu của bạn
"""

# ===== CẤU HÌNH TELEGRAM BOT =====
# Token bot Telegram (lấy từ @BotFather)
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"

# ID nhóm Telegram (lấy từ @userinfobot)
TELEGRAM_GROUP_ID = "YOUR_GROUP_ID"

# ===== CẤU HÌNH GITHUB =====
# Repository GitHub (format: username/repository)
GITHUB_REPO = "Mrkent1/Xml"

# GitHub Personal Access Token (lấy từ GitHub Settings > Developer settings > Personal access tokens)
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"

# ===== CẤU HÌNH THÔNG BÁO =====
# Thời gian chờ giữa các lần kiểm tra (giây)
CHECK_INTERVAL = 30

# Số lần kiểm tra tối đa
MAX_CHECKS = 20

# ===== HƯỚNG DẪN LẤY THÔNG TIN =====
"""
1. LẤY TELEGRAM_TOKEN:
   - Chat với @BotFather trên Telegram
   - Gõ /newbot
   - Đặt tên bot và username
   - Copy token được cung cấp

2. LẤY TELEGRAM_GROUP_ID:
   - Thêm @userinfobot vào nhóm
   - Gõ /start
   - Copy "Chat ID" (số âm)

3. LẤY GITHUB_TOKEN:
   - Vào GitHub.com > Settings > Developer settings > Personal access tokens
   - Generate new token
   - Chọn quyền: repo, workflow
   - Copy token được cung cấp

4. CẬP NHẬT FILE NÀY:
   - Thay thế các giá trị "YOUR_..." bằng thông tin thật
   - Lưu file
   - Chạy script check_build_status.py
"""
