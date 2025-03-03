import sqlite3

def get_analytics():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('select * from scans')
    scans = c.fetchall()
    print(scans)
    c.execute('SELECT username, COUNT(scans.id) FROM users LEFT JOIN scans ON users.id = scans.user_id GROUP BY users.id')
    scan_stats = c.fetchall()
    # print(scan_stats)
    c.execute('SELECT username, SUM(requested_credits) FROM credit_requests JOIN users ON credit_requests.user_id = users.id WHERE status = "approved" GROUP BY users.id')
    credit_stats = c.fetchall()
    c.execute('select username, credits_used from users where id = users.id')
    credits_used = c.fetchall()
    print(
        credits_used
    )
    conn.close()
    return {'scan_stats': scan_stats, 'credit_stats': credits_used}