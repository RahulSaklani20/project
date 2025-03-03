import sqlite3
from datetime import datetime

def reset_credits(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT last_reset_date FROM users WHERE id = ?', (user_id,))
    last_reset_date = c.fetchone()[0]
    if last_reset_date != datetime.now().strftime('%Y-%m-%d'):
        c.execute('UPDATE users SET credits = 20, last_reset_date = ? WHERE id = ?',
                  (datetime.now().strftime('%Y-%m-%d'), user_id))
        conn.commit()
    conn.close()

def deduct_credit(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT credits FROM users WHERE id = ?', (user_id,))
    credits = c.fetchone()[0]
    if user_id == 1:
        conn.close()
        return True
    if credits > 0:
        c.execute('UPDATE users SET credits = credits - 1, credits_used = credits_used + 1 WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def request_credits(user_id, requested_credits):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, requested_credits FROM credit_requests WHERE user_id = ? AND status = "pending"', (user_id,))
    existing_request = c.fetchone()
    if existing_request:
        requested_credits += existing_request[1]
        c.execute('UPDATE credit_requests SET requested_credits = ? WHERE id = ?', (requested_credits, existing_request[0]))
    else:
        c.execute('INSERT INTO credit_requests (user_id, requested_credits) VALUES (?, ?)',
              (user_id, requested_credits))
    conn.commit()
    conn.close()

def approve_credits(request_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT user_id, requested_credits FROM credit_requests WHERE id = ?', (request_id,))
    request = c.fetchone()
    c.execute('UPDATE users SET credits = credits + ? WHERE id = ?',
              (request[1], request[0]))
    c.execute('UPDATE credit_requests SET status = "approved" WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()