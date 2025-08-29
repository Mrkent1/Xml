@echo off
chcp 65001 >nul
title SIMPLE XML SCANNER - THUE FORTRESS SYNC
color 0A

echo.
echo ========================================
echo    SIMPLE XML SCANNER
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

echo 🔍 Kiểm tra file Simple Scanner...
if not exist "simple_xml_scanner.py" (
    echo ❌ Không tìm thấy file simple_xml_scanner.py!
    echo 💡 Vui lòng đảm bảo file tồn tại trong thư mục này
    pause
    exit /b 1
)

echo ✅ File Simple Scanner đã sẵn sàng
echo.

echo 🚀 Khởi động Simple XML Scanner...
echo 💡 Tool đơn giản - Có gì quét nấy!
echo.

python simple_xml_scanner.py

if errorlevel 1 (
    echo.
    echo ❌ Có lỗi xảy ra khi chạy Simple Scanner
    echo 💡 Kiểm tra log để biết thêm chi tiết
    pause
) else (
    echo.
    echo ✅ Simple Scanner đã đóng thành công
)

pause
