import threading
import time
import sys
import requests
from api import create_app
from system_info import get_system_info, get_agent_info
from network import get_network_traffic, get_listening_ports
from utils import URL, reset_metrics, TEST, tb_ram, tb_cpu
import platform
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

# ================== FUNCTION TO GET SYSTEM INFO AND SEND TO SERVER ==================
def send_metrics_loop():
    global TEST
    agent_data = get_agent_info()

    # Đăng ký agent một lần
    while True:
        try:
            response = requests.post(f"{URL}api/addagent", json=agent_data, timeout=2)
            response.raise_for_status()
            print(response.json())
            break
        except requests.RequestException as e:
            print("[!] Failed to connect to server:", e)
        time.sleep(2)

    # Gửi thông tin định kỳ
    while True:
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
            print("[+] Sent data to server")
        except requests.RequestException as e:
            print("[!] Error sending info to server:", e)
        except ValueError:
            pass

        time.sleep(5)

# ================== SYSTEM TRAY ==================
def create_image():
    image = Image.new('RGB', (64, 64), "white")
    dc = ImageDraw.Draw(image)
    dc.ellipse((16, 16, 48, 48), fill="blue")
    return image

def exit_app(icon, item):
    print("[*] Exiting...")
    icon.stop()
    sys.exit(0)

def tray_app():
    icon = Icon("Agent")
    icon.icon = create_image()
    icon.menu = Menu(MenuItem("Thoát", exit_app))
    icon.run()

# ================== MAIN ==================
if __name__ == "__main__":
    # Thread chạy Flask
    flask_thread = threading.Thread(
        target=create_app().run,
        kwargs={'host': '0.0.0.0', 'port': 5001, 'debug': False, 'use_reloader': False},
        daemon=True
    )
    flask_thread.start()

    # Thread chạy gửi dữ liệu
    metrics_thread = threading.Thread(target=send_metrics_loop, daemon=True)
    metrics_thread.start()

    # Giao diện khay hệ thống (chạy chính)
    tray_app()
