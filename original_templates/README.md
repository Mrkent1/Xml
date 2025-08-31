# 📁 ORIGINAL_TEMPLATES - Thư mục XML gốc

## 🎯 **MỤC ĐÍCH:**

**Thư mục này dành để anh upload file XML gốc từ máy anh!**

## 🚀 **CÁCH SỬ DỤNG:**

### **1. Upload file XML gốc:**
- **Copy file XML gốc** từ máy anh vào thư mục này
- **Đặt tên rõ ràng** (ví dụ: `Quy1_2025.xml`, `Quy2_2025.xml`)
- **Đảm bảo file có kỳ khai thuế khác nhau**

### **2. Tự động build:**
- **GitHub Actions sẽ tự động phát hiện** khi anh upload file XML
- **Tự động copy** file XML vào thư mục `templates/`
- **Tự động build EXE** với file XML gốc mới

### **3. Kết quả:**
- **EXE file** sẽ bao gồm tất cả file XML gốc
- **Không cần thao tác thủ công** nào khác

## 📋 **CẤU TRÚC THƯ MỤC:**

```
original_templates/
├── README.md
├── Quy1_2025.xml          # File XML Quý 1/2025
├── Quy2_2025.xml          # File XML Quý 2/2025
├── Quy3_2025.xml          # File XML Quý 3/2025
├── Quy4_2025.xml          # File XML Quý 4/2025
└── Nam2024.xml            # File XML Năm 2024
```

## ⚡ **TÍNH NĂNG TỰ ĐỘNG:**

- ✅ **Auto-detect:** Tự động nhận diện file XML mới
- ✅ **Auto-copy:** Tự động copy vào templates
- ✅ **Auto-build:** Tự động build EXE
- ✅ **Auto-notify:** Tự động thông báo kết quả

## 🔧 **WORKFLOW HOẠT ĐỘNG:**

1. **Anh upload file XML** vào `original_templates/`
2. **GitHub Actions phát hiện** thay đổi
3. **Tự động copy** file vào `templates/`
4. **Tự động build** EXE với PyInstaller
5. **Tự động upload** artifact và tạo release

## 📱 **THÔNG BÁO:**

**Kết quả build sẽ được gửi tự động về nhóm Telegram của anh!**

---

**🎯 Chỉ cần upload file XML gốc vào đây, mọi thứ sẽ tự động!** 🚀✨
