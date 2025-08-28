# PowerShell Script tự động kiểm tra GitHub Actions Build Status
# Chạy script này để theo dõi build và gửi thông báo Telegram

Write-Host "🚀 Script tự động kiểm tra GitHub Actions Build Status" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# Kiểm tra Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python không được cài đặt!" -ForegroundColor Red
    Write-Host "Vui lòng cài đặt Python trước khi chạy script này." -ForegroundColor Yellow
    exit 1
}

# Kiểm tra dependencies
Write-Host "📦 Kiểm tra dependencies..." -ForegroundColor Yellow
try {
    python -c "import requests; print('✅ requests')"
} catch {
    Write-Host "❌ requests chưa được cài đặt. Đang cài đặt..." -ForegroundColor Red
    pip install requests
}

# Chạy script Python
Write-Host "🔍 Bắt đầu kiểm tra build status..." -ForegroundColor Cyan
python check_build_status.py

Write-Host "✅ Hoàn tất kiểm tra build status!" -ForegroundColor Green
Write-Host "📱 Kiểm tra nhóm Telegram để xem thông báo!" -ForegroundColor Yellow

# Tạm dừng để xem kết quả
Read-Host "Nhấn Enter để thoát..."
