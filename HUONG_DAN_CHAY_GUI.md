# 🚀 HƯỚNG DẪN CHẠY XML VALIDATOR GUI

## 📁 VỊ TRÍ FILE CHÍNH

### **File GUI chính:**
```
C:\Users\Administrator\Videos\SYNC TAXX\xml_validator_gui.py
```

### **File batch để chạy:**
```
C:\Users\Administrator\Videos\SYNC TAXX\RUN_XML_VALIDATOR.bat
C:\Users\Administrator\Videos\SYNC TAXX\XML_VALIDATOR_SHORTCUT.bat
```

---

## 🚀 CÁCH CHẠY GUI

### **PHƯƠNG PHÁP 1: CHẠY TRỰC TIẾP**

#### **Bước 1: Mở Command Prompt**
- Nhấn `Win + R`
- Gõ `cmd` và nhấn Enter

#### **Bước 2: Di chuyển đến thư mục**
```bash
cd "C:\Users\Administrator\Videos\SYNC TAXX"
```

#### **Bước 3: Chạy GUI**
```bash
python xml_validator_gui.py
```

### **PHƯƠNG PHÁP 2: CHẠY FILE BATCH**

#### **Bước 1: Double-click file batch**
- Mở File Explorer
- Đi đến: `C:\Users\Administrator\Videos\SYNC TAXX`
- Double-click: `RUN_XML_VALIDATOR.bat` hoặc `XML_VALIDATOR_SHORTCUT.bat`

#### **Bước 2: Đợi GUI mở**
- File batch sẽ tự động:
  - Kiểm tra Python
  - Di chuyển đến thư mục đúng
  - Khởi động GUI

### **PHƯƠNG PHÁP 3: TẠO SHORTCUT TRÊN DESKTOP**

#### **Bước 1: Tạo shortcut**
1. Right-click trên Desktop
2. Chọn `New` → `Shortcut`
3. Nhập đường dẫn: `C:\Users\Administrator\Videos\SYNC TAXX\RUN_XML_VALIDATOR.bat`
4. Đặt tên: `XML Validator`

#### **Bước 2: Chạy từ Desktop**
- Double-click shortcut trên Desktop
- GUI sẽ mở ngay lập tức

---

## 💡 TÍNH NĂNG GUI

### **🔍 CHỨC NĂNG CHÍNH:**
1. **📂 Chọn File** - Chọn nhiều file XML để quét
2. **📁 Chọn Thư Mục** - Chọn cả thư mục chứa file XML
3. **🔍 QUÉT & VALIDATE** - Bắt đầu kiểm tra tất cả file
4. **📊 KẾT QUẢ** - Hiển thị kết quả chi tiết

### **📊 KẾT QUẢ HIỂN THỊ:**
- **✅ File gốc** - An toàn, có thể nạp vào kho Master
- **🆕 File mới** - Chưa có trong baseline
- **🚨 File fake** - KHÔNG NÊN nạp vào kho!
- **❌ File lỗi** - Có vấn đề về cấu trúc

---

## 🎯 SỬ DỤNG THỰC TẾ

### **TRƯỚC KHI NẠP VÀO KHO MASTER:**

#### **Bước 1: Mở GUI**
```bash
# Chạy từ Command Prompt
cd "C:\Users\Administrator\Videos\SYNC TAXX"
python xml_validator_gui.py

# HOẶC chạy file batch
RUN_XML_VALIDATOR.bat
```

#### **Bước 2: Chọn file cần kiểm tra**
1. **📂 Chọn File** - Chọn file XML cụ thể
2. **📁 Chọn Thư Mục** - Chọn thư mục chứa nhiều file XML

#### **Bước 3: Quét và validate**
1. **🔍 QUÉT & VALIDATE** - Bắt đầu kiểm tra
2. **Theo dõi progress bar** - Xem tiến độ quét
3. **Xem kết quả real-time** - Kết quả hiển thị ngay lập tức

#### **Bước 4: Xem báo cáo**
1. **Kiểm tra từng file** - Trạng thái chi tiết
2. **Xem tổng kết** - Thống kê tổng quan
3. **Quyết định** - Có nạp vào kho Master hay không

---

## 🔧 TROUBLESHOOTING

### **LỖI THƯỜNG GẶP:**

#### **1. Python không được cài đặt:**
```bash
# Kiểm tra Python
python --version

# Nếu không có, tải từ: https://python.org
```

#### **2. File không tìm thấy:**
```bash
# Kiểm tra đường dẫn
dir "C:\Users\Administrator\Videos\SYNC TAXX"

# Đảm bảo file xml_validator_gui.py tồn tại
```

#### **3. GUI không mở:**
```bash
# Chạy với thông báo lỗi
python -u xml_validator_gui.py

# Kiểm tra log để biết lỗi cụ thể
```

---

## 🎉 KẾT QUẢ

### **✅ ANH ĐÃ CÓ:**
1. **Tool GUI hoàn chỉnh** - Quét và validate file XML
2. **Nhiều cách chạy** - Trực tiếp, batch, shortcut
3. **Phát hiện file fake** - Với độ chính xác cao
4. **Bảo vệ kho Master** - Ngăn chặn file giả

### **🚀 ĐỂ CHẠY NGAY:**
1. **Double-click:** `RUN_XML_VALIDATOR.bat`
2. **HOẶC chạy trực tiếp:** `python xml_validator_gui.py`
3. **HOẶC tạo shortcut** trên Desktop

**Tool đã sẵn sàng sử dụng! Anh có thể chạy bất cứ lúc nào cần quét file XML!** 🎯✨
