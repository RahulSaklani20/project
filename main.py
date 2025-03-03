import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
sqliteConnection = sqlite3.connect('database.db')
c = sqliteConnection.cursor()
print('DB Init')
# write commad to change password where id is 1

# password = generate_password_hash('admin')
# c.execute('''alter table users add column role TEXT DEFAULT 'user' ''')
c.execute('''ALTER TABLE users ADD COLUMN credits_used INTEGER DEFAULT 0''')

# conn.commit()
# conn.close()
# conn.commit()
# conn.close()
query = 'SQL query;'
# c.execute(query)
result = c.fetchall()
print('SQLite Version is {}'.format(result))
sqliteConnection.commit()
sqliteConnection.close()