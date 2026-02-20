import sqlite3

# Connect to your database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Fetch all media records
cursor.execute("SELECT * FROM media")
rows = cursor.fetchall()

if not rows:
    print("No media records found.")
else:
    print("Media records in database:")
    for row in rows:
        print(row)

conn.close()
