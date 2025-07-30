from flask import session, redirect, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:  # Đổi key theo session bạn dùng
            return redirect(url_for('auth.login'))  # Đảm bảo 'auth.login' đúng với route login của bạn
        return f(*args, **kwargs)
    return decorated_function
