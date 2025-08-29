@echo off
chcp 65001 >nul
title XML VALIDATOR - THUE FORTRESS SYNC

echo.
echo ========================================
echo    XML VALIDATOR & SCANNER
echo    THUE FORTRESS SYNC
echo ========================================
echo.

echo 🚀 Khởi động XML Validator GUI...
echo 💡 Tool sẽ mở giao diện để quét và validate file XML
echo.

cd /d "C:\Users\Administrator\Videos\SYNC TAXX"
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
