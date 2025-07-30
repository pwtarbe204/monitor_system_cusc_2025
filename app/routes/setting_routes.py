from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, send_from_directory
from controller import home
from utils import globals
from utils.decorators import login_required

setting_bp = Blueprint('setting', __name__)

@setting_bp.route('/settings')
@login_required
def settings():
    return render_template('babbix_setting.html', flag=0,msg="no", active_page='settings')

@setting_bp.route('/add_gmail', methods=['POST', 'GET'])
@login_required
def addGmail():
    gmail = ''
    if request.method == 'POST':
        gmail += request.form.get('gmail')
        print(gmail)
    home.addGmail(globals.conn, globals.cursor, gmail)
    return render_template('babbix_setting.html', flag=1, msg="no", active_page='settings')

@setting_bp.route('/delete_gmail/<int:id>')
@login_required
def deleteGmail(id):
    home.deleteGmail(globals.conn, globals.cursor, id)
    return render_template('babbix_setting.html', flag=1, msg="no", active_page='settings')

@setting_bp.route('/gmails')
@login_required
def getGmail():
    return home.getEmail(globals.cursor)

@setting_bp.route('/comfirm/<int:id>', methods=['POST', 'GET'])
@login_required
def confirmOTP(id):
    otp = ''
    if request.method == 'POST':
        otp = request.form.get('otp')
    data = home.getOTP(globals.cursor, id)[0]
    if str(otp) == str(data):
        home.updateEmail(globals.conn, globals.cursor, id)
    return render_template('babbix_setting.html', flag=1, msg="no", active_page='settings')

@setting_bp.route('/change_password', methods=['POST'])
@login_required
def changePassword():
    if request.method == 'POST':
        username = session.get("username")
        old_password = request.form.get('oldPassword')
        new_password_1 = request.form.get('newPassword_1')
        new_password_2 = request.form.get('newPassword_2')
        if home.checkPassword(globals.cursor, username, old_password) is False or home.checkTwoPasswords(new_password_1, new_password_2) is False:
            msg = "Co Van De Roi"
            return render_template('babbix_setting.html', flag=0,msg=msg, active_page='settings')
        else:
            home.changePassword(globals.conn, globals.cursor, username, new_password_1)
            msg = "Ban da thay doi mat khau thanh cong!"
            return render_template('babbix_setting.html', flag=0,msg=msg, active_page='settings')
    return render_template('babbix_setting.html', flag=0, msg="no", active_page='settings')

@setting_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(directory='downloads', path=filename, as_attachment=True)