import threading
import time
import sys
import requests
from api import create_app
from system_info import get_system_info, get_agent_info
from network import get_network_traffic, get_listening_ports
from utils import reset_metrics, TEST, tb_ram, tb_cpu
import platform
import os
from dotenv import set_key, load_dotenv
from interface import setup
from pathlib import Path

from pystray import Icon, MenuItem, Menu
from PIL import Image

# ========== Load .env ==========
if getattr(sys, 'frozen', False):
    # Nếu chạy từ .exe
    env_file = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    # Nếu chạy từ script .py
    env_file = os.path.join(os.path.dirname(__file__), '.env')


def send_port_status():
    port_data = {
        "hostname": platform.node(),
        "ports": get_listening_ports()
    }
    try:
        requests.post(f"{URL}api/port_status", json=port_data, timeout=2)
        response.raise_for_status()
    except requests.RequestException as e:
        print("[!] Failed to connect to server:", e)


def main():
    """Main loop to collect system and network metrics and send to server."""
    global TEST
    TEST += 1

    sys_info = get_system_info()
    traffic = get_network_traffic()
    ports = get_listening_ports()

    sys_info['count'] = TEST
    tb_ram.append(sys_info['ram'])
    tb_cpu.append(sys_info['cpu'])
    sys_info['tb_ram'] = sum(tb_ram) / len(tb_ram) if tb_ram else 0
    sys_info['tb_cpu'] = sum(tb_cpu) / len(tb_cpu) if tb_cpu else 0

    port_data = {"hostname": sys_info['hostname'], "ports": ports}

    if TEST == 100:
        reset_metrics()
        time.sleep(10)

    try:
        requests.post(f"{URL}api/sysinfo", json=sys_info, timeout=2)
        requests.post(f"{URL}api/network", json=traffic, timeout=2)
        requests.post(f"{URL}api/port_status", json=port_data, timeout=2)
    except requests.RequestException as e:
        print("[!] Error sending info to server:", e)
    except ValueError:
        pass


# ========== SYSTEM TRAY ==========
def create_tray_icon():
    try:
        icon_image = Image.open("babbix.ico")
    except Exception as e:
        print(f"[!] Không thể tải icon: {e}")
        return

    def on_quit(icon, item):
        print("[INFO] Thoát chương trình từ tray.")
        icon.stop()
        os._exit(0)

    tray_menu = Menu(MenuItem('Thoát', on_quit))
    tray_icon = Icon("Agent Monitor", icon_image, "Agent đang chạy", tray_menu)
    tray_icon.run()


# ========== MAIN ==========
if __name__ == "__main__":

    # Hiển thị giao diện để người dùng nhập địa chỉ IP server
    confirmed = setup()

    if not confirmed:
        print("[!] Người dùng đã tắt cửa sổ mà không kết nối. Thoát.")
        sys.exit(0)

    load_dotenv(env_file, override=True)
    URL = os.getenv('SERVER')

    if not URL:
        print("[!] Không có biến SERVER trong file .env")
        sys.exit(1)

    print(f"[INFO] SERVER URL: {URL}")

    # Đăng ký agent lên server
    agent_data = get_agent_info()
    while True:
        try:
            response = requests.post(f"{URL}api/addagent", json=agent_data, timeout=2)
            response.raise_for_status()
            print(response.json())
            break
        except requests.RequestException as e:
            print("[!] Failed to connect to server:", e)
        time.sleep(2)

    # Chạy Flask app ở luồng nền
    flask_thread = threading.Thread(
        target=create_app().run,
        kwargs={'host': '0.0.0.0', 'port': 5001, 'debug': False, 'use_reloader': False},
        daemon=True
    )
    flask_thread.start()

    # Chạy icon tray ở luồng nền
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

    # Vòng lặp chính
    try:
        while True:
            main()
            time.sleep(5)
    except KeyboardInterrupt:
        sys.exit(0)
