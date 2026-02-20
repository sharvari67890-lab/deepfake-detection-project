# database.py

import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------ DATABASE CONFIG ------------------
DB_FILE = "database.db"

# ------------------ INITIALIZE DATABASE ------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)

    # Media table
    cursor.execute("""
   CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    file_type TEXT,
    file_data BLOB,
    verdict TEXT,
    fake_score REAL,
    real_score REAL,
    uploaded_by TEXT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


    
    # Text table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS text_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            message TEXT,
            verdict TEXT,
            date TEXT
        )
    """)
    

    

    conn.commit()
    conn.close()

# ------------------ USER FUNCTIONS ------------------
def create_user(name, email, password, is_admin=0):
    """Creates a new user with hashed password"""
    hashed_pw = generate_password_hash(password)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?)",
            (name, email, hashed_pw, is_admin)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    """Verifies user credentials, returns user dict if correct"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password, is_admin FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row and check_password_hash(row[3], password):
        return {"id": row[0], "name": row[1], "email": row[2], "is_admin": row[4]}
    return None

def get_user_by_email(email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, is_admin FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "email": row[2], "is_admin": row[3]}
    return None

def reset_password(email, temp_password):
    hashed_pw = generate_password_hash(temp_password)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed_pw, email))
    conn.commit()
    conn.close()

# ------------------ MEDIA FUNCTIONS ------------------
# def save_media_file(filename, file_type, file_bytes, verdict, fake_score, real_score, uploaded_by=None):
#     """
#     Save media bytes and metadata directly to DB (no file saved to disk)
#     Returns the database ID of saved media
#     """
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
#     cursor.execute("""
#     INSERT INTO media 
#     (filename, file_type, verdict, fake_score, real_score, upload_time, uploaded_by, file_bytes)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
# """, (
#     filename,
#     file_type,
#     verdict,
#     fake_score,
#     real_score,
#     timestamp,
#     uploaded_by,
#     file_bytes
# ))

#     conn.commit()
#     conn.close()

#     return media_id

def save_media_file(filename, file_type, file_bytes, verdict, fake_score, real_score, uploaded_by):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO media 
        (filename, file_type, file_data, verdict, fake_score, real_score, uploaded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (filename, file_type, file_bytes, verdict, fake_score, real_score, uploaded_by))

    media_id = cursor.lastrowid   # ✅ THIS FIXES BOTH IMAGE & VIDEO

    conn.commit()
    conn.close()

    return media_id


def get_media_file(file_id):
    """
    Fetch media bytes and filename for serving
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT file_bytes, filename FROM media WHERE id=?", (file_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {"file_data": row[0], "filename": row[1]}
    return None

def get_all_media():
    """
    Fetch all media records for history
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, file_type, verdict, fake_score, real_score, upload_time
        FROM media
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# ------------------ TEXT HISTORY ------------------
def save_text_result(email, message, verdict):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    masked_message = "User text hidden for privacy"
    cursor.execute("""
        INSERT INTO text_history (user_email, message, verdict, date)
        VALUES (?, ?, ?, ?)
    """, (email, masked_message, verdict, formatted_time))

    conn.commit()
    conn.close()

def get_user_text_history(email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, substr(message,1,20) || '....' as message_preview, verdict, substr(date,1,19) as date
        FROM text_history
        WHERE user_email=?
        ORDER BY id DESC
    """, (email,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_user_media(email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, file_type, verdict, fake_score, real_score, upload_time
        FROM media
        WHERE uploaded_by=?
        ORDER BY id DESC
    """, (email,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ------------------ ADMIN FUNCTIONS ------------------
def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, is_admin FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_text_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_email, message, verdict, date FROM text_history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def delete_text_record(record_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM text_history WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
