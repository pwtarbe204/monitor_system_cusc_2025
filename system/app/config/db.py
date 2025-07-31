import pyodbc
from dotenv import load_dotenv
import os

def connect(DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD):
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={DB_HOST},{DB_PORT};'
            f'DATABASE={DB_DATABASE};'
            f'UID={DB_USERNAME};'
            f'PWD={DB_PASSWORD};'
            'Trusted_Connection=no;'
        )
        cursor = conn.cursor()
        return conn, cursor
    except pyodbc.Error as e:
        print("Database connection error:", e)
        return None
    
def check_connect(DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD):
    try:
        pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={DB_HOST},{DB_PORT};'
            f'DATABASE={DB_DATABASE};'
            f'UID={DB_USERNAME};'
            f'PWD={DB_PASSWORD};'
            'Trusted_Connection=no;'
        )
        return True
    except pyodbc.Error as e:
        print("Database connection error:", e)
        return False


def initializeDatabase(conn, cursor, DB_DATABASE):
    #conn, cursor = connect(os.getenv('DB_SERVER'), os.getenv('DB_PORT'), os.getenv('DB_NAME'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'))  
    conn.autocommit = True
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
                    ( group_id INT IDENTITY(1,1) PRIMARY KEY, 
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
                    ram_total BIGINT,
                    ram_used BIGINT,
                    ram_free BIGINT,
                    disk_total BIGINT,
                    disk_used BIGINT,
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
                END''','''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='login' AND xtype='U')
                BEGIN
                    create table login (
                        username varchar(255) not null unique, 
                        hashed_password varchar(255) not null unique
                    );
                END''', '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='gmail' AND xtype='U')
                BEGIN
                    create table gmail (
                        gmail_id int identity(1, 1) primary key,
                        gmail varchar(255) not null unique, 
                        otp int,
                        gmail_status int
                    );
                END''']

    conn.autocommit = True
    for query in table_queries:
        cursor.execute(query)
        conn.commit()
        print('Create table successfully')

    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
    tables = cursor.fetchall()

    # Ghi vào file
    with open("table_name.txt", "w", encoding="utf-8") as f:
        for table in tables:
            f.write(f"{table.TABLE_NAME}\n")
    conn.close()
