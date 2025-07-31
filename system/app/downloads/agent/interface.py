import tkinter as tk
from tkinter import ttk, messagebox
import requests
from urllib.parse import urljoin
from dotenv import set_key, load_dotenv
import os
import sys
from pathlib import Path
       
# Đường dẫn đến file .env (có thể thay đổi nếu đặt ở nơi khác)
# env_file = os.path.join(Path(__file__).parent, '.env')
#env_file = os.path.join(os.path.dirname(sys.executable), '.env')

if getattr(sys, 'frozen', False):
    # Nếu chạy từ .exe
    env_file = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    # Nếu chạy từ script .py
    env_file = os.path.join(os.path.dirname(__file__), '.env')

def check_connection():
    ip = ip_entry.get().strip()
    if not ip:
        messagebox.showwarning("Lỗi", "Bạn chưa nhập địa chỉ IP.")
        return False  # ❌ Chưa nhập IP

    if not ip.endswith("/"):
        ip += "/"

    try:
        response = requests.get(urljoin(ip, "ping"), timeout=3)
        data = response.json()

        # Ghi vào file .env
        key = 'SERVER'
        value = ip
        set_key(env_file, key, value)

        print(f"Đã cập nhật biến {key} trong file {env_file}")
        messagebox.showinfo("Kết quả", f"Phản hồi từ server:\n{data}")

        # ✅ Load lại để chuẩn bị return từ setup()
        load_dotenv(env_file)
        global SERVER_VALUE
        SERVER_VALUE = os.getenv("SERVER")

        return True  # ✅ Kết nối thành công
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không kết nối được đến server:\n{e}")
        return False  # ❌ Kết nối thất bại

def setup():
    global root, ip_entry
    result = {"confirmed": False}

    def on_closing():
        root.destroy()  # Đóng GUI
        result["confirmed"] = False  # Gán lại cờ

    root = tk.Tk()
    root.title("Kết nối đến Server")
    root.geometry("400x180")
    root.resizable(False, False)

    root.protocol("WM_DELETE_WINDOW", on_closing)  # Bắt sự kiện tắt cửa sổ

    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 10))
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TEntry", font=("Segoe UI", 10))

    ttk.Label(root, text="Nhập địa chỉ IP của server:", font=("Segoe UI", 11, "bold")).pack(pady=(20, 5))
    ip_entry = ttk.Entry(root, width=40)

    if os.path.getsize(env_file) > 0:
        load_dotenv(env_file)
        server = os.getenv('SERVER')
        if server:
            ip_entry.insert(0, server)
    ip_entry.pack(pady=5)

    def confirm_and_close():
        if check_connection():  # ✅ Chỉ khi kết nối thành công
            result["confirmed"] = True
            root.destroy()

    ttk.Button(root, text="Kiểm tra kết nối", command=confirm_and_close).pack(pady=10)

    root.mainloop()
    return result["confirmed"]