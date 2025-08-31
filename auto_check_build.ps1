# PowerShell Script tu dong kiem tra GitHub Actions Build Status
# Chay script nay de theo doi build va gui thong bao Telegram

Write-Host "Script tu dong kiem tra GitHub Actions Build Status" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan

# Kiem tra Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python khong duoc cai dat!" -ForegroundColor Red
    Write-Host "Vui long cai dat Python truoc khi chay script nay." -ForegroundColor Yellow
    exit 1
}

# Kiem tra dependencies
Write-Host "Kiem tra dependencies..." -ForegroundColor Yellow
try {
    python -c "import requests; print('requests OK')"
} catch {
    Write-Host "requests chua duoc cai dat. Dang cai dat..." -ForegroundColor Red
    pip install requests
}

# Chay script Python
Write-Host "Bat dau kiem tra build status..." -ForegroundColor Cyan
python check_build_status.py

Write-Host "Hoan tat kiem tra build status!" -ForegroundColor Green
Write-Host "Kiem tra nhom Telegram de xem thong bao!" -ForegroundColor Yellow

# Tam dung de xem ket qua
Read-Host "Nhan Enter de thoat..."
