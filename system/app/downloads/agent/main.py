import threading
import time
import sys
import requests
from api import create_app
from system_info import get_system_info, get_agent_info
from network import get_network_traffic, get_listening_ports
from utils import URL, reset_metrics, TEST, tb_ram, tb_cpu
import platform

URL = None

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

    sys_info = get_system_info() # Collect system info
    traffic = get_network_traffic() # Collect network info
    ports = get_listening_ports() # Collect port info

    sys_info['count'] = TEST 
    tb_ram.append(sys_info['ram'])
    tb_cpu.append(sys_info['cpu'])
    sys_info['tb_ram'] = sum(tb_ram) / len(tb_ram) if tb_ram else 0
    sys_info['tb_cpu'] = sum(tb_cpu) / len(tb_cpu) if tb_cpu else 0
    

    port_data = {"hostname": sys_info['hostname'],"ports": ports}
    # Reset metrics if TEST reaches 100
    if TEST == 100:
        reset_metrics()
        time.sleep(10)
    
    # Send info to server
    try:
        requests.post(f"{URL}api/sysinfo", json=sys_info, timeout=2)
        requests.post(f"{URL}api/network", json=traffic, timeout=2)
        requests.post(f"{URL}api/port_status", json=port_data, timeout=2)
        response.raise_for_status()
        print(response.json())
    except requests.RequestException as e:
        print("[!] Error sending info to server:", e)
    except ValueError:
        pass


if __name__ == "__main__":
    # Register agent with server
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
    
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=create_app().run, kwargs={'host': '0.0.0.0', 'port': 5001, 'debug': False, 'use_reloader': False}, daemon=True)
    flask_thread.start()
    
    # Run main loop
    try:
        while True:
            main()
            time.sleep(5)
    except KeyboardInterrupt:
        sys.exit(0)