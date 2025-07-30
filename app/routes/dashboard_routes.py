from flask import Blueprint, render_template, session, redirect, url_for
from controller import home
from utils import globals


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def logged_in():
    if not session.get('username'):
        return False
    return True

@dashboard_bp.route('/')
def dashboard():
    if home.is_env_file_empty('../.env') is True:
        return
    if logged_in() is True:
        id = home.getServer(globals.cursor)
        if id == 0:
            return render_template('babbix_dashboard.html', id=0, active_page='dashboard') 
        return render_template('babbix_dashboard.html', id=id, active_page='dashboard')
    else:
        return redirect(url_for('auth.login'))