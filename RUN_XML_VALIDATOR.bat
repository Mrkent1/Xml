@echo off
chcp 65001 >nul
title XML VALIDATOR - THUE FORTRESS SYNC
color 0A

echo.
echo ========================================
echo    XML VALIDATOR & SCANNER
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

echo 🔍 Kiểm tra file XML Validator...
if not exist "xml_validator_gui.py" (
    echo ❌ Không tìm thấy file xml_validator_gui.py!
    echo 💡 Vui lòng đảm bảo file tồn tại trong thư mục này
    pause
    exit /b 1
)

echo ✅ File XML Validator đã sẵn sàng
echo.

echo 🚀 Khởi động XML Validator GUI...
echo 💡 Tool sẽ mở giao diện để quét và validate file XML
echo.

python xml_validator_gui.py

if errorlevel 1 (
    echo.
    echo ❌ Có lỗi xảy ra khi chạy XML Validator
    echo 💡 Kiểm tra log để biết thêm chi tiết
    pause
) else (
    echo.
    echo ✅ XML Validator đã đóng thành công
)

pause
