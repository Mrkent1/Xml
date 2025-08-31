# -*- coding: utf-8 -*-
"""
File cấu hình cho script kiểm tra GitHub Actions Build Status
và hệ thống quản lý nhiều máy (10-20 machines)
Thay đổi các thông tin dưới đây theo nhu cầu của bạn
"""

# ===== CẤU HÌNH TELEGRAM BOT =====
# Token bot Telegram (lấy từ @BotFather)
TELEGRAM_BOT_TOKEN = "7283723256:AAEqXPiQ-s2sYI8vyhfUyrcq8uL-pRG_UZI"

# ID nhóm Telegram (lấy từ @userinfobot)
TELEGRAM_GROUP_ID = "-1002980917638"

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

# ===== CẤU HÌNH MACHINE MANAGEMENT SYSTEM =====
# Database SQLite cho quản lý nhiều máy
MACHINE_DB_PATH = "machines.db"

# Cấu hình versioning tự động
AUTO_VERSIONING = True
VERSION_FORMAT = "v{}.{}.{}"  # v1.0.1, v1.0.2...

# Cấu hình multi-platform builds
BUILD_PLATFORMS = ["windows", "linux", "macos"]
DEFAULT_PLATFORM = "windows"

# Cấu hình machine health check
HEALTH_CHECK_INTERVAL = 300  # 5 phút
MACHINE_TIMEOUT = 600  # 10 phút

# Cấu hình batch operations
MAX_BATCH_SIZE = 20  # Tối đa 20 máy cùng lúc
BATCH_TIMEOUT = 1800  # 30 phút timeout cho batch

# Cấu hình alerting
ALERT_ON_FAILURE = True
ALERT_ON_TIMEOUT = True
ALERT_ON_OFFLINE = True

# ===== CẤU HÌNH ENTERPRISE DATABASE =====
# Database cho smart template lookup
ENTERPRISE_DB_PATH = "config/enterprises.db"

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

5. CẤU HÌNH MACHINE MANAGEMENT:
   - Machine database sẽ tự động tạo
   - Mỗi máy sẽ có Machine ID duy nhất
   - Hệ thống tự động quản lý 10-20 máy
"""
