from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify
from controller import home
from utils.decorators import login_required

speedtest_bp = Blueprint('speedtest', __name__)

@speedtest_bp.route('/speedtest', methods=['POST', 'GET'])
@login_required
def speedtest():
    return render_template('babbix_speedtest.html', active_page='speedtest')

# @speedtest_bp.route('/speedtest/get_server')
# def get_server():
#     servers = home.get_list_server()
#     return servers

# @speedtest_bp.route('/speedtest/<int:server_id>', methods=['POST', 'GET'])
# def speedtest_server(server_id):
#     speed = home.get_speed(server_id)
#     print(speed)
#     return speed
