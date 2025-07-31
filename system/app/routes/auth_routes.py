from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from controller import home
from dotenv import load_dotenv, set_key
import os
from config import db
from utils import globals


ENV_FILE = '.env'
auth_bp = Blueprint('auth', __name__)
load_dotenv(ENV_FILE, override=True)
#load_dotenv(dotenv_path='../config.conf')

@auth_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if not home.is_env_file_empty(ENV_FILE):
            load_dotenv(ENV_FILE, override=True)

            DB_HOST = os.getenv('DB_HOST')
            DB_PORT = os.getenv('DB_PORT')
            DB_DATABASE = os.getenv('DB_DATABASE')
            DB_USERNAME = os.getenv('DB_USERNAME')
            DB_PASSWORD = os.getenv('DB_PASSWORD')
            if home.is_right_parameters():
                conn, cursor = db.connect(DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD)
                conn.autocommit = True
                globals.conn = conn
                globals.cursor = cursor
                return redirect(url_for('auth.register'))
        return render_template('index.html')
    else:
        server = request.form.get('server')
        port = request.form.get('port')
        database = request.form.get('database')
        username = request.form.get('username')
        password = request.form.get('password')
        with open(ENV_FILE, 'a') as f:
            pass
        try:
            set_key(ENV_FILE, 'DB_HOST', server)
            set_key(ENV_FILE, 'DB_PORT', port)
            set_key(ENV_FILE, 'DB_DATABASE', database)
            set_key(ENV_FILE, 'DB_USERNAME', username)
            set_key(ENV_FILE, 'DB_PASSWORD', password)

            load_dotenv(ENV_FILE, override=True)

            DB_HOST = os.getenv('DB_HOST')
            DB_PORT = os.getenv('DB_PORT')
            DB_DATABASE = os.getenv('DB_DATABASE')
            DB_USERNAME = os.getenv('DB_USERNAME')
            DB_PASSWORD = os.getenv('DB_PASSWORD')

            conn, cursor = db.connect(DB_HOST, DB_PORT, 'master', DB_USERNAME,DB_PASSWORD)

            db.initializeDatabase(conn, cursor, DB_DATABASE)

            conn, cursor = db.connect(DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD)
            conn.autocommit = True

            globals.conn = conn
            globals.cursor = cursor

            return redirect(url_for('auth.register'))
        except Exception as e:
            print(f"Error setting environment variables: {e}")
            return jsonify({"message": "Failed to set environment variables"}, 500)
        

@auth_bp.route('/connect_database', methods=['GET'])
def connect_database():
    load_dotenv(override=True)

    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_DATABASE = os.getenv('DB_DATABASE')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    conn = db.connect(DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME,DB_PASSWORD)
    if conn:
        return jsonify({"message": "Connected to database successfully",}, 200)
    else:
        return jsonify({"message": "Connection to database failed"}, 500)
    
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if home.first(globals.cursor):
        flag = 0
        if request.method == 'POST':
            username = request.form.get('username')
            password_1 = request.form.get('password_1')
            password_2 = request.form.get('password_2')
            if password_1 == password_2:
                hashed_password = home.func_bcrypt(password_1)
                home.updatePassword(globals.conn, globals.cursor, username, hashed_password)
                return redirect(url_for('auth.login'))
            else:
                flag = 1
        return render_template('register.html', messages="Your passwords are not the same!", flag=flag)
    else:
        return redirect(url_for('auth.login'))
    
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if home.first(globals.cursor) is False:
        flag = 0
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if home.checkPassword(globals.cursor, username, password):
                session['username'] = username
                print(session['username'])
                #login_logger.info(f"LOGIN SUCCESS | User: {username} | IP: {request.remote_addr}")
                return redirect(url_for('group.group'))
            else:
                flag = 1
                #login_logger.warning(f"LOGIN FAIL: {username} from IP {request.remote_addr} — Wrong password")
        return render_template('login.html', messages='Your password is not correct!', flag=flag)
    else:
        return redirect(url_for('auth.register'))

@auth_bp.route('/logout')
def logout():
    print(session.get('username'))
    session.pop('username', None)
    return redirect(url_for('auth.login'))