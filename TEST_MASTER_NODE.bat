@echo off
chcp 65001 >nul
title THUẾ FORTRESS SYNC - TEST MASTER NODE

echo.
echo 🚀 THUẾ FORTRESS SYNC - TEST MASTER NODE
echo ================================================
echo.

echo 📁 Kiểm tra thư mục hiện tại...
cd /d "C:\Users\Administrator\Videos\SYNC TAXX"
echo ✅ Thư mục: %CD%
echo.

echo 🔍 Kiểm tra file Python...
if exist "hybrid_fortress_master.py" (
    echo ✅ Tìm thấy: hybrid_fortress_master.py
) else (
    echo ❌ Không tìm thấy: hybrid_fortress_master.py
    pause
    exit /b 1
)
echo.

echo 🔍 Kiểm tra Syncthing...
if exist "syncthing-windows-amd64-v1.27.6\syncthing.exe" (
    echo ✅ Tìm thấy: syncthing.exe
) else (
    echo ❌ Không tìm thấy: syncthing.exe
    echo 💡 Hãy tải Syncthing từ https://syncthing.net/
    pause
    exit /b 1
)
echo.

echo 🚀 Khởi động Master Node...
echo.
python hybrid_fortress_master.py

echo.
echo ⏹️  Master Node đã dừng
pause
