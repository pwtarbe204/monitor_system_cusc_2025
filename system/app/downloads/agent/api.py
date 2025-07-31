from flask import Flask, request, jsonify
from network import ping_url, check_load_time, get_agent_info
from urllib.parse import urlparse
from flask_cors import CORS

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    CORS(app)
    
    @app.route('/ping', methods=['POST'])
    def ping_url_endpoint():
        """Handle ping requests and return results."""
        data = request.get_json()
        url = data.get('url')

        if not url.startswith('http'):
            url = f'http://{url}'
        
        hostname = urlparse(url).hostname
        if not hostname:
            return jsonify({"error": "Invalid URL"}), 400
        
        ping_result = ping_url(hostname, 10)
        load_time = check_load_time(url)
        info = get_agent_info()
        
        print(f"Ping result for {url}: {ping_result} ms")
        print(f"Request result for {url}: {load_time} ms")
        
        status = "Active" if ping_result != -1 else "Inactive"
        response_data = {
            "host": info['host_ip'],
            "rtt": str(ping_result),
            "load_time": str(load_time),
            "status": status
        }
        return jsonify(response_data) if status == "Active" else (jsonify(response_data), 500)
    
    @app.route('/check_local', methods=['POST'])
    def check_local():
        """Handle local IP ping requests and return results."""
        data = request.get_json()
        ips = data.get('ips', [])
        result = [{"host": ip, "rtt": ping_url(ip, 10)} for ip in ips]
        return jsonify(result)
    @app.route('/get_speedtest', methods=['GET', 'POST'])
    def speedtest():
        """Handle speedtest requests and return results."""
        from internet_speed import get_speedtest_results
        download, upload, ping, server = get_speedtest_results()
        return {
            'download': round(download, 2),
            'upload': round(upload, 2),
            'ping': round(ping, 2), 
            'server': {
                'name': server['name'],
                'location': server['location'],
                'country': server['country'],
                'ip': server['ip']
            }
        }
    return app