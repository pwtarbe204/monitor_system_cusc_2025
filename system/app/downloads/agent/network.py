import psutil
import time
from datetime import datetime
from ping3 import ping
import requests
from urllib.parse import urlparse
from system_info import get_agent_info
import socket
import platform

def get_network_traffic():
    """Collect network traffic metrics (speed and packets)."""
    info = get_agent_info()
    speed = get_network_speed(interval=1)
    packets = get_network_packets()
    return {**speed, **packets, "hostname": info['hostname']}

def get_network_speed(interval):
    """Calculate network send/receive speed in KB/s."""
    net_io_1 = psutil.net_io_counters()
    bytes_sent_1 = net_io_1.bytes_sent
    bytes_recv_1 = net_io_1.bytes_recv
    
    time.sleep(interval)
    
    net_io_2 = psutil.net_io_counters()
    bytes_sent_2 = net_io_2.bytes_sent
    bytes_recv_2 = net_io_2.bytes_recv
    
    sent_speed = (bytes_sent_2 - bytes_sent_1) / interval / 1024  # KB/s
    recv_speed = (bytes_recv_2 - bytes_recv_1) / interval / 1024  # KB/s
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "timestamp": timestamp,
        "sent_speed": sent_speed,
        "recv_speed": recv_speed
    }

def get_network_packets():
    """Get network packet counts."""
    net_io = psutil.net_io_counters()
    return {
        "packet_sent": net_io.packets_sent,
        "packet_recv": net_io.packets_recv
    }

def ping_url(url, times):
    try:
        sum = 0
        for i in range(times):
             sum += float(ping(url, unit="ms", timeout=5))
        result = sum/times
        return int(result) if result else -1
    except Exception as e:
        print(f"Ping error: {e}")
        return -1

def check_load_time(url):
    """Measure the load time of a URL in ms."""
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        end = time.time()
        load_time = round((end - start) * 1000, 2)
        print(f"[+] Page loaded in {load_time} ms" if response.status_code == 200 else f"[!] Page returned status: {response.status_code}")
        return load_time
    except requests.RequestException as e:
        print(f"[!] Error loading page: {e}")
        return -1

def get_listening_ports():
    listening_ports = []

    for conn in psutil.net_connections(kind="inet"):
        if conn.status == psutil.CONN_LISTEN:
            port = conn.laddr.port
            proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
            listening_ports.append({
                "port": port,
                "protocol": proto,
                "status": "open"
            })
    return listening_ports



