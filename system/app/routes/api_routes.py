from flask import Blueprint, jsonify, request, redirect, url_for
import requests
from controller import home
import time
from utils import globals

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/chart-data/<int:agent_id>', methods=['GET'])
def get_chart_data(agent_id):
    try:
        network = home.getNetTraffic(globals.cursor, agent_id)
        sysinfo = home.getSysinfo(globals.cursor, agent_id)
        data = network | sysinfo
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/addagent', methods=['POST'])
def getInfo():
    time.sleep(0.2)
    data = request.get_json()
    home.addAgentHostname(globals.conn, globals.cursor, data)
    return jsonify({"status": "success"}), 200

@api_bp.route('/DataGroup')
def getGroups():
    if globals.conn is None or globals.cursor is None:
        return jsonify({"error": "Database connection not established"}), 500
    all_group = home.getGroupHost(globals.cursor)
    so_luong = {'soluong': len(all_group.get('id'))}
    data = []
    for i in range(so_luong.get('soluong')):
        dt = {}
        for j in all_group:
            dt[j] = all_group.get(j)[i]
            if j == 'id':
                id = all_group.get(j)[i]
                dt['total']  = home.number_of_agent_in_Group(globals.cursor, id)
        data.append(dt)
    data.append(so_luong)
    return data

THRESHOLDS = {
    "cpu": 85,   
    "ram": 80,
    "disk": 90
}
@api_bp.route('/sysinfo', methods=['POST', 'GET'])
def sendsysinfo():
    time.sleep(0.2)
    global TEST
    try:
        data = request.get_json()
        hostname= data['hostname']
        id = home.getAgentIdFromHostname(globals.cursor, hostname)
        home.addSysInfo(globals.conn, globals.cursor, data, id['id'][0])
        if data['count'] == 100:
            ten_may_tinh = hostname
            ip_may_tinh = data['ip']
            thoi_gian = data['timestamp']
            cpu_usage = data['tb_cpu']
            ram_usage = data['tb_ram']
            disk_usage  = data['disk']

            cpu_threshold = THRESHOLDS['cpu']
            ram_threshold = THRESHOLDS['ram']
            disk_threshold = THRESHOLDS['disk']

            thong_so_1 = ''
            thong_so_2 = ''
            thong_so_3 = ''

            if cpu_usage > cpu_threshold:
                thong_so_1 = f'<tr><td>CPU Usage</td><td style="color:red;"><b>{cpu_usage}%</b></td><td>{cpu_threshold}%</td></tr>'
            else: 
                thong_so_1 = f'<tr><td>CPU Usage</td><td><b>{cpu_usage}%</b></td><td>{cpu_threshold}%</td></tr>'

            if ram_usage > ram_threshold:
                thong_so_2 = f'<tr><td>RAM Usage</td><td style="color:red;"><b>{ram_usage}%</b></td><td>{ram_threshold}%</td></tr>'
            else: 
                thong_so_2 = f'<tr><td>RAM Usage</td><td><b>{ram_usage}%</b></td><td>{ram_threshold}%</td></tr>'

            if disk_usage > disk_threshold:
                thong_so_3 = f'<tr><td>Disk Usage</td><td style="color:red;"><b>{disk_usage}%</b></td><td>{disk_threshold}%</td></tr>'
            else: 
                thong_so_3 = f'<tr><td>Disk Usage</td><td><b>{disk_usage}%</b></td><td>{disk_threshold}%</td></tr>'

            html = f"""
                    <html>
                    <body>
                    <p>Kính gửi Quản trị viên,</p>

                    <p>Hệ thống vừa ghi nhận <b>một số thông số trên máy tính <u>{ten_may_tinh}</u> đã vượt ngưỡng</b> vào lúc <b>{thoi_gian}</b>:</p>

                    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
                    <tr><th>Thông số</th><th>Giá trị hiện tại</th><th>Ngưỡng cho phép</th></tr>
                    {thong_so_1}
                    {thong_so_2}
                    {thong_so_3}
                    </table>

                    <p><b>Thông tin thêm:</b><br>
                    - Địa chỉ IP: <code>{ip_may_tinh}</code><br>
                    </p>

                    <p><b>Hành động đề xuất:</b><br>
                    – Kiểm tra tiến trình tiêu tốn tài nguyên.<br>
                    – Đảm bảo hệ thống không bị tấn công hoặc lỗi ứng dụng.<br>
                    – Khởi động lại máy nếu cần thiết.</p>

                    <p>Trân trọng,<br>
                    <b>Hệ Thống Babbix./b></p>
                    </body>
                    </html>
                    """
            content = ''
            if data['tb_ram'] > 70 or data['tb_cpu'] > 80:
                content += "TB_RAM: " + str(data['tb_ram']) + '\n'
                content += "TB_CPU: " + str(data['tb_cpu']) + '\n'
                home.sendAlerts(globals.cursor, html)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

#________________________________________________________________________________

@api_bp.route('/network', methods=['POST'])
def netinfo():
    time.sleep(0.2)
    try:
        data = request.get_json()
        hostname = data['hostname']
        id = home.getAgentIdFromHostname(globals.cursor, hostname)
        if id != 0:
            home.addNetTraffic(globals.conn, globals.cursor, data, id['id'][0])
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    
@api_bp.route('/agents')
def allAgent():
    time.sleep(0.2)
    try:
        home.updateStatus(globals.conn, globals.cursor)
        data = home.getAllData(globals.cursor)
        return data
    except Exception as e:
         return jsonify({"error": "Internal server error"}), 500
    
@api_bp.route('/agents/<int:group_id>')
def allAgentInGroup(group_id):
    time.sleep(0.2)
    try:
        home.updateStatus(globals.conn, globals.cursor)
        data = home.getAgentsInGroup(globals.cursor, group_id)
        return data
    except Exception as e:
         return jsonify({"error": "Internal server error"}), 500
    

@api_bp.route('/agent/<int:id>')
def getAgent(id):
    data = home.getAgentById(globals.cursor, id)
    return data

@api_bp.route('/url')
def getUrl():
    try:
        urls = home.getUrl(globals.cursor)
        if urls:
            return jsonify(urls)
        else:
            return jsonify({"message": "No URLs found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    
@api_bp.route('/checker/<int:agent_id>')
def getChecker(agent_id):
    data = home.getAllDataUrl(globals.cursor,agent_id)
    return jsonify(data)


@api_bp.route("/port_status", methods=["POST"])
def port_status():
    data = request.get_json()
    hostname = data.get("hostname")
    ports = data.get("ports")
    
    if hostname and ports:
        port_status_dict = {
            f"{p['port']}/{p['protocol']}": p["status"] for p in ports
        }
        globals.last_known_ports[hostname] = port_status_dict
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "Invalid data"}), 400

@api_bp.route('/groups')
def allGroups():
    try:
        data = home.getGroupHost(globals.cursor)
        so_luong = len(data.get('id'))
        print(so_luong)
        all_data = []
        for i in range(0, so_luong):
            dt = {}
            for j in data:
                dt[j] = data.get(j)[i]
            dt.pop('location', None)
            all_data.append(dt)
        return jsonify(all_data)
    except Exception as e:
         return jsonify({"error": "Internal server error"}), 500