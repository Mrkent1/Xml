# 🚀 XMLProcessor - Smart XML Overwrite Tool

## 📋 Mô tả
XMLProcessor là công cụ thông minh để tự động ghi đè file XML dựa trên MST (Mã Số Thuế) và các trường định danh khác. **Hỗ trợ quản lý 10-20 máy cùng lúc với Machine Management System.**

## ✨ Tính năng chính
- 🔍 **Smart Template Matching**: Tìm template gốc theo MST
- 📁 **100% File Copy**: Copy hoàn toàn file template gốc
- 🛡️ **File Protection**: Bảo vệ file gốc khỏi bị thay đổi
- 📱 **Telegram Bot**: Điều khiển từ xa qua Telegram
- 🔄 **Auto Monitoring**: Giám sát toàn bộ ổ đĩa hệ thống
- 🤖 **Machine Management**: Quản lý 10-20 máy cùng lúc
- ⚡ **Batch Operations**: Thực hiện lệnh hàng loạt
- 🏥 **Health Monitoring**: Giám sát sức khỏe máy real-time

## 🚀 Build trên GitHub Actions

### Tự động build khi:
- ✅ Push code lên branch `main` hoặc `master`
- ✅ Tạo Pull Request
- ✅ Manual trigger (workflow_dispatch)
- ✅ **Multi-platform support**: Windows, Linux, macOS

### Kết quả build:
- 📦 **EXE Files**: `XMLProcessor-Windows.exe`, `XMLProcessor-Linux`, `XMLProcessor-MacOS`
- 🔒 **No Console**: Chạy ngầm (Windows)
- 📁 **Single File**: Tất cả dependencies trong 1 file
- 📋 **Templates**: Bao gồm thư mục templates
- 🤖 **Machine Management**: Hệ thống quản lý máy tích hợp

## 🤖 Machine Management System

### Tính năng chính:
- **Machine ID duy nhất**: Mỗi máy có ID riêng biệt
- **Real-time monitoring**: Giám sát trạng thái máy real-time
- **Health check automation**: Tự động kiểm tra sức khỏe máy
- **Batch operations**: Thực hiện lệnh trên nhiều máy cùng lúc
- **Machine grouping**: Nhóm máy theo chức năng
- **Auto-registration**: Tự động đăng ký máy khi khởi động

### Quản lý máy:
- 📊 **Dashboard**: Xem trạng thái tất cả máy
- 🏥 **Health Check**: Kiểm tra sức khỏe máy
- ⚡ **Batch Commands**: Lệnh hàng loạt
- 📁 **Template Updates**: Cập nhật templates đồng bộ
- 🔄 **Service Management**: Khởi động lại dịch vụ

## 📥 Download
1. Vào **Actions** tab trên GitHub
2. Chọn workflow **Build XMLProcessor EXE - Multi-Platform**
3. Tải **XMLProcessor-[Platform]-EXE** artifact theo hệ điều hành

## 🛠️ Cài đặt
1. Tải `XMLProcessor-[Platform]` phù hợp với hệ điều hành
2. Chạy với quyền Administrator (Windows)
3. EXE sẽ tự động bảo vệ XML và đăng ký với hệ thống

## 🔧 Cấu hình
- **Telegram Bot**: Cấu hình trong `icon3.py`
- **Templates**: Đặt file XML template trong thư mục `templates/`
- **Protected Folders**: File trong `ORIGINAL_TEMPLATES_SAFE/` và `PROTECTED_XML_FILES_SAFE/` sẽ không bị giám sát
- **Machine Management**: Tự động tạo database `machines.db` trong `%APPDATA%/XMLOverwrite/`

## 📱 Telegram Bot Commands

### Lệnh cơ bản:
- `/start` hoặc `/menu` - Mở control panel
- `/status` - Kiểm tra trạng thái hệ thống
- `/ping` - Kiểm tra bot hoạt động
- `/build` - Trigger build EXE mới

### Machine Management:
- **MACHINES** button - Xem dashboard quản lý máy
- **HEALTH CHECK** - Kiểm tra sức khỏe tất cả máy
- **BATCH COMMAND** - Thực hiện lệnh hàng loạt
- **MACHINE INFO** - Thông tin chi tiết máy

## 🔄 Workflow Automation

### GitHub Actions:
1. **Auto-detect XML**: Tự động phát hiện thay đổi XML
2. **Multi-platform Build**: Build cho Windows, Linux, macOS
3. **Smart Versioning**: Tự động tạo version mới
4. **Auto-release**: Tự động tạo release với changelog

### Machine Management:
1. **Auto-registration**: Máy tự đăng ký khi khởi động
2. **Health monitoring**: Giám sát sức khỏe máy real-time
3. **Batch operations**: Thực hiện lệnh trên nhiều máy
4. **Status reporting**: Báo cáo trạng thái tự động

## 📝 License
MIT License - Sử dụng tự do cho mục đích thương mại và cá nhân

## 🆕 What's New in v2.0

### Machine Management System:
- ✅ Quản lý 10-20 máy cùng lúc
- ✅ Machine ID duy nhất cho mỗi máy
- ✅ Real-time status monitoring
- ✅ Health check automation
- ✅ Batch operations support

### Enhanced GitHub Actions:
- ✅ Multi-platform builds (Windows, Linux, macOS)
- ✅ Smart versioning (v1.0.1, v1.0.2...)
- ✅ Enhanced automation workflows
- ✅ Platform-specific builds

### Intelligent Bot System:
- ✅ Machine management dashboard
- ✅ Batch command execution
- ✅ Health monitoring
- ✅ Machine grouping
