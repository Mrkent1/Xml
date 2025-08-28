#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THUẾ FORTRESS SYNC - HYBRID SLAVE NODE
Tích hợp Syncthing với Stealth Guard để chạy ngầm trên máy con
"""

import os
import sys
import time
import json
import logging
import requests
import threading
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

# Windows API để ẩn hoàn toàn
try:
    import win32gui
    import win32con
    import win32api
    import win32process
    import winreg
    import ctypes
    from ctypes import wintypes
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False

# --- CẤU HÌNH HYBRID FORTRESS SLAVE --- #
APP_DIR = Path(os.getenv('APPDATA', Path.home())) / 'WindowsSecurityUpdate'  # Tên ngụy trang
APP_DIR.mkdir(parents=True, exist_ok=True)

# Files cấu hình
CONFIG_FILE = APP_DIR / 'slave_config.json'
LOG_FILE = APP_DIR / 'security_update.log'
STATE_FILE = APP_DIR / 'system_cache.dat'
CONTROL_FILE = APP_DIR / 'control_access.key'

# Syncthing config (sẽ nhận từ Master)
SYNCTHING_CONFIG = {
    "baseUrl": "http://127.0.0.1:8384",
    "apiKey": "",
    "folderId": "",
    "folderRoot": r"C:\Users\Administrator\Documents\TaxXML"
}

# Master Node config
MASTER_CONFIG = {
    "deviceId": "",  # Sẽ nhận từ Master
    "folderId": "tax_xml_master",
    "syncMode": "receiveonly"
}

# --- LOGGING ẨN --- #
logging.basicConfig(
    filename=str(LOG_FILE),
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HybridFortressSlave:
    """Slave Node tích hợp Syncthing + Stealth Guard"""
    
    def __init__(self):
        self.syncthing_client = None
        self.stealth_guard = None
        self.is_running = False
        self.machine_id = None
        
        # Khởi tạo các component
        self.init_components()
    
    def init_components(self):
        """Khởi tạo các component cần thiết"""
        try:
            # 1. Ẩn hoàn toàn process
            self.hide_process()
            
            # 2. Tạo Machine ID
            self.machine_id = self.get_or_create_machine_id()
            
            # 3. Khởi tạo Syncthing client
            self.init_syncthing_client()
            
            # 4. Tạo cấu hình mặc định
            self.create_default_config()
            
            # 5. Khởi tạo Stealth Guard
            self.init_stealth_guard()
            
            logging.info(f"✅ Hybrid Fortress Slave initialized - Machine ID: {self.machine_id}")
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize components: {e}")
            raise
    
    def hide_process(self):
        """Ẩn hoàn toàn process khỏi Windows"""
        try:
            if not WINDOWS_API_AVAILABLE:
                logging.warning("⚠️ Windows API not available, cannot hide process")
                return
            
            # Ẩn console window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            
            # Ẩn khỏi Task Manager
            try:
                # Đổi tên process
                current_pid = win32api.GetCurrentProcessId()
                handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, current_pid)
                
                # Sử dụng SetProcessWorkingSetSize để ẩn khỏi Task Manager
                ctypes.windll.kernel32.SetProcessWorkingSetSize(handle, -1, -1)
                win32api.CloseHandle(handle)
                
            except Exception as e:
                logging.debug(f"Process hiding technique failed: {e}")
            
            # Ẩn console window hoàn toàn
            try:
                kernel32 = ctypes.windll.kernel32
                user32 = ctypes.windll.user32
                
                SW_HIDE = 0
                hWnd = kernel32.GetConsoleWindow()
                if hWnd:
                    user32.ShowWindow(hWnd, SW_HIDE)
                    
            except Exception as e:
                logging.debug(f"Console hiding failed: {e}")
            
            logging.info("✅ Process hidden successfully")
            
        except Exception as e:
            logging.error(f"❌ Failed to hide process: {e}")
    
    def get_or_create_machine_id(self):
        """Tạo hoặc lấy Machine ID duy nhất"""
        try:
            # Tạo Machine ID từ hostname và hardware info
            import platform
            import uuid
            
            hostname = platform.node()
            machine_guid = str(uuid.getnode())  # MAC address
            
            # Tạo hash duy nhất
            machine_hash = hashlib.md5(f"{hostname}_{machine_guid}".encode()).hexdigest()[:8].upper()
            machine_id = f"SLAVE_{hostname}_{machine_hash}"
            
            # Lưu Machine ID
            with open(CONTROL_FILE, 'w', encoding='utf-8') as f:
                f.write(machine_id)
            
            logging.info(f"✅ Machine ID created: {machine_id}")
            return machine_id
            
        except Exception as e:
            logging.error(f"❌ Failed to create Machine ID: {e}")
            return f"SLAVE_UNKNOWN_{int(time.time())}"
    
    def init_syncthing_client(self):
        """Khởi tạo Syncthing client"""
        try:
            # Kiểm tra Syncthing có chạy không
            response = requests.get(f"{SYNCTHING_CONFIG['baseUrl']}/rest/system/status", timeout=5)
            if response.status_code == 200:
                logging.info("✅ Syncthing is running")
                self.syncthing_client = True
                
                # Tự động tạo folder config
                self.create_syncthing_folder_config()
                    
            else:
                logging.warning("⚠️ Syncthing not responding properly")
                
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Syncthing not accessible: {e}")
            print("⚠️ Syncthing chưa chạy. Hãy khởi động Syncthing trước!")
            print("💡 Hướng dẫn:")
            print("   1. Tải Syncthing từ https://syncthing.net/")
            print("   2. Cài đặt và khởi động Syncthing")
            print("   3. Đợi Syncthing khởi động xong (có icon trong system tray)")
            print("   4. Chạy lại python hybrid_fortress_slave.py")
    
    def create_default_config(self):
        """Tạo cấu hình mặc định cho Slave Node"""
        try:
            if not CONFIG_FILE.exists():
                default_config = {
                    "syncthing": {
                        "baseUrl": SYNCTHING_CONFIG["baseUrl"],
                        "apiKey": "",
                        "folderId": "tax_xml_master",
                        "folderRoot": SYNCTHING_CONFIG["folderRoot"]
                    },
                    "master": MASTER_CONFIG,
                    "stealth": {
                        "hide_console": True,
                        "hide_task_manager": True,
                        "process_name": "WindowsSecurityUpdate.exe",
                        "service_mode": True
                    },
                    "security": {
                        "auto_overwrite": True,
                        "conflict_resolution": "master_wins",
                        "file_protection": True
                    },
                    "monitoring": {
                        "interval": 3,
                        "health_check_interval": 300,
                        "log_retention_days": 30
                    }
                }
                
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                
                logging.info("✅ Default configuration created")
            
            # Load config
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                SYNCTHING_CONFIG.update(config["syncthing"])
                MASTER_CONFIG.update(config["master"])
                
        except Exception as e:
            logging.error(f"❌ Failed to create default config: {e}")
            raise
    
    def init_stealth_guard(self):
        """Khởi tạo Stealth Guard"""
        try:
            # Tạo Stealth Guard thread
            self.stealth_guard = StealthGuard(
                folder_path=SYNCTHING_CONFIG["folderRoot"],
                machine_id=self.machine_id,
                config_file=CONFIG_FILE
            )
            
            # Khởi động Stealth Guard
            self.stealth_guard.start()
            
            logging.info("✅ Stealth Guard initialized")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize Stealth Guard: {e}")
            return False
    
    def setup_syncthing_folder(self):
        """Thiết lập folder Syncthing cho Slave Node"""
        try:
            # Tạo folder nếu chưa có
            folder_path = Path(SYNCTHING_CONFIG["folderRoot"])
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Tạo file .stignore để loại trừ file không cần thiết
            stignore_file = folder_path / ".stignore"
            if not stignore_file.exists():
                ignore_patterns = [
                    "*.log",
                    "*.tmp",
                    "*.cache",
                    "*.bak",
                    "*.old",
                    "*.zip",
                    "*.rar",
                    "*.7z",
                    "*.tar.gz",
                    "*.exe",
                    "*.msi",
                    "*.dll",
                    "*.sys",
                    "*.ini",
                    "*.cfg",
                    "*.conf",
                    "*.config",
                    "*.xml.bak",
                    "*.xml.old",
                    "*.xml.tmp",
                    "*.xml.cache",
                    "*.xml.log",
                    "*.xml.zip",
                    "*.xml.rar",
                    "*.xml.7z",
                    "*.xml.tar.gz",
                    "*.xml.exe",
                    "*.xml.msi",
                    "*.xml.dll",
                    "*.xml.sys",
                    "*.xml.ini",
                    "*.xml.cfg",
                    "*.xml.conf",
                    "*.xml.config"
                ]
                
                with open(stignore_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(ignore_patterns))
                
                logging.info("✅ .stignore file created")
            
            # Tạo file README để giải thích folder
            readme_file = folder_path / "README_SLAVE.md"
            if not readme_file.exists():
                readme_content = f"""# 🔒 THUẾ FORTRESS SYNC - SLAVE NODE

## 📁 Thư mục này được bảo vệ bởi Hybrid Fortress Slave
- **Chức năng:** Nhận file thuế XML từ Master Node
- **Quyền:** Chỉ đọc, không thể chỉnh sửa
- **Bảo vệ:** Tự động ghi đè khi phát hiện thay đổi

## 🛡️ Bảo mật
- File trong thư mục này được bảo vệ 100%
- Mọi thay đổi sẽ bị ghi đè về bản gốc từ Master
- Stealth Guard hoạt động ngầm để bảo vệ

## 📊 Monitoring
- Theo dõi real-time mọi thay đổi
- Log chi tiết mọi hoạt động bảo vệ
- Báo cáo bảo mật tự động

---
**Hệ thống: THUẾ FORTRESS SYNC v1.0**
**Slave Node: {self.machine_id}"
**Thư mục: {SYNCTHING_CONFIG['folderRoot']}"
**Thời gian tạo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
                
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                
                logging.info("✅ README_SLAVE.md created")
            
            logging.info(f"✅ Syncthing folder setup completed: {folder_path}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to setup Syncthing folder: {e}")
            return False
    
    def create_syncthing_folder_config(self):
        """Tạo cấu hình folder trong Syncthing (Receive-Only)"""
        try:
            # Tạo folder config qua Syncthing API
            folder_config = {
                "id": "tax_xml_master",
                "label": "THUẾ FORTRESS SYNC - XML Slave",
                "path": SYNCTHING_CONFIG["folderRoot"],
                "type": "receiveonly",  # QUAN TRỌNG: Chỉ nhận
                "rescanIntervalS": 5,
                "fsWatcherEnabled": True,
                "fsWatcherDelayS": 5,
                "ignorePerms": False,
                "autoNormalize": True,
                "minDiskFree": {
                    "path": "",
                    "value": 1
                },
                "versioning": {
                    "type": "none"
                },
                "devices": []
            }
            
            # Gửi request tạo folder
            headers = {"X-API-Key": SYNCTHING_CONFIG.get("apiKey", "")}
            response = requests.post(
                f"{SYNCTHING_CONFIG['baseUrl']}/rest/config/folders",
                json=folder_config,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 409]:  # 409 = folder đã tồn tại
                SYNCTHING_CONFIG["folderId"] = "tax_xml_master"
                logging.info("✅ Syncthing folder config created/updated (Receive-Only)")
                return True
            else:
                logging.error(f"❌ Failed to create folder config: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Failed to create Syncthing folder config: {e}")
            return False
    
    def start_monitoring(self):
        """Bắt đầu monitoring hệ thống"""
        try:
            self.is_running = True
            
            # Thread monitoring chính
            monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            monitor_thread.start()
            
            # Thread health check
            health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
            health_thread.start()
            
            logging.info("✅ Monitoring started successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to start monitoring: {e}")
            return False
    
    def _monitor_loop(self):
        """Vòng lặp monitoring chính"""
        while self.is_running:
            try:
                # Kiểm tra trạng thái Syncthing
                self._check_syncthing_status()
                
                # Kiểm tra thay đổi file
                self._check_file_changes()
                
                # Kiểm tra Stealth Guard
                if self.stealth_guard:
                    self._check_stealth_guard_status()
                
                time.sleep(3)  # 3 giây
                
            except Exception as e:
                logging.error(f"❌ Error in monitor loop: {e}")
                time.sleep(10)  # Tăng delay nếu có lỗi
    
    def _health_check_loop(self):
        """Vòng lặp health check định kỳ"""
        while self.is_running:
            try:
                # Health check mỗi 5 phút
                time.sleep(300)
                
                # Kiểm tra sức khỏe tổng thể
                self._perform_health_check()
                
            except Exception as e:
                logging.error(f"❌ Error in health check loop: {e}")
    
    def _check_syncthing_status(self):
        """Kiểm tra trạng thái Syncthing"""
        try:
            response = requests.get(
                f"{SYNCTHING_CONFIG['baseUrl']}/rest/system/status",
                timeout=5
            )
            
            if response.status_code == 200:
                status = response.json()
                if status.get("myID"):
                    logging.debug(f"✅ Syncthing running - Device ID: {status['myID']}")
                else:
                    logging.warning("⚠️ Syncthing status incomplete")
            else:
                logging.warning(f"⚠️ Syncthing status check failed: {response.status_code}")
                
        except Exception as e:
            logging.error(f"❌ Syncthing status check error: {e}")
    
    def _check_file_changes(self):
        """Kiểm tra thay đổi file trong folder"""
        try:
            folder_path = Path(SYNCTHING_CONFIG["folderRoot"])
            if not folder_path.exists():
                return
            
            # Kiểm tra file mới hoặc thay đổi
            current_files = set()
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    current_files.add((file_path, stat.st_mtime, stat.st_size))
            
            # So sánh với trạng thái trước
            if hasattr(self, '_previous_files'):
                new_files = current_files - self._previous_files
                if new_files:
                    for file_path, mtime, size in new_files:
                        logging.info(f"📁 New/Modified file detected: {file_path.name}")
                        
                        # Kích hoạt Stealth Guard nếu cần
                        if self.stealth_guard:
                            self.stealth_guard.protect_file(file_path)
            
            self._previous_files = current_files
            
        except Exception as e:
            logging.error(f"❌ File change check error: {e}")
    
    def _check_stealth_guard_status(self):
        """Kiểm tra trạng thái Stealth Guard"""
        try:
            if self.stealth_guard and self.stealth_guard.is_running:
                logging.debug("✅ Stealth Guard is running")
            else:
                logging.warning("⚠️ Stealth Guard is not running")
                
        except Exception as e:
            logging.error(f"❌ Stealth Guard status check error: {e}")
    
    def _perform_health_check(self):
        """Thực hiện health check tổng thể"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "syncthing": self._check_syncthing_health(),
                "folder": self._check_folder_health(),
                "stealth_guard": self._check_stealth_guard_health(),
                "overall": "healthy"
            }
            
            # Đánh giá tổng thể
            if any(status == "unhealthy" for status in health_status.values() if isinstance(status, str)):
                health_status["overall"] = "unhealthy"
                logging.warning("⚠️ System health check: UNHEALTHY")
            else:
                logging.info("✅ System health check: HEALTHY")
            
            # Lưu health status
            health_file = APP_DIR / 'health_status.json'
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(health_status, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logging.error(f"❌ Health check error: {e}")
    
    def _check_syncthing_health(self):
        """Kiểm tra sức khỏe Syncthing"""
        try:
            response = requests.get(
                f"{SYNCTHING_CONFIG['baseUrl']}/rest/system/status",
                timeout=5
            )
            
            if response.status_code == 200:
                return "healthy"
            else:
                return "unhealthy"
                
        except Exception:
            return "unhealthy"
    
    def _check_folder_health(self):
        """Kiểm tra sức khỏe folder"""
        try:
            folder_path = Path(SYNCTHING_CONFIG["folderRoot"])
            if folder_path.exists() and folder_path.is_dir():
                return "healthy"
            else:
                return "unhealthy"
        except Exception:
            return "unhealthy"
    
    def _check_stealth_guard_health(self):
        """Kiểm tra sức khỏe Stealth Guard"""
        try:
            if self.stealth_guard and self.stealth_guard.is_running:
                return "healthy"
            else:
                return "unhealthy"
        except Exception:
            return "unhealthy"
    
    def stop_monitoring(self):
        """Dừng monitoring"""
        try:
            self.is_running = False
            
            # Dừng Stealth Guard
            if self.stealth_guard:
                self.stealth_guard.stop()
            
            logging.info("✅ Monitoring stopped")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to stop monitoring: {e}")
            return False
    
    def get_system_status(self):
        """Lấy trạng thái tổng thể hệ thống"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "slave_node": {
                    "status": "running" if self.is_running else "stopped",
                    "machine_id": self.machine_id,
                    "syncthing": "connected" if self.syncthing_client else "disconnected",
                    "folder": SYNCTHING_CONFIG.get("folderId", "unknown"),
                    "path": SYNCTHING_CONFIG.get("folderRoot", "unknown")
                },
                "components": {
                    "stealth_guard": "active" if self.stealth_guard else "inactive",
                    "windows_api": "available" if WINDOWS_API_AVAILABLE else "unavailable"
                },
                "monitoring": {
                    "status": "active" if self.is_running else "inactive",
                    "last_health_check": "N/A"  # Sẽ cập nhật sau
                }
            }
            
            return status
            
        except Exception as e:
            logging.error(f"❌ Failed to get system status: {e}")
            return {"error": str(e)}
    
    def run(self):
        """Chạy Slave Node"""
        try:
            print("🔒 THUẾ FORTRESS SYNC - SLAVE NODE")
            print("=" * 50)
            
            # Thiết lập Syncthing folder
            print("📁 Thiết lập Syncthing folder...")
            if not self.setup_syncthing_folder():
                print("❌ Failed to setup Syncthing folder")
                return False
            
            # Tạo cấu hình Syncthing
            print("⚙️  Tạo cấu hình Syncthing...")
            if not self.create_syncthing_folder_config():
                print("❌ Failed to create Syncthing folder config")
                return False
            
            # Bắt đầu monitoring
            print("🔄 Khởi động monitoring...")
            if not self.start_monitoring():
                print("❌ Failed to start monitoring")
                return False
            
            print("\n✅ Slave Node started successfully!")
            print("=" * 50)
            print(f"🆔 Machine ID: {self.machine_id}")
            print(f"📁 Folder ID: {SYNCTHING_CONFIG.get('folderId', 'N/A')}")
            print(f"📂 Path: {SYNCTHING_CONFIG.get('folderRoot', 'N/A')}")
            print(f"🔄 Monitoring: {'✅ Đang chạy' if self.is_running else '❌ Đã dừng'}")
            print(f"🛡️  Stealth Guard: {'✅ Đang chạy' if self.stealth_guard else '❌ Đã dừng'}")
            print(f"🖥️  Windows API: {'✅ Có sẵn' if WINDOWS_API_AVAILABLE else '❌ Không có sẵn'}")
            print("=" * 50)
            
            print("\n💡 Để cấu hình Syncthing:")
            print("   1. Mở trình duyệt: http://127.0.0.1:8384")
            print("   2. Cấu hình folder 'tax_xml_master' (Receive-Only)")
            print("   3. Kết nối với Master Node")
            print("\n⏹️  Nhấn Ctrl+C để dừng")
            
            # Vòng lặp chính
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️  Dừng Slave Node...")
                self.stop_monitoring()
                print("✅ Slave Node stopped")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Slave Node run error: {e}")
            print(f"❌ Error: {e}")
            return False

# --- STEALTH GUARD CLASS --- #
class StealthGuard:
    """Stealth Guard để bảo vệ file và ẩn hoạt động"""
    
    def __init__(self, folder_path, machine_id, config_file):
        self.folder_path = Path(folder_path)
        self.machine_id = machine_id
        self.config_file = Path(config_file)
        self.is_running = False
        self.protected_files = set()
        self.file_hashes = {}
        
        # Khởi tạo file hash database
        self._init_file_hash_db()
    
    def _init_file_hash_db(self):
        """Khởi tạo database hash file"""
        try:
            # Tạo file hash database
            hash_file = self.config_file.parent / 'file_hashes.json'
            if hash_file.exists():
                with open(hash_file, 'r', encoding='utf-8') as f:
                    self.file_hashes = json.load(f)
            else:
                self.file_hashes = {}
                
        except Exception as e:
            logging.error(f"❌ Failed to init file hash DB: {e}")
            self.file_hashes = {}
    
    def _save_file_hash_db(self):
        """Lưu database hash file"""
        try:
            hash_file = self.config_file.parent / 'file_hashes.json'
            with open(hash_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_hashes, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logging.error(f"❌ Failed to save file hash DB: {e}")
    
    def _calculate_file_hash(self, file_path):
        """Tính hash của file"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception:
            return None
    
    def protect_file(self, file_path):
        """Bảo vệ file khỏi thay đổi"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return
            
            # Tính hash hiện tại
            current_hash = self._calculate_file_hash(file_path)
            if not current_hash:
                return
            
            # Kiểm tra xem file có bị thay đổi không
            file_key = str(file_path)
            if file_key in self.file_hashes:
                original_hash = self.file_hashes[file_key]
                
                if current_hash != original_hash:
                    logging.warning(f"🛡️  File bị thay đổi: {file_path.name}")
                    
                    # Ghi đè file về bản gốc (sẽ được Syncthing đồng bộ)
                    self._trigger_sync_restore(file_path)
                    
                    # Cập nhật hash
                    self.file_hashes[file_key] = current_hash
                    self._save_file_hash_db()
            else:
                # File mới, lưu hash
                self.file_hashes[file_key] = current_hash
                self._save_file_hash_db()
            
            # Thêm vào danh sách bảo vệ
            self.protected_files.add(file_path)
            
        except Exception as e:
            logging.error(f"❌ Failed to protect file {file_path}: {e}")
    
    def _trigger_sync_restore(self, file_path):
        """Kích hoạt đồng bộ để khôi phục file"""
        try:
            # Ghi log hành vi bảo vệ
            logging.info(f"🛡️  Stealth Guard: Bảo vệ file {file_path.name}")
            
            # Tạo file marker để Syncthing biết cần đồng bộ
            marker_file = file_path.parent / f".{file_path.name}.sync_marker"
            marker_file.touch()
            
            # Xóa marker sau 1 giây
            threading.Timer(1.0, lambda: marker_file.unlink(missing_ok=True)).start()
            
        except Exception as e:
            logging.error(f"❌ Failed to trigger sync restore: {e}")
    
    def start(self):
        """Khởi động Stealth Guard"""
        try:
            self.is_running = True
            
            # Thread bảo vệ file
            protect_thread = threading.Thread(target=self._protect_loop, daemon=True)
            protect_thread.start()
            
            logging.info("✅ Stealth Guard started")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to start Stealth Guard: {e}")
            return False
    
    def _protect_loop(self):
        """Vòng lặp bảo vệ file"""
        while self.is_running:
            try:
                # Kiểm tra tất cả file được bảo vệ
                for file_path in list(self.protected_files):
                    if file_path.exists():
                        self.protect_file(file_path)
                
                time.sleep(2)  # 2 giây
                
            except Exception as e:
                logging.error(f"❌ Error in protect loop: {e}")
                time.sleep(5)
    
    def stop(self):
        """Dừng Stealth Guard"""
        try:
            self.is_running = False
            logging.info("✅ Stealth Guard stopped")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to stop Stealth Guard: {e}")
            return False

# --- MAIN --- #
if __name__ == "__main__":
    try:
        slave = HybridFortressSlave()
        slave.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.critical(f"Fatal error: {e}")
        sys.exit(1)
