import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT id, name, email, is_admin FROM users")

users = cursor.fetchall()

print("Current Users in Database:")
for u in users:
    print(u)

conn.close()
