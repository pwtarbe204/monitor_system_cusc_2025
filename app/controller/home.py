import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from flask import jsonify
import random
from dotenv import load_dotenv
import platform
import subprocess
import bcrypt
from ping3 import ping
import socket
import pyodbc
import pytz
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string

ENV_FILE = '.env'

def is_env_file_empty(file_path):
    return os.path.exists(file_path) and os.path.getsize(file_path) == 0

def is_right_parameters():
    load_dotenv(ENV_FILE, override=True)

    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_DATABASE = os.getenv('DB_DATABASE')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    if db.check_connect(DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME,DB_PASSWORD):
        return True
    return False

def initializeDatabase(conn, cursor, DB_DATABASE):
    
    query = f"""IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{DB_DATABASE}')
                BEGIN
                    CREATE DATABASE {DB_DATABASE};
                END"""
    cursor.execute(query)
    
    conn.commit()

    print('Create Database successfully')

    query_2 = f'USE {DB_DATABASE}'
    cursor.execute(query_2)
    conn.commit()

    # noinspection SqlNoDataSourceInspection
    table_queries = ['''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='group_host' AND xtype='U')
                BEGIN
                    CREATE TABLE group_host 
                    ( group_id INT PRIMARY KEY, 
                    group_name VARCHAR(255) NOT NULL UNIQUE,
                    group_location VARCHAR(255) NOT NULL);
                END''',
                '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='agents' AND xtype='U')
                BEGIN
                    CREATE TABLE agents (
                    agent_id INT IDENTITY(1,1) PRIMARY KEY,
                    agent_name VARCHAR(255) NOT NULL,
                    hostname VARCHAR(255) NOT NULL,
                    host_ip VARCHAR(255) NOT NULL UNIQUE,
                    os VARCHAR(50),
                    agent_status INT,
                    group_id INT, 
                    FOREIGN KEY (group_id) REFERENCES group_host(group_id)
                    );
                END''',''' IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sysinfo' AND xtype='U')
                BEGIN
                    CREATE TABLE sysinfo(
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    timestamp Datetime,
                    cpu_usage decimal(5, 2),
                    ram_usage decimal(5, 2),
                    disk_usage decimal(5, 2),
                    agent_id INT FOREIGN KEY REFERENCES agents(agent_id));
                END''','''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='net_traffic' AND xtype='U')
                BEGIN
                    create table net_traffic (
                    id int identity(1, 1) primary key, 
                    timestamp Datetime,
                    upload FLOAT,
                    download FLOAT,
                    packet_sent FLOAT,
                    packet_recv FLOAT,
                    agent_id INT FOREIGN KEY REFERENCES agents(agent_id));
                    );
                END''','''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='login' AND xtype='U')
                BEGIN
                    create table login (
                        username varchar(255) not null unique, 
                        hashed_password varchar(255) not null unique
                    );
                END''']
    for query in table_queries:
        cursor.execute(query)
        conn.commit()


def addGroupHost(conn, cursor, group_name, location):
    try:
        query = 'INSERT INTO group_host VALUES (?, ?)'
        cursor.execute(query, (group_name, location))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        print(f"Error in addGroupHost: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def addNetTraffic(conn, cursor, data, agent_id):
    try:
        query = 'INSERT INTO net_traffic VALUES (?, ?, ?, ?, ?, ?)'
        cursor.execute(query, (
            data['timestamp'],
            data['sent_speed'],
            data['recv_speed'],
            data['packet_sent'],
            data['packet_recv'],
            agent_id
        ))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        print(f"Error in addNetTraffic: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

#có sửa ngày 12/6
def addSysInfo(conn, cursor, data, agent_id):
    try:
        query = 'INSERT INTO sysinfo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        cursor.execute(query, (
            data['timestamp'],
            data['cpu'],
            data['ram'],
            data['disk'],
            data['ram_total'], 
            data['ram_used'], 
            data['ram_free'], 
            data['disk_total'],
            data['disk_used'],
            agent_id
        ))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        print(f"Error in addSysInfo: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def addAgent(conn, cursor, data):
    ip = data['host_ip']
    query = '''IF NOT EXISTS (SELECT 1 FROM agents WHERE host_ip = ?)
                BEGIN
                INSERT INTO agents (agent_name, hostname, host_ip, os, agent_status)
                VALUES (?, ?, ?, ?, ?)
                END'''
    cursor.execute(query, (ip, data['agent_name'], data['hostname'], data['host_ip'], data['os'], data['status'], ))
    conn.commit()

def addAgentHostname(conn, cursor, data):
    hostname = data['hostname']
    query = '''IF NOT EXISTS (SELECT 1 FROM agents WHERE hostname = ?)
                BEGIN
                INSERT INTO agents (agent_name, hostname, host_ip, os, agent_status)
                VALUES (?, ?, ?, ?, ?)
                END'''
    cursor.execute(query, (hostname, data['agent_name'], data['hostname'], data['host_ip'], data['os'], data['status'], ))
    conn.commit()

    ip = data['host_ip']
    query = '''UPDATE agents SET host_ip = ? where hostname = ?'''
    cursor.execute(query, (ip, hostname))
    conn.commit()

def addAgentIntoGroup(conn, cursor, group_id, agent_id):
    query = 'update agents set group_id = ? where agent_id = ?'
    cursor.execute(query, (group_id, agent_id))
    conn.commit()

def getNetTraffic(cursor, agent_id):
    query = 'select * from net_traffic where agent_id = ?'
    cursor.execute(query, (agent_id))
    data = cursor.fetchall()
    return {
        "id": [i[0] for i in data],
        "time": [i[1] for i in data],
        "upload": [i[2] for i in data],
        "download": [i[3] for i in data],
        "packet_sent": [i[4] for i in data],
        "packet_recv": [i[5] for i in data]
    }
def getGroupHost(cursor):
    query = 'select * from group_host'
    cursor.execute(query)
    data = cursor.fetchall()
    return {
        "id": [i[0] for i in data],
        "group_name": [i[1] for i in data],
        "location": [i[2] for i in data]
    }


def getAllData(cursor):
    try:
        query = '''SELECT *
                    FROM (
                        SELECT *,
                            ROW_NUMBER() OVER (PARTITION BY agent_id ORDER BY timestamp DESC) AS rn
                        FROM sysinfo
                    ) AS ranked
                    join agents on agents.agent_id = ranked.agent_id
                    WHERE rn = 1;'''
        cursor.execute(query)
        data = cursor.fetchall()
        all_data = []
        for i in data:
            group = getGroupName(cursor, i[18])
            dt = {
                'time':i[1],
                'cpu': i[2],
                'ram': i[3],
                'disk': i[4],
                'hostname': i[14],
                'ip': i[15],
                'status': i[17],
                'group_id': i[18],
                'groupname': group['group_name'],
                'grouplocation': group['group_location'],
                'agent_id': i[10]
            }
            all_data.append(dt)
        return jsonify(all_data)
    except Exception as e:
        print(f"Error in addNetTraffic: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
    
def getGroupName(cursor, group_id):
    query = 'select group_name, group_location from group_host where group_id = ?'
    cursor.execute(query, (group_id))
    data = cursor.fetchall()
    if data:
        return {
            'group_name': data[0][0],
            'group_location': data[0][1]
        }
    else:
        return {
        'group_name': 'None',
        'group_location': 'None'
    }

def getAgents(cursor):
    query = 'select * from agents'
    cursor.execute(query)
    result = cursor.fetchall()

    return {
        "id": [r[0] for r in result],
        "agent-name": [r[1] for r in result],
        "hostname": [r[2] for r in result],
        "ip": [r[3] for r in result],
        "os": [r[4] for r in result],
        "status": [r[5] for r in result],
        "group_id": [r[6] for r in result]
    }

def getAgentById(cursor, agent_id):
    query = 'select * from agents where agent_id = ? '
    cursor.execute(query, (agent_id,))
    r = cursor.fetchall()

    return {
        "id": r[0][0],
        "agent-name": r[0][1],
        "hostname": r[0][2],
        "ip": r[0][3],
        "os": r[0][4],
        "status": r[0][5],
        "group_id": r[0][6]
    }
#-------------------------------#
def getAgentsInGroup(cursor, group_id):
    query = '''select * from agents 
                join group_host on group_host.group_id = agents.group_id
                where group_host.group_id=?'''
    cursor.execute(query, (group_id,))
    data = cursor.fetchall()

    all_data = []
    for i in data:
        dt = {
            'agent_id':i[0],
            'hostname': i[2],
            'ip': i[3],
            'status': i[5],
            'group_id': i[6],
            'groupname': i[8],
            'grouplocation': i[9]
        }
        all_data.append(dt)

    return all_data
#-------------------------------#
def getAgentIdFromIp(cursor, ip):
    try:
        if cursor is None:
            raise ValueError("Database cursor is None. Make sure it's initialized.")
        query = 'SELECT agent_id FROM agents WHERE host_ip = ?'
        cursor.execute(query, (ip,))
        result = cursor.fetchall()
        if result:
            return {
                'id': [r[0] for r in result]
            }
        else:
            return {
                'id': 0
            }
    except Exception as e:
        return {
            'id': 0,
            'error': str(e)
        }
def getAgentIdFromHostname(cursor, hostname):
    try:
        if cursor is None:
            raise ValueError("Database cursor is None. Make sure it's initialized.")
        query = 'SELECT agent_id FROM agents WHERE hostname = ?'
        cursor.execute(query, (hostname,))
        result = cursor.fetchall()
        if result:
            return {
                'id': [r[0] for r in result]
            }
        else:
            return {
                'id': 0
            }
    except Exception as e:
        return {
            'id': 0,
            'error': str(e)
        }

def getSysinfo(cursor, id):
    query = 'select * from sysinfo where agent_id = ?'
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    return {
        "id": [r[0] for r in result],
        "timestamp_2": [r[1] for r in result],
        "cpu": [r[2] for r in result],
        "ram": [r[3] for r in result],
        "disk": [r[4] for r in result],
        "ram_total": [r[6] for r in result],
        "ram_used": [r[7] for r in result],
        "ram_free": [r[8] for r in result], 
       "disk_total": [r[9] for r in result],
       "disk_used": [r[10] for r in result] 
    }

def deleteAgent(conn, cursor, id):
    query_2 = 'update agents set group_id = NULL where agent_id = ?'
    cursor.execute(query_2, (id, ))
    conn.commit()

# delete from net_traffic where agent_id = 7033
# delete from sysinfo where agent_id = ?
# delete from agents where agent_id = ?

def removeAgent(conn, cursor, id):
    query = 'delete from net_traffic where agent_id = ?'
    cursor.execute(query, (id, ))
    conn.commit()

    query = 'delete from sysinfo where agent_id = ?'
    cursor.execute(query, (id, ))
    conn.commit()

    query = 'delete from agents where agent_id = ?'
    cursor.execute(query, (id, ))
    conn.commit()

def deleteGroup(conn, cursor, group_id):
    query_1 = 'update agents set group_id = NULL where group_id = ?'
    query_2 = 'delete from group_host where group_id = ?'
    cursor.execute(query_1, (group_id, ))
    conn.commit()
    cursor.execute(query_2, (group_id, ))
    conn.commit()

def checkAdmin(cursor):
    query = 'select 1 from login where username = ? and hashed_password = ?'
    cursor.execute(query, ('admin', 'admin'))
    if cursor.fetchall():
        return False
    return True



def first(cursor):
    cursor.execute('''SELECT 1 FROM login''')
    return cursor.fetchone() is None

def updatePassword(conn, cursor, username, password):
    query = 'delete from login'
    cursor.execute(query)
    conn.commit()


    query = 'insert into login values (?, ?)'
    cursor.execute(query, (username, password, ))
    conn.commit()

def getColum(cursor):
    query = 'select COUNT(group_id) from group_host'
    cursor.execute(query)
    data = cursor.fetchall()
    return data[0][0]

def is_active(ip):
    try:
        output = subprocess.check_output(["ping", "-n", "1", "-w", "1000", ip], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def getInfo():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return {
        "ip": ip
    }

def getServer(cursor):
    data = getInfo()
    ip = data['ip']
    query = '''select agent_id from agents where host_ip = ?'''
    cursor.execute(query, (ip,))
    data = cursor.fetchall()
    if data == []:
        return 0
    else:
        return data[0][0]
    
def number_of_agent_in_Group(cursor, group_id):
    query = 'select count(group_id) from agents where group_id = ?'
    cursor.execute(query, (group_id))
    data = cursor.fetchone()
    return data[0]


def updateStatus(conn, cursor):
    query = '''SELECT *
                    FROM (
                        SELECT *,
                            ROW_NUMBER() OVER (PARTITION BY agent_id ORDER BY timestamp DESC) AS rn
                        FROM sysinfo
                    ) AS ranked
                    join agents on agents.agent_id = ranked.agent_id
                    WHERE rn = 1;'''
    cursor.execute(query)
    data = cursor.fetchall()
    for i in data:
        dt = {
            'agent_id': i[10], 
            'lastest': i[1]
        }
        query = 'update agents set agent_status = ? where agent_id = ?'
        if checkStatus(dt['lastest']):
            cursor.execute(query, (0, dt['agent_id']))
        else:
            cursor.execute(query, (1, dt['agent_id']))
        conn.commit()

def checkStatus(time):
    time_format = "%Y-%m-%d %H:%M:%S"
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

    lastest_time = vn_tz.localize(datetime.strptime(str(time), time_format))
    current_time = datetime.now(vn_tz)

    delta_time = current_time - lastest_time
    delta_seconds = abs(int(delta_time.total_seconds()))

    return delta_seconds > 30


def func_bcrypt(password):
    salt = bcrypt.gensalt(rounds=15)
    return bcrypt.hashpw(password.encode('utf-8'), salt)

#++++++++++++++++++++++++++++++



def addGmail(conn, cursor, gmail):
    try:
        # Kiểm tra trùng email
        cursor.execute("SELECT 1 FROM gmail WHERE gmail = ?", (gmail,))
        if cursor.fetchone():
            print("Email already exists.")
            return False
        otp = ''.join(random.choice(string.digits) for _ in range(5))
        cursor.execute(
            "INSERT INTO gmail (gmail, otp, gmail_status) VALUES (?, ?, ?)",
            (gmail, otp, 0)
        )
        conn.commit()
        print("Email added successfully.")
        content = f'You have successfully registered this email for system alerts, all system related alerts will be sent to you in the future.\nYour OTP is: {otp}'
        sendEmail(content, gmail)
        return True
    except Exception as e:
        print(f"Error adding email: {e}")
        conn.rollback()
        return False

def deleteGmail(conn, cursor, gmail_id):
    getEmail(cursor)
    cursor.execute('delete from gmail where gmail_id = ?', (gmail_id,))
    conn.commit()
    print('Email deleted successfully.')
    return True

def sendEmail(content, email_receiver):
    sender_email = 'hehehehehehehehe2004@gmail.com'
    sender_password = 'wvzh mpdx eopp dekl'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Babbix System'
    msg['From'] = sender_email
    msg['To'] = email_receiver

    part = MIMEText(content, 'html')
    msg.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Khởi tạo kết nối bảo mật TLS
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_receiver, msg.as_string())
            print('[+] Gửi email thành công!')
    except Exception as e:
        print('[!] Gửi email không thành công!', e)

def getEmail(cursor):
    cursor.execute('select * from gmail')
    raw_data = cursor.fetchall()
    data = []
    for i in raw_data:
        dt = {
            'gmail_id' : i[0],
            'gmail': i[1],
            'status': i[3]
        }
        data.append(dt)
    return data

def getOTP(cursor, gmail_id):
    cursor.execute('select otp from gmail where gmail_id = ?', (gmail_id, ))
    return cursor.fetchone()

def updateEmail(conn, cursor, gmail_id):
    cursor.execute('update gmail set gmail_status = 1 where gmail_id = ?', (gmail_id, ))
    conn.commit()

def sendAlerts(cursor, content):
    cursor.execute('select * from gmail where gmail_status = 1')
    raw_data = cursor.fetchall()
    data = []
    for i in raw_data:
        data.append(i[1])
    for i in data:
        sendEmail(content, i)


def checkPassword(cursor, username, password):
    query = 'select hashed_password from login where username=?'
    cursor.execute(query, (username))
    password_bytes = password.encode('utf-8')
    password = cursor.fetchall()
    if password != []:
        if bcrypt.checkpw(password_bytes, password[0][0].encode('utf-8')):
            print('correct')
            return True
    print('incorrect')
    return False

def checkTwoPasswords(p1, p2):
    return p1 == p2

def changePassword(conn, cursor, username, new_password):
    hashed_password = func_bcrypt(new_password)
    query = 'update login set hashed_password = ? where username = ?'
    cursor.execute(query, (hashed_password, username))
    conn.commit()
    print('Password changed successfully.')
    return True
#----------------------------------------------

def addUrl(conn, cursor, url, agent_id):
    cursor.execute('insert into checker (url, agent_id, status) values (?, ?, ?)', (url,agent_id, 'pending'))
    conn.commit()

def getUrl(cursor):
    cursor.execute('''select top(1) * from checker where status = ? order by id desc''', ('pending', ))
    data = cursor.fetchall()
    return {
        'id': [d[0] for d in data],
        'url': [d[1] for d in data],
        'status': [d[3] for d in data],
        'agent_id' : [d[4] for d in data]
    }

def addResultIntoUrl(conn, cursor, id, rrt):
    cursor.execute('update checker set status = ?, rrt = ? where id = ?', ('checked', rrt, id))
    conn.commit()

def getUrlById(cursor, agent_id):
    cursor.execute('select top(1) * from checker where agent_id = ? order by id desc', (agent_id,))
    
    data = cursor.fetchone()
    return {
        'url': data[1],
        'rrt': data[2],
        'status': data[3],
        'agent_id': data[4]
    }

def getAllDataUrl(cursor, agent_id):
    cursor.execute('''select * from agents join group_host on agents.group_id = group_host.group_id where agent_id = ?''', (agent_id,))
    data = cursor.fetchone()
    cursor.execute('select top(1) * from checker where agent_id = ? order by id desc', (agent_id,))
    data_2 = cursor.fetchone()
    return {
        'agent_id': data[0],
        'agent_name': data[1],
        'hostname': data[2],
        'host_ip': data[3],
        'os': data[4],
        'agent_status': data[5],
        'group_id': data[6],
        'group_name': data[7],
        'group_location': data[8],
        'id': data_2[0],
        'url': data_2[1],
        'rrt': data_2[2],
        'status': data_2[3]
    }