#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMPLE XML SCANNER - THUẾ FORTRESS SYNC
Tool đơn giản để quét file XML - Có gì quét nấy
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

class SimpleXMLScanner:
    """Tool XML Scanner đơn giản"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📁 SIMPLE XML SCANNER")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Biến lưu trữ
        self.scan_results = []
        
        # Tạo giao diện đơn giản
        self.create_simple_widgets()
        
    def create_simple_widgets(self):
        """Tạo giao diện đơn giản"""
        # Title
        title_label = tk.Label(self.root, text="📁 SIMPLE XML SCANNER", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # Buttons đơn giản
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        scan_btn = tk.Button(button_frame, text="🔍 QUÉT FILE XML", 
                            command=self.scan_files, bg='#4CAF50', fg='white', 
                            font=('Arial', 12), padx=20, pady=10)
        scan_btn.pack(side='left', padx=10)
        
        folder_btn = tk.Button(button_frame, text="📁 CHỌN THƯ MỤC", 
                              command=self.select_folder, bg='#2196F3', fg='white', 
                              font=('Arial', 12), padx=20, pady=10)
        folder_btn.pack(side='left', padx=10)
        
        clear_btn = tk.Button(button_frame, text="🗑️ XÓA KẾT QUẢ", 
                             command=self.clear_results, bg='#f44336', fg='white', 
                             font=('Arial', 12), padx=20, pady=10)
        clear_btn.pack(side='left', padx=10)
        
        # Kết quả đơn giản
        result_frame = tk.Frame(self.root, bg='#f0f0f0')
        result_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Listbox đơn giản
        self.result_listbox = tk.Listbox(result_frame, bg='white', fg='black', 
                                        font=('Consolas', 10), selectmode='extended')
        self.result_listbox.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(result_frame, orient='vertical', command=self.result_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.result_listbox.config(yscrollcommand=scrollbar.set)
        
        # Status đơn giản
        self.status_var = tk.StringVar()
        self.status_var.set("🚀 Sẵn sàng quét file XML...")
        
        status_label = tk.Label(self.root, textvariable=self.status_var, 
                               bg='#f0f0f0', font=('Arial', 10))
        status_label.pack(pady=5)
        
        # Thư mục hiện tại
        self.current_folder = None
    
    def select_folder(self):
        """Chọn thư mục đơn giản"""
        folder = filedialog.askdirectory(title="Chọn thư mục chứa file XML")
        if folder:
            self.current_folder = folder
            self.status_var.set(f"📁 Đã chọn: {os.path.basename(folder)}")
    
    def scan_files(self):
        """Quét file đơn giản"""
        if not self.current_folder:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thư mục trước!")
            return
        
        try:
            self.status_var.set("🔍 Đang quét...")
            self.result_listbox.delete(0, tk.END)
            
            # Quét tất cả file XML
            xml_files = list(Path(self.current_folder).rglob("*.xml"))
            
            if not xml_files:
                self.result_listbox.insert(tk.END, "❌ Không tìm thấy file XML nào!")
                self.status_var.set("❌ Không có file XML")
                return
            
            # Xử lý từng file đơn giản
            for xml_file in xml_files:
                file_info = self._process_file_simple(xml_file)
                if file_info:
                    self.result_listbox.insert(tk.END, file_info)
            
            # Hoàn thành
            total_files = len(xml_files)
            self.status_var.set(f"✅ Hoàn thành: {total_files} file XML")
            
            # Thông báo kết quả
            messagebox.showinfo("Hoàn thành", f"Quét xong {total_files} file XML!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi quét: {e}")
            self.status_var.set("❌ Có lỗi xảy ra")
    
    def _process_file_simple(self, file_path):
        """Xử lý file đơn giản - Có gì hiển thị nấy"""
        try:
            # Thông tin cơ bản
            file_name = file_path.name
            file_size = file_path.stat().st_size
            file_date = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            
            # Thông tin cơ bản
            basic_info = f"📁 {file_name} | 📏 {file_size:,} bytes | 📅 {file_date}"
            
            # Thử đọc XML đơn giản
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Đếm số tag
                tag_count = len(list(root.iter()))
                
                # Tìm một số tag cơ bản
                found_tags = []
                for elem in root.iter():
                    tag = elem.tag
                    if elem.text and elem.text.strip():
                        # Chỉ lấy 5 tag đầu tiên để không quá dài
                        if len(found_tags) < 5:
                            found_tags.append(f"{tag}: {elem.text.strip()}")
                
                # Kết quả đơn giản
                xml_info = f" | 🏷️ {tag_count} tags | 📋 {', '.join(found_tags[:3])}"
                
                return basic_info + xml_info
                
            except ET.ParseError:
                # File XML lỗi
                return basic_info + " | ❌ XML lỗi"
                
        except Exception as e:
            return f"❌ Lỗi xử lý {file_path.name}: {e}"
    
    def clear_results(self):
        """Xóa kết quả đơn giản"""
        self.result_listbox.delete(0, tk.END)
        self.status_var.set("🗑️ Đã xóa kết quả")
        self.current_folder = None

def main():
    """Hàm main đơn giản"""
    root = tk.Tk()
    app = SimpleXMLScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
