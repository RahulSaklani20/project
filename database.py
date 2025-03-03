import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



def init_db():
    print("init_db")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    credits INTEGER DEFAULT 20,
                    credits_used INTEGER DEFAULT 0,
                    last_reset_date TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    upload_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS credit_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    requested_credits INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    document_id INTEGER NOT NULL,
                    scan_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )''')
    password = 'admin'
    # password_hash = hashlib.sha256(password.encode()).hexdigest()

    password = generate_password_hash(password)
    c.execute('''INSERT INTO users (username, password_hash, role, credits, last_reset_date)
                VALUES (?, ?, ?, ?, ?)''',
                ('admin', password, 'admin', 100, '2023-01-01'))
    # conn.commit()
    # conn.close()
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect('database.db')