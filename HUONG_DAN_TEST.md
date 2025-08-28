# 🚀 HƯỚNG DẪN TEST THUẾ FORTRESS SYNC

## 📋 **TRẠNG THÁI DỰ ÁN: 95% HOÀN THÀNH**

### ✅ **Đã hoàn thành:**
- Master Node code hoàn chỉnh
- Slave Node code hoàn chỉnh  
- Stealth Guard hoạt động
- Monitoring system sẵn sàng
- Telegram Bot framework
- File batch test tự động

### ⚠️ **Cần thực hiện (5%):**
- Test Master Node
- Cấu hình Syncthing Web UI
- Test Slave Node
- Final testing thực tế

---

## 🎯 **BƯỚC 1: TEST MASTER NODE**

### **1.1. Khởi động Syncthing**
```bash
# Mở cmd với quyền Admin
cd "C:\Users\Administrator\Videos\SYNC TAXX\syncthing-windows-amd64-v1.27.6"
syncthing.exe
```

**Kết quả mong đợi:**
- ✅ Syncthing khởi động
- ✅ Có icon trong system tray
- ✅ Web UI mở tại http://127.0.0.1:8384

### **1.2. Test Master Node**
```bash
# Mở cmd mới
cd "C:\Users\Administrator\Videos\SYNC TAXX"
python hybrid_fortress_master.py
```

**Kết quả mong đợi:**
```
🚀 THUẾ FORTRESS SYNC - MASTER NODE
==================================================
📁 Thiết lập Syncthing folder...
✅ Syncthing folder setup completed
⚙️  Tạo cấu hình Syncthing...
✅ Syncthing folder config created/updated
🔄 Khởi động monitoring...
✅ Monitoring started successfully

✅ Master Node started successfully!
==================================================
📁 Folder ID: tax_xml_master
📂 Path: C:\Users\Administrator\Videos\SYNC TAXX
🔑 API Key: ✅ Đã cấu hình
🔄 Monitoring: ✅ Đang chạy
🤖 Telegram Bot: ✅ Đã cấu hình
==================================================
```

---

## 🎯 **BƯỚC 2: CẤU HÌNH SYNCTHING WEB UI**

### **2.1. Mở Syncthing Web UI**
- **URL:** http://127.0.0.1:8384
- **Username:** (để trống)
- **Password:** (để trống)

### **2.2. Cấu hình Folder**
1. **Vào tab "Folders"**
2. **Kiểm tra folder "tax_xml_master" đã có**
3. **Nếu chưa có, tạo mới:**
   - **Folder ID:** `tax_xml_master`
   - **Folder Label:** `THUẾ FORTRESS SYNC - XML Master`
   - **Folder Path:** `C:\Users\Administrator\Videos\SYNC TAXX`
   - **Folder Type:** `Send & Receive`

### **2.3. Lấy API Key**
1. **Vào tab "Actions" → "Settings"**
2. **Vào "GUI"**
3. **Copy "API Key"**

---

## 🎯 **BƯỚC 3: TEST SLAVE NODE**

### **3.1. Cài đặt Syncthing trên máy Slave**
1. **Tải Syncthing:** https://syncthing.net/
2. **Cài đặt và khởi động**
3. **Đợi Syncthing khởi động xong**

### **3.2. Test Slave Node**
```bash
# Trên máy Slave
cd "C:\Users\Administrator\Videos\SYNC TAXX"
python hybrid_fortress_slave.py
```

**Kết quả mong đợi:**
```
🔒 THUẾ FORTRESS SYNC - SLAVE NODE
==================================================
📁 Thiết lập Syncthing folder...
✅ Syncthing folder setup completed
⚙️  Tạo cấu hình Syncthing...
✅ Syncthing folder config created/updated (Receive-Only)
🔄 Khởi động monitoring...
✅ Monitoring started successfully

✅ Slave Node started successfully!
==================================================
🆔 Machine ID: SLAVE_HOSTNAME_XXXXXXXX
📁 Folder ID: tax_xml_master
📂 Path: C:\Users\Administrator\Documents\TaxXML
🔄 Monitoring: ✅ Đang chạy
🛡️  Stealth Guard: ✅ Đang chạy
🖥️  Windows API: ✅ Có sẵn
==================================================
```

---

## 🎯 **BƯỚC 4: KẾT NỐI MASTER-SLAVE**

### **4.1. Trên Master Node**
1. **Mở Syncthing Web UI:** http://127.0.0.1:8384
2. **Vào tab "Devices"**
3. **Click "Add Device"**
4. **Nhập Device ID của Slave**
5. **Chọn folder "tax_xml_master"**

### **4.2. Trên Slave Node**
1. **Mở Syncthing Web UI:** http://127.0.0.1:8384
2. **Chấp nhận kết nối từ Master**
3. **Kiểm tra folder "tax_xml_master"**

---

## 🎯 **BƯỚC 5: TEST BẢO VỆ FILE**

### **5.1. Test trên Slave Node**
1. **Mở thư mục:** `C:\Users\Administrator\Documents\TaxXML`
2. **Sửa đổi file XML bất kỳ**
3. **Lưu file**
4. **Quan sát:**
   - ✅ File bị ghi đè về bản gốc
   - ✅ Stealth Guard hoạt động
   - ✅ Log ghi nhận hành vi bảo vệ

### **5.2. Kiểm tra Log**
- **Master Log:** `%APPDATA%\ThuếFortressSync\hybrid_master.log`
- **Slave Log:** `%APPDATA%\WindowsSecurityUpdate\security_update.log`

---

## 🎯 **BƯỚC 6: TEST TELEGRAM BOT**

### **6.1. Gửi lệnh test**
```
/start - Mở control panel
/status - Kiểm tra trạng thái hệ thống
/machines - Xem danh sách máy con
/health - Kiểm tra sức khỏe máy
```

### **6.2. Kiểm tra thông báo**
- ✅ Thông báo file mới
- ✅ Cảnh báo bảo mật
- ✅ Health check report

---

## 🔧 **TROUBLESHOOTING**

### **❌ Lỗi thường gặp:**

#### **1. Syncthing không khởi động:**
```bash
# Kiểm tra port 8384
netstat -an | findstr 8384

# Khởi động lại Syncthing
taskkill /f /im syncthing.exe
syncthing.exe
```

#### **2. Không kết nối được Master:**
- Kiểm tra firewall
- Kiểm tra Device ID
- Kiểm tra folder ID

#### **3. File không đồng bộ:**
- Kiểm tra quyền thư mục
- Kiểm tra cấu hình folder
- Kiểm tra log Syncthing

---

## 🎉 **KẾT QUẢ CUỐI CÙNG**

### **✅ Hệ thống hoạt động:**
- **Master Node:** Quản lý tập trung
- **Slave Node:** Bảo vệ file tự động
- **Syncthing:** Đồng bộ real-time
- **Stealth Guard:** Ẩn hoạt động
- **Telegram Bot:** Điều khiển từ xa

### **🛡️ Bảo mật đạt được:**
- File thuế XML luôn được bảo vệ
- Kẻ tấn công không biết file đã bị ghi đè
- Đồng bộ tự động giữa Master và Slave
- Quản lý tập trung từ Master Node

---

## 🚀 **SẴN SÀNG TEST!**

**Bây giờ anh có thể:**
1. **Chạy `TEST_MASTER_NODE.bat`** để test Master Node
2. **Làm theo hướng dẫn** để cấu hình Syncthing
3. **Chạy `TEST_SLAVE_NODE.bat`** để test Slave Node
4. **Test bảo vệ file** thực tế

**Chúc anh test thành công! 🎯✨**
