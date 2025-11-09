import sqlite3

conn = sqlite3.connect('D:/Users/CNSHO/Documents/GitHub/Natpudan-/physician_ai.db')
cursor = conn.cursor()

print("=== Database Tables ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables] if tables else "No tables found")
print()

print("=== chat_sessions table schema ===")
cursor.execute('PRAGMA table_info(chat_sessions)')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"{row[1]:25} {row[2]:15}")
else:
    print("No columns found!")

print("\n=== chat_messages table schema ===")
cursor.execute('PRAGMA table_info(chat_messages)')
rows = cursor.fetchall()
for row in rows:
    print(f"{row[1]:25} {row[2]:15}")

conn.close()
