from flask import Blueprint, render_template, redirect, url_for, request, session
from controller import home
from utils import globals
from utils.decorators import login_required


report_bp = Blueprint('report', __name__)

@report_bp.route('/export/<int:id>')
@login_required
def export(id):
    return render_template('babbix_reports.html', id=id, active_page='reports')

@report_bp.route('/reports')
@login_required
def reports():
    return render_template('babbix_export.html', active_page='reports')