import subprocess
import json

def bps_to_mbps(bps):
    return round(bps * 8 / 1_000_000, 2)

def get_speedtest_results():
    """Get speedtest results including download, upload, and ping."""
    command = ['speedtest.exe', '--format=json']

    data = subprocess.run(command, capture_output=True, text=True)

    data = json.loads(data.stdout)

    download_speed = bps_to_mbps(data['download']['bandwidth'])
    upload_speed = bps_to_mbps(data['upload']['bandwidth'])
    ping = data['ping']['latency']
    server = {
        'name': data['server']['name'],
        'location': data['server']['location'],
        'country': data['server']['country'],
        'ip': data['server']['ip']
    }
    print(f"Download: {download_speed:.2f} Mbps")
    print(f"Upload: {upload_speed:.2f} Mbps")
    print(f"Ping: {ping:.2f} ms")
    print(f"Server: {server['name']} ({server['location']}, {server['country']}) - {server['ip']}") 

    return download_speed, upload_speed, ping, server
