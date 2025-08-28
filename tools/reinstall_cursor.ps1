# Script cài đặt lại Cursor về chế độ full màn hình
# Chạy với quyền Administrator

Write-Host "=== CÀI ĐẶT LẠI CURSOR ===" -ForegroundColor Green

# 1. Gỡ cài đặt Cursor hiện tại
Write-Host "Đang gỡ cài đặt Cursor..." -ForegroundColor Yellow
try {
    $cursorPath = Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\Programs\Cursor" -ErrorAction SilentlyContinue
    if ($cursorPath) {
        Start-Process "C:\Users\$env:USERNAME\AppData\Local\Programs\Cursor\Cursor.exe" -ArgumentList "--uninstall" -Wait
        Write-Host "Đã gỡ cài đặt Cursor" -ForegroundColor Green
    } else {
        Write-Host "Không tìm thấy Cursor đã cài đặt" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Lỗi khi gỡ cài đặt: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Tải Cursor mới nhất
Write-Host "Đang tải Cursor mới nhất..." -ForegroundColor Yellow
$downloadUrl = "https://download.cursor.sh/windows/x64"
$outputPath = "$env:TEMP\CursorSetup.exe"

try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath
    Write-Host "Đã tải xong Cursor" -ForegroundColor Green
} catch {
    Write-Host "Lỗi khi tải Cursor: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 3. Cài đặt Cursor
Write-Host "Đang cài đặt Cursor..." -ForegroundColor Yellow
try {
    Start-Process -FilePath $outputPath -ArgumentList "/S" -Wait
    Write-Host "Đã cài đặt xong Cursor" -ForegroundColor Green
} catch {
    Write-Host "Lỗi khi cài đặt: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 4. Dọn dẹp file tạm
Remove-Item $outputPath -Force -ErrorAction SilentlyContinue

Write-Host "=== HOÀN THÀNH ===" -ForegroundColor Green
Write-Host "Cursor đã được cài đặt lại về chế độ full màn hình" -ForegroundColor Green
Write-Host "Khởi động lại máy tính để đảm bảo hoạt động ổn định" -ForegroundColor Yellow

# Hỏi có muốn khởi động lại không
$restart = Read-Host "Có muốn khởi động lại máy tính ngay không? (y/n)"
if ($restart -eq "y" -or $restart -eq "Y") {
    Restart-Computer -Force
}
