import sqlite3

conn = sqlite3.connect('natpudan.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("=== Database Tables ===")
for table in tables:
    print(f"  - {table[0]}")

# Check users table
try:
    cursor.execute("SELECT id, email, full_name, role FROM users ORDER BY id DESC LIMIT 10")
    users = cursor.fetchall()
    print("\n=== Recent Users ===")
    for user in users:
        print(f"ID {user[0]}: {user[1]} ({user[2]}) - Role: {user[3]}")
except sqlite3.OperationalError as e:
    print(f"\nError querying users: {e}")

conn.close()
