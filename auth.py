import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                  (username, generate_password_hash(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[2], password):
        return {'id': user[0], 'username': user[1], 'role': user[3]}
    return None

def get_user_profile(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return {'username': user[1], 'credits': user[4]}