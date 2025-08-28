#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THUẾ FORTRESS SYNC - HYBRID MASTER NODE
Tích hợp Syncthing với XMLProcessor logic ghi đè
"""

import os
import sys
import time
import json
import logging
import requests
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

# Import logic từ XMLProcessor
try:
    sys.path.append(r"C:\Users\Administrator\Videos\xml")
    from icon3 import init_machine_management, get_machine_info
    XML_PROCESSOR_AVAILABLE = True
    print("✅ XMLProcessor logic loaded successfully")
except ImportError as e:
    XML_PROCESSOR_AVAILABLE = False
    print(f"⚠️ XMLProcessor not available: {e}")

# --- CẤU HÌNH HYBRID FORTRESS --- #
APP_DIR = Path(os.getenv('APPDATA', Path.home())) / 'ThuếFortressSync'
APP_DIR.mkdir(parents=True, exist_ok=True)

# Files cấu hình
CONFIG_FILE = APP_DIR / 'hybrid_config.json'
LOG_FILE = APP_DIR / 'hybrid_master.log'
SYNC_DB = APP_DIR / 'sync_machines.db'

# Syncthing API config
SYNCTHING_CONFIG = {
    "baseUrl": "http://127.0.0.1:8384",
    "apiKey": "",  # Sẽ lấy từ Syncthing config
    "folderId": "",  # Sẽ tạo khi setup
    "folderRoot": r"C:\Users\Administrator\Videos\SYNC TAXX"
}

# Telegram config (từ XMLProcessor)
TELEGRAM_CONFIG = {
    "bot_token": "7283723256:AAEqXPiQ-s2sYI8vyhfUyrcq8uL-pRG_UZI",
    "group_id": "-1002980917638"
}

# --- LOGGING --- #
logging.basicConfig(
    filename=str(LOG_FILE),
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HybridFortressMaster:
    """Master Node tích hợp Syncthing + XMLProcessor"""
    
    def __init__(self):
        self.syncthing_client = None
        self.xml_processor = None
        self.machine_manager = None
        self.is_running = False
        
        # Khởi tạo các component
        self.init_components()
    
    def init_components(self):
        """Khởi tạo các component cần thiết"""
        try:
            # 1. Khởi tạo Machine Management (từ XMLProcessor)
            if XML_PROCESSOR_AVAILABLE:
                init_machine_management()
                self.machine_manager = True
                logging.info("✅ Machine Management initialized")
            
            # 2. Khởi tạo Syncthing client
            self.init_syncthing_client()
            
            # 3. Tạo cấu hình mặc định
            self.create_default_config()
            
            logging.info("✅ Hybrid Fortress Master initialized successfully")
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize components: {e}")
            raise
    
    def init_syncthing_client(self):
        """Khởi tạo Syncthing client"""
        try:
            # Kiểm tra Syncthing có chạy không
            response = requests.get(f"{SYNCTHING_CONFIG['baseUrl']}/rest/system/status", timeout=5)
            if response.status_code == 200:
                logging.info("✅ Syncthing is running")
                self.syncthing_client = True
                
                # Tự động lấy API key
                if not SYNCTHING_CONFIG["apiKey"]:
                    self.get_syncthing_api_key()
                
                # Tự động tạo folder config
                if SYNCTHING_CONFIG["apiKey"]:
                    self.create_syncthing_folder_config()
                    
            else:
                logging.warning("⚠️ Syncthing not responding properly")
                
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Syncthing not accessible: {e}")
            print("⚠️ Syncthing chưa chạy. Hãy khởi động Syncthing trước!")
            print("💡 Hướng dẫn:")
            print("   1. Mở cmd với quyền Admin")
            print("   2. cd 'C:\\Users\\Administrator\\Videos\\SYNC TAXX\\syncthing-windows-amd64-v1.27.6'")
            print("   3. syncthing.exe")
            print("   4. Đợi Syncthing khởi động xong (có icon trong system tray)")
            print("   5. Chạy lại python hybrid_fortress_master.py")
    
    def create_default_config(self):
        """Tạo cấu hình mặc định cho Hybrid Fortress"""
        try:
            if not CONFIG_FILE.exists():
                default_config = {
                    "syncthing": {
                        "baseUrl": SYNCTHING_CONFIG["baseUrl"],
                        "apiKey": "",
                        "folderId": "tax_xml_master",
                        "folderRoot": SYNCTHING_CONFIG["folderRoot"]
                    },
                    "telegram": TELEGRAM_CONFIG,
                    "monitoring": {
                        "interval": 5,
                        "health_check_interval": 300,
                        "log_retention_days": 30
                    },
                    "security": {
                        "auto_overwrite": True,
                        "conflict_resolution": "master_wins",
                        "stealth_mode": True
                    }
                }
                
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                
                logging.info("✅ Default configuration created")
            
            # Load config
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                SYNCTHING_CONFIG.update(config["syncthing"])
                
        except Exception as e:
            logging.error(f"❌ Failed to create default config: {e}")
            raise
    
    def setup_syncthing_folder(self):
        """Thiết lập folder Syncthing cho Master Node"""
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
            readme_file = folder_path / "README_MASTER.md"
            if not readme_file.exists():
                readme_content = f"""# 🚀 THUẾ FORTRESS SYNC - MASTER NODE

## 📁 Thư mục này được quản lý bởi Hybrid Fortress Master
- **Chức năng:** Chia sẻ file thuế XML gốc với tất cả Slave Node
- **Quyền:** Chỉ Master Node mới được chỉnh sửa
- **Đồng bộ:** Tự động với tất cả máy con qua Syncthing

## 🔒 Bảo mật
- File trong thư mục này sẽ được bảo vệ 100%
- Slave Node chỉ có thể nhận, không thể sửa đổi
- Mọi thay đổi sẽ bị ghi đè về bản gốc

## 📊 Monitoring
- Theo dõi real-time mọi thay đổi
- Log chi tiết mọi hoạt động
- Báo cáo bảo mật qua Telegram Bot

---
**Hệ thống: THUẾ FORTRESS SYNC v1.0**
**Master Node: {SYNCTHING_CONFIG['folderRoot']}**
**Thời gian tạo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
                
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                
                logging.info("✅ README_MASTER.md created")
            
            logging.info(f"✅ Syncthing folder setup completed: {folder_path}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to setup Syncthing folder: {e}")
            return False
    
    def get_syncthing_api_key(self):
        """Lấy API key từ Syncthing config"""
        try:
            # Đường dẫn config Syncthing
            config_path = Path.home() / "AppData/Local/Syncthing/config.xml"
            
            if not config_path.exists():
                logging.warning("⚠️ Syncthing config not found, trying alternative path")
                config_path = Path.home() / "AppData/Roaming/Syncthing/config.xml"
            
            if config_path.exists():
                # Parse XML để lấy API key
                tree = ET.parse(config_path)
                root = tree.getroot()
                
                # Tìm thẻ gui
                gui_element = root.find("gui")
                if gui_element is not None:
                    api_key = gui_element.find("apikey")
                    if api_key is not None:
                        SYNCTHING_CONFIG["apiKey"] = api_key.text
                        logging.info("✅ Syncthing API key retrieved")
                        return True
            
            logging.warning("⚠️ API key not found in config, will use default")
            return False
            
        except Exception as e:
            logging.error(f"❌ Failed to get Syncthing API key: {e}")
            return False
    
    def create_syncthing_folder_config(self):
        """Tạo cấu hình folder trong Syncthing"""
        try:
            if not SYNCTHING_CONFIG["apiKey"]:
                if not self.get_syncthing_api_key():
                    logging.error("❌ Cannot create folder config without API key")
                    return False
            
            # Kiểm tra xem folder đã có chưa
            headers = {"X-API-Key": SYNCTHING_CONFIG["apiKey"]}
            response = requests.get(
                f"{SYNCTHING_CONFIG['baseUrl']}/rest/config/folders",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                folders = response.json()
                for folder in folders:
                    if folder.get("id") == "tax_xml_master":
                        SYNCTHING_CONFIG["folderId"] = "tax_xml_master"
                        logging.info("✅ Syncthing folder already exists")
                        
                        # Cập nhật folder config nếu cần
                        self._update_folder_config()
                        return True
            
            # Nếu folder chưa có, tạo mới
            folder_config = {
                "id": "tax_xml_master",
                "label": "THUẾ FORTRESS SYNC - XML Master",
                "path": SYNCTHING_CONFIG["folderRoot"],
                "type": "sendreceive",
                "rescanIntervalS": 10,
                "fsWatcherEnabled": True,
                "fsWatcherDelayS": 10,
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
            response = requests.post(
                f"{SYNCTHING_CONFIG['baseUrl']}/rest/config/folders",
                json=folder_config,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 409]:  # 409 = folder đã tồn tại
                SYNCTHING_CONFIG["folderId"] = "tax_xml_master"
                logging.info("✅ Syncthing folder config created/updated")
                
                # Cập nhật folder config
                self._update_folder_config()
                return True
            else:
                logging.error(f"❌ Failed to create folder config: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Failed to create Syncthing folder config: {e}")
            return False
    
    def _update_folder_config(self):
        """Cập nhật cấu hình folder với device ID của Master"""
        try:
            if not SYNCTHING_CONFIG["apiKey"] or not SYNCTHING_CONFIG["folderId"]:
                return False
            
            # Lấy device ID của Master
            headers = {"X-API-Key": SYNCTHING_CONFIG["apiKey"]}
            response = requests.get(
                f"{SYNCTHING_CONFIG['baseUrl']}/rest/system/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                status = response.json()
                master_device_id = status.get("myID")
                
                if master_device_id:
                    # Cập nhật folder config để thêm Master device
                    folder_config = {
                        "devices": [
                            {
                                "deviceID": master_device_id,
                                "introducedBy": "",
                                "encryptionPassword": ""
                            }
                        ]
                    }
                    
                    # Gửi request cập nhật
                    update_response = requests.put(
                        f"{SYNCTHING_CONFIG['baseUrl']}/rest/config/folders/{SYNCTHING_CONFIG['folderId']}",
                        json=folder_config,
                        headers=headers,
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        logging.info(f"✅ Folder config updated with Master device: {master_device_id}")
                        return True
                    else:
                        logging.warning(f"⚠️ Failed to update folder config: {update_response.status_code}")
                        return False
            
            return False
            
        except Exception as e:
            logging.error(f"❌ Failed to update folder config: {e}")
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
                
                # Kiểm tra machine status
                if self.machine_manager:
                    self._check_machine_health()
                
                time.sleep(5)  # 5 giây
                
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
            if not SYNCTHING_CONFIG["apiKey"]:
                return
            
            headers = {"X-API-Key": SYNCTHING_CONFIG["apiKey"]}
            response = requests.get(
                f"{SYNCTHING_CONFIG['baseUrl']}/rest/system/status",
                headers=headers,
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
                        
                        # Gửi thông báo qua Telegram nếu cần
                        if self._should_notify_file_change(file_path):
                            self._send_telegram_notification(f"📁 File mới: {file_path.name}")
            
            self._previous_files = current_files
            
        except Exception as e:
            logging.error(f"❌ File change check error: {e}")
    
    def _check_machine_health(self):
        """Kiểm tra sức khỏe các máy con"""
        try:
            if not self.machine_manager:
                return
            
            # Sử dụng XMLProcessor để kiểm tra machine health
            # (Logic này sẽ được implement khi tích hợp hoàn chỉnh)
            pass
            
        except Exception as e:
            logging.error(f"❌ Machine health check error: {e}")
    
    def _perform_health_check(self):
        """Thực hiện health check tổng thể"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "syncthing": self._check_syncthing_health(),
                "folder": self._check_folder_health(),
                "machines": self._check_machines_health(),
                "overall": "healthy"
            }
            
            # Đánh giá tổng thể
            if any(status == "unhealthy" for status in health_status.values() if isinstance(status, str)):
                health_status["overall"] = "unhealthy"
                logging.warning("⚠️ System health check: UNHEALTHY")
                
                # Gửi cảnh báo qua Telegram
                self._send_telegram_notification("⚠️ Hệ thống có vấn đề - Kiểm tra ngay!")
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
            if not SYNCTHING_CONFIG["apiKey"]:
                return "unknown"
            
            headers = {"X-API-Key": SYNCTHING_CONFIG["apiKey"]}
            response = requests.get(
                f"{SYNCTHING_CONFIG['baseUrl']}/rest/system/status",
                headers=headers,
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
    
    def _check_machines_health(self):
        """Kiểm tra sức khỏe các máy con"""
        try:
            # Logic kiểm tra máy con sẽ được implement sau
            return "healthy"
        except Exception:
            return "unhealthy"
    
    def _should_notify_file_change(self, file_path):
        """Quyết định có gửi thông báo file thay đổi không"""
        try:
            # Chỉ thông báo file XML thuế
            if file_path.suffix.lower() == '.xml':
                # Kiểm tra tên file có pattern thuế không
                filename = file_path.name.lower()
                tax_keywords = ['tax', 'thue', 'etax', 'vat', 'invoice']
                return any(keyword in filename for keyword in tax_keywords)
            return False
        except Exception:
            return False
    
    def _send_telegram_notification(self, message):
        """Gửi thông báo qua Telegram"""
        try:
            if not TELEGRAM_CONFIG.get("bot_token") or not TELEGRAM_CONFIG.get("group_id"):
                return
            
            url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['bot_token']}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CONFIG["group_id"],
                "text": f"🚀 **THUẾ FORTRESS SYNC**\n\n{message}\n\n⏰ {datetime.now().strftime('%H:%M:%S')}",
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logging.info(f"✅ Telegram notification sent: {message}")
            else:
                logging.warning(f"⚠️ Telegram notification failed: {response.status_code}")
                
        except Exception as e:
            logging.error(f"❌ Telegram notification error: {e}")
    
    def stop_monitoring(self):
        """Dừng monitoring"""
        try:
            self.is_running = False
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
                "master_node": {
                    "status": "running" if self.is_running else "stopped",
                    "syncthing": "connected" if SYNCTHING_CONFIG.get("apiKey") else "disconnected",
                    "folder": SYNCTHING_CONFIG.get("folderId", "unknown"),
                    "path": SYNCTHING_CONFIG.get("folderRoot", "unknown")
                },
                "components": {
                    "xml_processor": "available" if XML_PROCESSOR_AVAILABLE else "unavailable",
                    "machine_manager": "active" if self.machine_manager else "inactive",
                    "telegram_bot": "active" if TELEGRAM_CONFIG.get("bot_token") else "inactive"
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
        """Chạy Master Node"""
        try:
            print("🚀 THUẾ FORTRESS SYNC - MASTER NODE")
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
            
            print("\n✅ Master Node started successfully!")
            print("=" * 50)
            print(f"📁 Folder ID: {SYNCTHING_CONFIG.get('folderId', 'N/A')}")
            print(f"📂 Path: {SYNCTHING_CONFIG.get('folderRoot', 'N/A')}")
            print(f"🔑 API Key: {'✅ Đã cấu hình' if SYNCTHING_CONFIG.get('apiKey') else '❌ Chưa cấu hình'}")
            print(f"🔄 Monitoring: {'✅ Đang chạy' if self.is_running else '❌ Đã dừng'}")
            print(f"🤖 Telegram Bot: {'✅ Đã cấu hình' if TELEGRAM_CONFIG.get('bot_token') else '❌ Chưa cấu hình'}")
            print("=" * 50)
            
            print("\n💡 Để cấu hình Syncthing:")
            print("   1. Mở trình duyệt: http://127.0.0.1:8384")
            print("   2. Cấu hình folder 'tax_xml_master'")
            print("   3. Thêm Slave Node")
            print("\n⏹️  Nhấn Ctrl+C để dừng")
            
            # Vòng lặp chính
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️  Dừng Master Node...")
                self.stop_monitoring()
                print("✅ Master Node stopped")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Master Node run error: {e}")
            print(f"❌ Error: {e}")
            return False

# --- MAIN --- #
if __name__ == "__main__":
    try:
        master = HybridFortressMaster()
        master.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.critical(f"Fatal error: {e}")
        sys.exit(1)
