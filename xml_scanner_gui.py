#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML SCANNER & CLASSIFIER - THUẾ FORTRESS SYNC
Tool GUI đẹp, hiện đại để quét và phân loại file XML theo doanh nghiệp
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
from collections import defaultdict

class ModernXMLScannerGUI:
    """GUI hiện đại cho XML Scanner & Classifier"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 XML SCANNER & CLASSIFIER - THUẾ FORTRESS SYNC")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a2e')
        
        # Biến lưu trữ
        self.scan_results = {}
        self.company_groups = defaultdict(list)
        self.tax_form_types = defaultdict(list)
        self.selected_fields = {
            'mst': True,
            'company_name': True,
            'tax_form_type': True,
            'period': True,
            'declaration_number': True
        }
        
        # Cấu hình style hiện đại
        self.setup_modern_styles()
        
        # Tạo giao diện
        self.create_modern_widgets()
        
        # Khởi tạo dữ liệu mẫu
        self.load_sample_data()
        
    def setup_modern_styles(self):
        """Thiết lập style hiện đại cho GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cấu hình style hiện đại
        style.configure('Modern.TFrame', 
                       background='#1a1a2e')
        
        style.configure('Card.TFrame', 
                       background='#16213e',
                       relief='flat',
                       borderwidth=2)
        
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'), 
                       foreground='#00d4ff',
                       background='#1a1a2e')
        
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 14), 
                       foreground='#ffffff',
                       background='#1a1a2e')
        
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 12, 'bold'), 
                       foreground='#00ff88',
                       background='#16213e')
        
        style.configure('Info.TLabel', 
                       font=('Segoe UI', 10), 
                       foreground='#cccccc',
                       background='#16213e')
        
        style.configure('Modern.TButton', 
                       font=('Segoe UI', 11, 'bold'),
                       background='#0f3460',
                       foreground='#ffffff',
                       relief='flat',
                       borderwidth=0)
        
        style.map('Modern.TButton',
                 background=[('active', '#533483')])
    
    def create_modern_widgets(self):
        """Tạo các widget hiện đại cho GUI"""
        # Title với gradient effect
        title_frame = ttk.Frame(self.root, style='Modern.TFrame')
        title_frame.pack(fill='x', pady=20)
        
        title_label = ttk.Label(title_frame, 
                               text="🚀 XML SCANNER & CLASSIFIER", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Tool thông minh quét và phân loại file XML theo doanh nghiệp", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=5)
        
        # Main Container với modern layout
        main_container = ttk.Frame(self.root, style='Modern.TFrame')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left Panel - Control & Configuration
        left_panel = self.create_left_panel(main_container)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        # Right Panel - Results & Dashboard
        right_panel = self.create_right_panel(main_container)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Status bar hiện đại
        self.create_modern_status_bar()
        
        # Progress bar với animation
        self.create_progress_section()
    
    def create_left_panel(self, parent):
        """Tạo panel trái - Control & Configuration"""
        left_frame = ttk.LabelFrame(parent, text="🎛️ ĐIỀU KHIỂN & CẤU HÌNH", 
                                   padding=15, style='Card.TFrame')
        
        # Scan Control Section
        scan_frame = ttk.LabelFrame(left_frame, text="🔍 QUÉT & PHÂN LOẠI", 
                                   padding=10, style='Card.TFrame')
        scan_frame.pack(fill='x', pady=(0, 15))
        
        # Scan buttons với modern design
        btn_frame = ttk.Frame(scan_frame)
        btn_frame.pack(fill='x', pady=5)
        
        scan_btn = ttk.Button(btn_frame, text="🚀 QUÉT THÔNG MINH", 
                             command=self.start_smart_scan, style='Modern.TButton')
        scan_btn.pack(fill='x', pady=5)
        
        folder_btn = ttk.Button(btn_frame, text="📁 CHỌN THƯ MỤC", 
                               command=self.select_folder, style='Modern.TButton')
        folder_btn.pack(fill='x', pady=5)
        
        clear_btn = ttk.Button(btn_frame, text="🗑️ XÓA KẾT QUẢ", 
                              command=self.clear_results, style='Modern.TButton')
        clear_btn.pack(fill='x', pady=5)
        
        # Field Selection Section
        fields_frame = ttk.LabelFrame(left_frame, text="⚙️ CHỌN TRƯỜNG ĐỊNH DANH", 
                                     padding=10, style='Card.TFrame')
        fields_frame.pack(fill='x', pady=(0, 15))
        
        # Checkboxes cho các trường
        self.mst_var = tk.BooleanVar(value=True)
        self.company_var = tk.BooleanVar(value=True)
        self.form_type_var = tk.BooleanVar(value=True)
        self.period_var = tk.BooleanVar(value=True)
        self.declaration_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(fields_frame, text="🏢 MST (Mã số thuế)", 
                       variable=self.mst_var, style='Info.TLabel').pack(anchor='w', pady=2)
        ttk.Checkbutton(fields_frame, text="🏭 Tên doanh nghiệp", 
                       variable=self.company_var, style='Info.TLabel').pack(anchor='w', pady=2)
        ttk.Checkbutton(fields_frame, text="📋 Loại tờ khai", 
                       variable=self.form_type_var, style='Info.TLabel').pack(anchor='w', pady=2)
        ttk.Checkbutton(fields_frame, text="📅 Kỳ khai", 
                       variable=self.period_var, style='Info.TLabel').pack(anchor='w', pady=2)
        ttk.Checkbutton(fields_frame, text="🔢 Số tờ khai", 
                       variable=self.declaration_var, style='Info.TLabel').pack(anchor='w', pady=2)
        
        # Export Section
        export_frame = ttk.LabelFrame(left_frame, text="📤 XUẤT DỮ LIỆU", 
                                     padding=10, style='Card.TFrame')
        export_frame.pack(fill='x', pady=(0, 15))
        
        export_btn = ttk.Button(export_frame, text="📊 XUẤT BÁO CÁO", 
                               command=self.export_report, style='Modern.TButton')
        export_btn.pack(fill='x', pady=5)
        
        return left_frame
    
    def create_right_panel(self, parent):
        """Tạo panel phải - Results & Dashboard"""
        right_frame = ttk.Frame(parent, style='Modern.TFrame')
        
        # Dashboard Header
        dashboard_header = ttk.LabelFrame(right_frame, text="📊 DASHBOARD TỔNG QUAN", 
                                        padding=15, style='Card.TFrame')
        dashboard_header.pack(fill='x', pady=(0, 15))
        
        # Statistics cards
        stats_frame = ttk.Frame(dashboard_header)
        stats_frame.pack(fill='x')
        
        self.total_files_label = ttk.Label(stats_frame, text="📁 Tổng file: 0", 
                                          style='Header.TLabel')
        self.total_files_label.pack(side='left', padx=10)
        
        self.total_companies_label = ttk.Label(stats_frame, text="🏢 Doanh nghiệp: 0", 
                                              style='Header.TLabel')
        self.total_companies_label.pack(side='left', padx=10)
        
        self.total_forms_label = ttk.Label(stats_frame, text="📋 Loại tờ khai: 0", 
                                          style='Header.TLabel')
        self.total_forms_label.pack(side='left', padx=10)
        
        # Results Display
        results_frame = ttk.LabelFrame(right_frame, text="🎯 KẾT QUẢ PHÂN LOẠI", 
                                      padding=15, style='Card.TFrame')
        results_frame.pack(fill='both', expand=True)
        
        # Notebook cho tabbed interface
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Tab 1: Phân loại theo doanh nghiệp
        self.companies_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.companies_tab, text="🏢 THEO DOANH NGHIỆP")
        
        # Companies treeview
        self.companies_tree = ttk.Treeview(self.companies_tab, columns=('MST', 'Tên', 'Số file', 'Loại tờ khai'), 
                                          show='tree headings', height=15)
        self.companies_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 2: Phân loại theo loại tờ khai
        self.forms_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.forms_tab, text="📋 THEO LOẠI TỜ KHAI")
        
        # Forms treeview
        self.forms_tree = ttk.Treeview(self.forms_tab, columns=('Loại', 'Số lượng', 'Doanh nghiệp'), 
                                      show='tree headings', height=15)
        self.forms_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 3: Chi tiết file
        self.files_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.files_tab, text="📁 CHI TIẾT FILE")
        
        # Files listbox
        self.files_listbox = tk.Listbox(self.files_tab, bg='#16213e', fg='#ffffff', 
                                       selectmode='extended', height=15)
        self.files_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        return right_frame
    
    def create_modern_status_bar(self):
        """Tạo status bar hiện đại"""
        status_frame = ttk.Frame(self.root, style='Card.TFrame')
        status_frame.pack(side='bottom', fill='x', padx=20, pady=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("🚀 Sẵn sàng quét và phân loại file XML...")
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                style='Info.TLabel')
        status_label.pack(side='left', padx=10, pady=5)
        
        # Time display
        self.time_var = tk.StringVar()
        self.time_var.set(datetime.now().strftime("%H:%M:%S"))
        time_label = ttk.Label(status_frame, textvariable=self.time_var, 
                              style='Info.TLabel')
        time_label.pack(side='right', padx=10, pady=5)
        
        # Update time
        self.update_time()
    
    def create_progress_section(self):
        """Tạo section progress với animation"""
        progress_frame = ttk.Frame(self.root, style='Modern.TFrame')
        progress_frame.pack(side='bottom', fill='x', padx=20, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill='x')
        
        self.progress_label = ttk.Label(progress_frame, text="0%", 
                                       style='Info.TLabel')
        self.progress_label.pack(pady=2)
    
    def update_time(self):
        """Cập nhật thời gian"""
        self.time_var.set(datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)
    
    def load_sample_data(self):
        """Load dữ liệu mẫu để demo"""
        # Dữ liệu mẫu cho demo
        sample_data = {
            'companies': [
                {'mst': '0123456789', 'name': 'Cty Tiến Bình Yến', 'files': 5, 'forms': ['Thông báo thuế A', 'Tờ khai thuế']},
                {'mst': '0987654321', 'name': 'Cty ABC', 'files': 3, 'forms': ['Tờ khai thuế', 'Báo cáo thuế']},
                {'mst': '1122334455', 'name': 'Cty XYZ', 'files': 2, 'forms': ['Thông báo thuế A']}
            ],
            'forms': [
                {'type': 'Thông báo thuế A', 'count': 2, 'companies': ['Cty Tiến Bình Yến', 'Cty XYZ']},
                {'type': 'Tờ khai thuế', 'count': 2, 'companies': ['Cty Tiến Bình Yến', 'Cty ABC']},
                {'type': 'Báo cáo thuế', 'count': 1, 'companies': ['Cty ABC']}
            ]
        }
        
        self.update_dashboard(sample_data)
    
    def update_dashboard(self, data):
        """Cập nhật dashboard với dữ liệu"""
        # Update statistics
        total_files = sum(company['files'] for company in data['companies'])
        total_companies = len(data['companies'])
        total_forms = len(data['forms'])
        
        self.total_files_label.config(text=f"📁 Tổng file: {total_files}")
        self.total_companies_label.config(text=f"🏢 Doanh nghiệp: {total_companies}")
        self.total_forms_label.config(text=f"📋 Loại tờ khai: {total_forms}")
        
        # Update companies tree
        self.companies_tree.delete(*self.companies_tree.get_children())
        for company in data['companies']:
            self.companies_tree.insert('', 'end', text=company['name'], 
                                     values=(company['mst'], company['name'], 
                                            company['files'], ', '.join(company['forms'])))
        
        # Update forms tree
        self.forms_tree.delete(*self.forms_tree.get_children())
        for form in data['forms']:
            self.forms_tree.insert('', 'end', text=form['type'], 
                                 values=(form['type'], form['count'], 
                                        ', '.join(form['companies'])))
    
    def select_folder(self):
        """Chọn thư mục để quét"""
        folder = filedialog.askdirectory(title="Chọn thư mục chứa file XML")
        if folder:
            self.status_var.set(f"📁 Đã chọn thư mục: {os.path.basename(folder)}")
            self.scan_folder = folder
    
    def start_smart_scan(self):
        """Bắt đầu quét thông minh"""
        if not hasattr(self, 'scan_folder'):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thư mục để quét trước!")
            return
        
        # Start scanning in separate thread
        scan_thread = threading.Thread(target=self._smart_scan_files, daemon=True)
        scan_thread.start()
    
    def _smart_scan_files(self):
        """Quét file thông minh trong thread riêng"""
        try:
            self.root.after(0, lambda: self.status_var.set("🔍 Đang quét file XML..."))
            self.root.after(0, lambda: self.progress_var.set(0))
            
            # Scan XML files
            xml_files = list(Path(self.scan_folder).rglob("*.xml"))
            total_files = len(xml_files)
            
            if total_files == 0:
                self.root.after(0, lambda: messagebox.showinfo("Thông báo", "Không tìm thấy file XML nào!"))
                return
            
            # Process each file
            for i, xml_file in enumerate(xml_files):
                try:
                    # Update progress
                    progress = (i + 1) / total_files * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    self.root.after(0, lambda p=int(progress): self.progress_label.config(text=f"{p}%"))
                    
                    # Update status
                    self.root.after(0, lambda f=os.path.basename(xml_file): 
                                  self.status_var.set(f"🔍 Đang quét: {f}"))
                    
                    # Process file
                    file_info = self._process_xml_file(xml_file)
                    if file_info:
                        self._add_to_results(file_info)
                    
                except Exception as e:
                    print(f"Error processing {xml_file}: {e}")
            
            # Scan completed
            self.root.after(0, lambda: self._scan_completed())
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi quét: {e}"))
    
    def _process_xml_file(self, file_path):
        """Xử lý một file XML với logic cải tiến"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract basic info
            file_info = {
                'path': str(file_path),
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
            }
            
            # Cải tiến: Trích xuất thông tin với logic thông minh hơn
            all_tags = {}
            for elem in root.iter():
                tag = elem.tag.lower()
                text = elem.text.strip() if elem.text else ""
                
                # Lưu tất cả tag để phân tích
                if text:
                    all_tags[tag] = text
            
            # 1. Trích xuất MST - Logic cải tiến
            mst_candidates = []
            for tag, text in all_tags.items():
                if 'mst' in tag or 'masothue' in tag or 'taxcode' in tag:
                    mst_candidates.append(text)
                elif len(text) == 10 and text.isdigit():  # MST thường có 10 số
                    mst_candidates.append(text)
            
            if mst_candidates:
                file_info['mst'] = mst_candidates[0]
            
            # 2. Trích xuất tên doanh nghiệp - Logic cải tiến
            company_candidates = []
            for tag, text in all_tags.items():
                if any(keyword in tag for keyword in ['tennnt', 'tencty', 'tendoanhnghiep', 'companyname']):
                    company_candidates.append(text)
                elif any(keyword in text.lower() for keyword in ['công ty', 'cty', 'tnhh', 'jsc', 'co ltd']):
                    company_candidates.append(text)
            
            if company_candidates:
                file_info['company_name'] = company_candidates[0]
            
            # 3. Trích xuất loại tờ khai - Logic cải tiến
            form_type = self._detect_tax_form_type(all_tags, file_path.name)
            file_info['form_type'] = form_type
            
            # 4. Trích xuất kỳ khai - Logic cải tiến
            period_candidates = []
            for tag, text in all_tags.items():
                if any(keyword in tag for keyword in ['kykhai', 'kybaocao', 'period', 'thang', 'quy', 'nam']):
                    period_candidates.append(text)
                elif any(keyword in text.lower() for keyword in ['tháng', 'quý', 'năm', '2024', '2025']):
                    period_candidates.append(text)
            
            if period_candidates:
                file_info['period'] = period_candidates[0]
            
            # 5. Trích xuất số tờ khai - Logic cải tiến
            declaration_candidates = []
            for tag, text in all_tags.items():
                if any(keyword in tag for keyword in ['sotk', 'matkhai', 'declaration', 'sochungtu']):
                    declaration_candidates.append(text)
                elif text.startswith('ETAX') or text.startswith('HTKK'):  # Pattern phổ biến
                    declaration_candidates.append(text)
            
            if declaration_candidates:
                file_info['declaration_number'] = declaration_candidates[0]
            
            return file_info
            
        except Exception as e:
            print(f"Error processing XML {file_path}: {e}")
            return None
    
    def _detect_tax_form_type(self, all_tags, filename):
        """Phát hiện loại tờ khai thông minh"""
        try:
            # Phân tích filename trước
            filename_lower = filename.lower()
            
            # 1. Phân tích theo filename pattern
            if 'etax' in filename_lower:
                if '113' in filename_lower:
                    return "Tờ khai thuế GTGT (ETAX113)"
                elif '01' in filename_lower:
                    return "Tờ khai thuế TNDN (ETAX01)"
                elif '02' in filename_lower:
                    return "Tờ khai thuế TNCN (ETAX02)"
                else:
                    return "Tờ khai thuế (ETAX)"
            
            if 'htkk' in filename_lower:
                return "Tờ khai HTKK"
            
            if 'fake' in filename_lower:
                return "⚠️ FILE FAKE"
            
            # 2. Phân tích theo nội dung XML
            content_text = ' '.join(all_tags.values()).lower()
            
            # Tìm từ khóa trong nội dung
            if 'thông báo thuế' in content_text:
                return "Thông báo thuế"
            
            if 'tờ khai thuế' in content_text:
                if 'gtgt' in content_text or 'giá trị gia tăng' in content_text:
                    return "Tờ khai thuế GTGT"
                elif 'tndn' in content_text or 'thu nhập doanh nghiệp' in content_text:
                    return "Tờ khai thuế TNDN"
                elif 'tncn' in content_text or 'thu nhập cá nhân' in content_text:
                    return "Tờ khai thuế TNCN"
                else:
                    return "Tờ khai thuế"
            
            if 'báo cáo thuế' in content_text:
                return "Báo cáo thuế"
            
            if 'quyết toán thuế' in content_text:
                return "Quyết toán thuế"
            
            # 3. Phân tích theo tag cụ thể
            for tag, text in all_tags.items():
                tag_lower = tag.lower()
                text_lower = text.lower()
                
                if 'loaikhai' in tag_lower or 'loaitt' in tag_lower:
                    if text:
                        return f"Loại: {text}"
                
                if 'tenmau' in tag_lower or 'maukhai' in tag_lower:
                    if text:
                        return f"Mẫu: {text}"
                
                if 'kykhai' in tag_lower:
                    if text:
                        return f"Kỳ khai: {text}"
            
            # 4. Phân tích theo cấu trúc XML
            if len(all_tags) < 10:
                return "XML đơn giản"
            elif len(all_tags) < 50:
                return "XML trung bình"
            else:
                return "XML phức tạp"
                
        except Exception as e:
            print(f"Error detecting form type: {e}")
            return "Unknown"
    
    def _add_to_results(self, file_info):
        """Thêm file vào kết quả phân loại"""
        # Group by MST
        mst = file_info.get('mst', 'Unknown')
        if mst not in self.company_groups:
            self.company_groups[mst] = []
        self.company_groups[mst].append(file_info)
        
        # Group by form type
        form_type = file_info.get('form_type', 'Unknown')
        if form_type not in self.tax_form_types:
            self.tax_form_types[form_type] = []
        self.tax_form_types[form_type].append(file_info)
    
    def _scan_completed(self):
        """Hoàn thành quét"""
        try:
            # Update dashboard
            self._update_results_display()
            
            # Update status
            total_files = sum(len(files) for files in self.company_groups.values())
            self.status_var.set(f"✅ Hoàn thành quét {total_files} file XML")
            self.progress_var.set(100)
            self.progress_label.config(text="100%")
            
            # Show completion message
            messagebox.showinfo("Hoàn thành", 
                              f"Quét hoàn thành!\nPhát hiện {len(self.company_groups)} doanh nghiệp\nTổng cộng {total_files} file XML")
                
        except Exception as e:
            print(f"Error in scan completion: {e}")
    
    def _update_results_display(self):
        """Cập nhật hiển thị kết quả"""
        # Update companies tab
        self.companies_tree.delete(*self.companies_tree.get_children())
        for mst, files in self.company_groups.items():
            company_name = files[0].get('company_name', 'Unknown') if files else 'Unknown'
            form_types = list(set(f.get('form_type', 'Unknown') for f in files))
            
            self.companies_tree.insert('', 'end', text=company_name, 
                                     values=(mst, company_name, len(files), ', '.join(form_types)))
        
        # Update forms tab
        self.forms_tree.delete(*self.forms_tree.get_children())
        for form_type, files in self.tax_form_types.items():
            companies = list(set(f.get('company_name', 'Unknown') for f in files))
            
            self.forms_tree.insert('', 'end', text=form_type, 
                                 values=(form_type, len(files), ', '.join(companies)))
        
        # Update files tab
        self.files_listbox.delete(0, tk.END)
        for mst, files in self.company_groups.items():
            for file_info in files:
                display_text = f"🏢 {file_info.get('company_name', 'Unknown')} | 📁 {file_info['name']} | 📋 {file_info.get('form_type', 'Unknown')}"
                self.files_listbox.insert(tk.END, display_text)
    
    def clear_results(self):
        """Xóa kết quả"""
        self.company_groups.clear()
        self.tax_form_types.clear()
        self._update_results_display()
        self.status_var.set("🗑️ Đã xóa tất cả kết quả")
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
    
    def export_report(self):
        """Xuất báo cáo"""
        if not self.company_groups:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất!")
            return
        
        try:
            # Create report data
            report_data = {
                'scan_time': datetime.now().isoformat(),
                'total_companies': len(self.company_groups),
                'total_files': sum(len(files) for files in self.company_groups.values()),
                'companies': dict(self.company_groups),
                'forms': dict(self.tax_form_types)
            }
            
            # Save report
            report_file = f"xml_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo: {report_file}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {e}")

def main():
    """Hàm main"""
    try:
        root = tk.Tk()
        app = ModernXMLScannerGUI(root)
        
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
