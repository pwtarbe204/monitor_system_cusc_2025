from flask import Blueprint, render_template, redirect, url_for, request, session
from controller import home
from utils import globals
from utils.decorators import login_required


chart_bp = Blueprint('chart', __name__, url_prefix='/chart')

def logged_in():
    if not session.get('username'):
        return False
    return True

@chart_bp.route('/<int:id>')
@login_required
def chart(id):
    if logged_in() is True:
        hostname = home.getAgentById(globals.cursor, id)['hostname']
        sorted_port_info = {}
        if globals.last_known_ports.get(hostname):
            port_info = dict(globals.last_known_ports.get(hostname))
            sorted_port_info = dict(sorted(
                port_info.items(),
                key=lambda item: int(item[0].split('/')[0])  # sort theo số port
            ))
        return render_template('babbix_charts.html', active_page='groups', id=id, port_info=sorted_port_info)
    else:
        return redirect(url_for('auth.login'))