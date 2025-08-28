# 🚀 XMLProcessor - Smart XML Overwrite Tool

## 📋 Mô tả
XMLProcessor là công cụ thông minh để tự động ghi đè file XML dựa trên MST (Mã Số Thuế) và các trường định danh khác.

## ✨ Tính năng chính
- 🔍 **Smart Template Matching**: Tìm template gốc theo MST
- 📁 **100% File Copy**: Copy hoàn toàn file template gốc
- 🛡️ **File Protection**: Bảo vệ file gốc khỏi bị thay đổi
- 📱 **Telegram Bot**: Điều khiển từ xa qua Telegram
- 🔄 **Auto Monitoring**: Giám sát toàn bộ ổ đĩa hệ thống

## 🚀 Build trên GitHub Actions

### Tự động build khi:
- ✅ Push code lên branch `main` hoặc `master`
- ✅ Tạo Pull Request
- ✅ Manual trigger (workflow_dispatch)

### Kết quả build:
- 📦 **EXE File**: `XMLProcessor.exe`
- 🔒 **No Console**: Chạy ngầm
- 📁 **Single File**: Tất cả dependencies trong 1 file
- 📋 **Templates**: Bao gồm thư mục templates

## 📥 Download
1. Vào **Actions** tab trên GitHub
2. Chọn workflow **Build XMLProcessor EXE**
3. Tải **XMLProcessor-EXE** artifact

## 🛠️ Cài đặt
1. Tải `XMLProcessor.exe`
2. Chạy với quyền Administrator
3. EXE sẽ tự động bảo vệ XML

## 🔧 Cấu hình
- **Telegram Bot**: Cấu hình trong `icon3.py`
- **Templates**: Đặt file XML template trong thư mục `templates/`
- **Protected Folders**: File trong `ORIGINAL_TEMPLATES_SAFE/` và `PROTECTED_XML_FILES_SAFE/` sẽ không bị giám sát

## 📝 License
MIT License - Sử dụng tự do cho mục đích thương mại và cá nhân
