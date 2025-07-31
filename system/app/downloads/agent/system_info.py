import psutil
import socket
import platform
import pytz
from datetime import datetime

def get_system_info():
    """Collect system metrics (CPU, RAM, disk) with timestamp."""
    info = get_agent_info()
    cpu = get_cpu_usage()
    ram = get_ram_usage()
    disk = get_disk_usage()
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    timestamp = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "timestamp": timestamp,
        "hostname": info['hostname'],
        "ip": info['host_ip'],
        "cpu": cpu['usage'],
        "ram": ram['percent'],
        "disk": disk['used'], 
        "ram_total": ram['total'],
        "ram_used" : ram['used'],
        "ram_free" : ram['free'], 
        "disk_total" : disk['disk_total'],
        "disk_used" : disk['disk_used']
    }

def get_agent_info():
    """Get agent information (OS, hostname, IP)."""
    os_name = platform.system()
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return {
        "agent_name": f"agent-{hostname}",
        "hostname": hostname,
        "host_ip": ip,
        "os": os_name,
        "status": 1
    }

def get_cpu_usage():
    """Get CPU usage percentage."""
    psutil.cpu_percent(interval=None)
    usage = psutil.cpu_percent(interval=1)
    return {"usage": usage}

def get_ram_usage():
    """Get RAM usage metrics."""
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "percent": mem.percent,
        "free": mem.free
    }

def get_disk_usage():
    """Get disk usage percentage."""
    total, used, free = 0, 0, 0

    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            total += usage.total
            used += usage.used
            free += usage.free
        except PermissionError:
            continue
        
    os_name = platform.system()
    path = 'C:\\' if os_name == 'Windows' else '/'

    return {"used": psutil.disk_usage(path).percent, 
            "disk_total": total,
            "disk_used": used }

get_system_info()