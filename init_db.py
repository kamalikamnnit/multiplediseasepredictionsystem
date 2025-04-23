import sqlite3

conn = sqlite3.connect('results.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        disease TEXT,
        result TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()
