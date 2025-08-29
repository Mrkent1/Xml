@echo off
chcp 65001 >nul
title XML SCANNER & CLASSIFIER - THUE FORTRESS SYNC
color 0B

echo.
echo ========================================
echo    XML SCANNER & CLASSIFIER
echo    THUE FORTRESS SYNC
echo ========================================
echo.

echo 🔍 Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt!
    echo 💡 Vui lòng cài đặt Python 3.7+ trước
    pause
    exit /b 1
)

echo ✅ Python đã sẵn sàng
echo.

echo 🔍 Kiểm tra file XML Scanner...
if not exist "xml_scanner_gui.py" (
    echo ❌ Không tìm thấy file xml_scanner_gui.py!
    echo 💡 Vui lòng đảm bảo file tồn tại trong thư mục này
    pause
    exit /b 1
)

echo ✅ File XML Scanner đã sẵn sàng
echo.

echo 🚀 Khởi động XML Scanner GUI...
echo 💡 Tool sẽ mở giao diện hiện đại để quét và phân loại file XML
echo.

python xml_scanner_gui.py

if errorlevel 1 (
    echo.
    echo ❌ Có lỗi xảy ra khi chạy XML Scanner
    echo 💡 Kiểm tra log để biết thêm chi tiết
    pause
) else (
    echo.
    echo ✅ XML Scanner đã đóng thành công
)

pause
