#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML VALIDATOR & SCANNER - THUẾ FORTRESS SYNC
Tool GUI để quét và validate file XML trước khi nạp vào kho Master
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import json
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import threading
import requests

class XMLValidatorGUI:
    """GUI chính cho XML Validator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 XML VALIDATOR - THUẾ FORTRESS SYNC")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # Cấu hình style
        self.setup_styles()
        
        # Biến lưu trữ
        self.selected_files = []
        self.baseline_hashes = {}
        self.scan_results = []
        
        # Khởi tạo baseline
        self.load_baseline()
        
        # Tạo giao diện
        self.create_widgets()
        
    def setup_styles(self):
        """Thiết lập style cho GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cấu hình style
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'), 
                       foreground='#00ff00',
                       background='#2b2b2b')
        
        style.configure('Header.TLabel', 
                       font=('Arial', 12, 'bold'), 
                       foreground='#ffffff',
                       background='#2b2b2b')
        
        style.configure('Info.TLabel', 
                       font=('Arial', 10), 
                       foreground='#cccccc',
                       background='#2b2b2b')
        
        style.configure('Success.TLabel', 
                       font=('Arial', 10, 'bold'), 
                       foreground='#00ff00',
                       background='#2b2b2b')
        
        style.configure('Warning.TLabel', 
                       font=('Arial', 10, 'bold'), 
                       foreground='#ffff00',
                       background='#2b2b2b')
        
        style.configure('Error.TLabel', 
                       font=('Arial', 10, 'bold'), 
                       foreground='#ff0000',
                       background='#2b2b2b')
    
    def load_baseline(self):
        """Load baseline hashes từ Master Node"""
        try:
            baseline_folder = Path("Cty Tiến Bình Yến")
            if baseline_folder.exists():
                for xml_file in baseline_folder.rglob("*.xml"):
                    file_hash = self._calculate_file_hash(xml_file)
                    if file_hash:
                        self.baseline_hashes[xml_file.name] = {
                            'hash': file_hash,
                            'path': str(xml_file),
                            'size': xml_file.stat().st_size,
                            'modified': xml_file.stat().st_mtime
                        }
                print(f"✅ Baseline loaded: {len(self.baseline_hashes)} files")
            else:
                print("⚠️ Baseline folder not found")
                
        except Exception as e:
            print(f"❌ Failed to load baseline: {e}")
    
    def _calculate_file_hash(self, file_path):
        """Tính hash MD5 của file"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception:
            return None
    
    def create_widgets(self):
        """Tạo các widget cho GUI"""
        # Title
        title_label = ttk.Label(self.root, 
                               text="🔒 XML VALIDATOR & SCANNER", 
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(self.root, 
                                  text="Tool quét và validate file XML trước khi nạp vào kho Master", 
                                  style='Info.TLabel')
        subtitle_label.pack(pady=5)
        
        # Main Frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left Panel - File Selection
        left_panel = ttk.LabelFrame(main_frame, text="📁 CHỌN FILE XML", padding=10)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # File selection buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="📂 Chọn File", 
                  command=self.select_files).pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="📁 Chọn Thư Mục", 
                  command=self.select_folder).pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="🗑️ Xóa Tất Cả", 
                  command=self.clear_files).pack(side='left')
        
        # File list
        file_frame = ttk.Frame(left_panel)
        file_frame.pack(fill='both', expand=True, pady=5)
        
        ttk.Label(file_frame, text="Danh sách file đã chọn:", 
                 style='Header.TLabel').pack(anchor='w')
        
        self.file_listbox = tk.Listbox(file_frame, bg='#3c3c3c', fg='#ffffff', 
                                      selectmode='extended', height=8)
        self.file_listbox.pack(fill='both', expand=True)
        
        # Scan button
        scan_btn = ttk.Button(left_panel, text="🔍 QUÉT & VALIDATE", 
                             command=self.start_scan, style='Accent.TButton')
        scan_btn.pack(fill='x', pady=10)
        
        # Right Panel - Results
        right_panel = ttk.LabelFrame(main_frame, text="📊 KẾT QUẢ QUÉT", padding=10)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Results display
        results_frame = ttk.Frame(right_panel)
        results_frame.pack(fill='both', expand=True)
        
        ttk.Label(results_frame, text="Kết quả kiểm tra:", 
                 style='Header.TLabel').pack(anchor='w')
        
        self.results_text = scrolledtext.ScrolledText(results_frame, 
                                                    bg='#3c3c3c', fg='#ffffff',
                                                    height=15, width=50)
        self.results_text.pack(fill='both', expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng quét file XML...")
        
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief='sunken', anchor='w', style='Info.TLabel')
        status_bar.pack(side='bottom', fill='x')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(side='bottom', fill='x', padx=20, pady=5)
    
    def select_files(self):
        """Chọn nhiều file XML"""
        try:
            files = filedialog.askopenfilenames(
                title="Chọn file XML để quét",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
            )
            
            if files:
                for file_path in files:
                    if file_path not in self.selected_files:
                        self.selected_files.append(file_path)
                        self.file_listbox.insert(tk.END, os.path.basename(file_path))
                
                self.status_var.set(f"Đã chọn {len(self.selected_files)} file")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chọn file: {e}")
    
    def select_folder(self):
        """Chọn thư mục chứa file XML"""
        try:
            folder = filedialog.askdirectory(title="Chọn thư mục chứa file XML")
            
            if folder:
                xml_files = list(Path(folder).rglob("*.xml"))
                
                for xml_file in xml_files:
                    file_path = str(xml_file)
                    if file_path not in self.selected_files:
                        self.selected_files.append(file_path)
                        self.file_listbox.insert(tk.END, xml_file.name)
                
                self.status_var.set(f"Đã chọn {len(self.selected_files)} file từ thư mục")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chọn thư mục: {e}")
    
    def clear_files(self):
        """Xóa tất cả file đã chọn"""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.status_var.set("Đã xóa tất cả file")
    
    def start_scan(self):
        """Bắt đầu quét và validate file"""
        if not self.selected_files:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file XML để quét!")
            return
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.scan_results.clear()
        
        # Start scanning in separate thread
        scan_thread = threading.Thread(target=self._scan_files, daemon=True)
        scan_thread.start()
    
    def _scan_files(self):
        """Quét file trong thread riêng"""
        try:
            total_files = len(self.selected_files)
            self.progress_var.set(0)
            
            for i, file_path in enumerate(self.selected_files):
                try:
                    # Update progress
                    progress = (i + 1) / total_files * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    
                    # Update status
                    self.root.after(0, lambda f=os.path.basename(file_path): 
                                  self.status_var.set(f"Đang quét: {f}"))
                    
                    # Scan file
                    result = self._scan_single_file(file_path)
                    self.scan_results.append(result)
                    
                    # Display result
                    self.root.after(0, lambda r=result: self._display_result(r))
                    
                except Exception as e:
                    error_result = {
                        'file_path': file_path,
                        'file_name': os.path.basename(file_path),
                        'status': 'ERROR',
                        'message': f"Lỗi khi quét file: {e}",
                        'details': {}
                    }
                    self.scan_results.append(error_result)
                    self.root.after(0, lambda r=error_result: self._display_result(r))
            
            # Scan completed
            self.root.after(0, lambda: self._scan_completed())
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi quét: {e}"))
    
    def _scan_single_file(self, file_path):
        """Quét một file XML cụ thể"""
        try:
            file_name = os.path.basename(file_path)
            file_path_obj = Path(file_path)
            
            result = {
                'file_path': file_path,
                'file_name': file_name,
                'status': 'UNKNOWN',
                'message': '',
                'details': {}
            }
            
            # Kiểm tra file tồn tại
            if not file_path_obj.exists():
                result['status'] = 'ERROR'
                result['message'] = 'File không tồn tại'
                return result
            
            # Kiểm tra kích thước file
            file_size = file_path_obj.stat().st_size
            result['details']['file_size'] = file_size
            
            if file_size == 0:
                result['status'] = 'ERROR'
                result['message'] = 'File rỗng'
                return result
            
            # Tính hash MD5
            file_hash = self._calculate_file_hash(file_path_obj)
            result['details']['file_hash'] = file_hash
            
            # Kiểm tra với baseline
            if file_name in self.baseline_hashes:
                baseline_info = self.baseline_hashes[file_name]
                
                if file_hash == baseline_info['hash']:
                    result['status'] = 'ORIGINAL'
                    result['message'] = 'File gốc - Khớp với baseline'
                    result['details']['baseline_match'] = True
                else:
                    result['status'] = 'FAKE'
                    result['message'] = 'File fake - Hash không khớp với baseline'
                    result['details']['baseline_match'] = False
                    result['details']['baseline_hash'] = baseline_info['hash']
            else:
                result['status'] = 'NEW'
                result['message'] = 'File mới - Không có trong baseline'
                result['details']['baseline_match'] = False
            
            # Validate XML structure
            xml_validation = self._validate_xml_structure(file_path_obj)
            result['details']['xml_validation'] = xml_validation
            
            # Kiểm tra nội dung XML
            content_check = self._check_xml_content(file_path_obj)
            result['details']['content_check'] = content_check
            
            return result
            
        except Exception as e:
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'status': 'ERROR',
                'message': f'Lỗi khi quét: {e}',
                'details': {}
            }
    
    def _validate_xml_structure(self, file_path):
        """Validate cấu trúc XML"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Kiểm tra namespace
            namespaces = root.nsmap if hasattr(root, 'nsmap') else {}
            
            # Kiểm tra các element chính
            main_elements = []
            for child in root:
                main_elements.append(child.tag)
            
            return {
                'valid': True,
                'root_tag': root.tag,
                'namespaces': namespaces,
                'main_elements': main_elements,
                'element_count': len(main_elements)
            }
            
        except ET.ParseError as e:
            return {
                'valid': False,
                'error': f'XML parse error: {e}'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {e}'
            }
    
    def _check_xml_content(self, file_path):
        """Kiểm tra nội dung XML"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            content_info = {
                'has_tax_info': False,
                'has_company_info': False,
                'has_declaration_info': False,
                'content_summary': {}
            }
            
            # Kiểm tra thông tin thuế
            for elem in root.iter():
                tag = elem.tag.lower()
                text = elem.text.strip() if elem.text else ""
                
                if 'thue' in tag or 'tax' in tag:
                    content_info['has_tax_info'] = True
                
                if 'congty' in tag or 'company' in tag:
                    content_info['has_company_info'] = True
                
                if 'khai' in tag or 'declaration' in tag:
                    content_info['has_declaration_info'] = True
                
                # Lưu thông tin quan trọng
                if text and len(text) > 5:
                    content_info['content_summary'][tag] = text[:100] + "..." if len(text) > 100 else text
            
            return content_info
            
        except Exception as e:
            return {
                'error': f'Content check error: {e}'
            }
    
    def _display_result(self, result):
        """Hiển thị kết quả quét"""
        try:
            # Xác định màu sắc theo status
            if result['status'] == 'ORIGINAL':
                status_icon = "✅"
                status_color = "green"
            elif result['status'] == 'NEW':
                status_icon = "🆕"
                status_color = "blue"
            elif result['status'] == 'FAKE':
                status_icon = "🚨"
                status_color = "red"
            else:
                status_icon = "❌"
                status_color = "orange"
            
            # Tạo text hiển thị
            display_text = f"{status_icon} {result['file_name']}\n"
            display_text += f"   Trạng thái: {result['status']}\n"
            display_text += f"   Thông báo: {result['message']}\n"
            
            # Thêm chi tiết
            if 'details' in result:
                details = result['details']
                if 'file_size' in details:
                    display_text += f"   Kích thước: {details['file_size']:,} bytes\n"
                if 'xml_validation' in details:
                    xml_val = details['xml_validation']
                    if xml_val.get('valid'):
                        display_text += f"   XML: ✅ Hợp lệ ({xml_val.get('element_count', 0)} elements)\n"
                    else:
                        display_text += f"   XML: ❌ Không hợp lệ - {xml_val.get('error', 'Unknown error')}\n"
                if 'content_check' in details:
                    content = details['content_check']
                    if 'has_tax_info' in content:
                        display_text += f"   Nội dung: {'✅' if content['has_tax_info'] else '❌'} Thông tin thuế\n"
                        display_text += f"            {'✅' if content.get('has_company_info') else '❌'} Thông tin công ty\n"
                        display_text += f"            {'✅' if content.get('has_declaration_info') else '❌'} Thông tin khai thuế\n"
            
            display_text += "-" * 50 + "\n\n"
            
            # Thêm vào text widget
            self.results_text.insert(tk.END, display_text)
            self.results_text.see(tk.END)
            
        except Exception as e:
            print(f"Error displaying result: {e}")
    
    def _scan_completed(self):
        """Hoàn thành quét"""
        try:
            # Tính thống kê
            total_files = len(self.scan_results)
            original_count = sum(1 for r in self.scan_results if r['status'] == 'ORIGINAL')
            new_count = sum(1 for r in self.scan_results if r['status'] == 'NEW')
            fake_count = sum(1 for r in self.scan_results if r['status'] == 'FAKE')
            error_count = sum(1 for r in self.scan_results if r['status'] == 'ERROR')
            
            # Hiển thị tổng kết
            summary = f"\n{'='*60}\n"
            summary += f"📊 TỔNG KẾT QUÉT\n"
            summary += f"{'='*60}\n"
            summary += f"✅ File gốc: {original_count}/{total_files}\n"
            summary += f"🆕 File mới: {new_count}/{total_files}\n"
            summary += f"🚨 File fake: {fake_count}/{total_files}\n"
            summary += f"❌ File lỗi: {error_count}/{total_files}\n"
            summary += f"{'='*60}\n"
            
            if fake_count > 0:
                summary += f"⚠️ CẢNH BÁO: Phát hiện {fake_count} file fake!\n"
                summary += f"   Không nên nạp vào kho Master!\n"
            else:
                summary += f"✅ Tất cả file đều an toàn!\n"
                summary += f"   Có thể nạp vào kho Master.\n"
            
            summary += f"{'='*60}\n"
            
            self.results_text.insert(tk.END, summary)
            self.results_text.see(tk.END)
            
            # Update status
            self.status_var.set(f"Hoàn thành quét {total_files} file")
            self.progress_var.set(100)
            
            # Show completion message
            if fake_count > 0:
                messagebox.showwarning("Cảnh báo", 
                                     f"Phát hiện {fake_count} file fake!\nKhông nên nạp vào kho Master!")
            else:
                messagebox.showinfo("Hoàn thành", 
                                  f"Quét hoàn thành!\nTất cả {total_files} file đều an toàn.")
                
        except Exception as e:
            print(f"Error in scan completion: {e}")

def main():
    """Hàm main"""
    try:
        root = tk.Tk()
        app = XMLValidatorGUI(root)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        root.mainloop()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        messagebox.showerror("Lỗi nghiêm trọng", f"Không thể khởi động ứng dụng: {e}")

if __name__ == "__main__":
    main()
