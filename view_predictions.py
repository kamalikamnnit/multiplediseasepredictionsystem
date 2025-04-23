import sqlite3

conn = sqlite3.connect('results.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables in database:", cursor.fetchall())

cursor.execute("SELECT * FROM predictions")
rows = cursor.fetchall()

if rows:
    for row in rows:
        print(row)
else:
    print("No prediction data found.")

conn.close()
