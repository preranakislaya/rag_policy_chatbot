import sqlite3
import hashlib

DB_NAME = "chatbot.db"

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_connection():

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    return conn


# -----------------------------
# CREATE TABLES
# -----------------------------
def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT

        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# PASSWORD HASHING
# -----------------------------
def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()


# -----------------------------
# CREATE USER
# -----------------------------
def create_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    try:

        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, hashed_password))

        conn.commit()

        return True

    except:

        return False

    finally:

        conn.close()


# -----------------------------
# LOGIN USER
# -----------------------------
def login_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
        AND password = ?
    """, (username, hashed_password))

    user = cursor.fetchone()
    conn.close()
    return user

# -----------------------------
# CREATE CHAT TABLES
# -----------------------------
def create_chat_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # CHAT SESSIONS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_name TEXT,
            vector_id TEXT,
            file_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # MESSAGES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# CREATE NEW CHAT
# -----------------------------
def create_chat_session(user_id, session_name, vector_id = None, file_name = None):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_sessions (user_id, session_name, vector_id, file_name)
        VALUES (?, ?, ?, ?)
    """, (user_id, session_name, vector_id, file_name))

    conn.commit()

    session_id = cursor.lastrowid

    conn.close()

    return session_id


# -----------------------------
# GET USER SESSIONS
# -----------------------------
def get_user_sessions(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM chat_sessions
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    sessions = cursor.fetchall()

    conn.close()

    return sessions


# -----------------------------
# SAVE MESSAGE
# -----------------------------
def save_message(session_id, role, content):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (
            session_id,
            role,
            content
        )
        VALUES (?, ?, ?)
    """, (session_id, role, content))

    conn.commit()
    conn.close()


# -----------------------------
# LOAD MESSAGES
# -----------------------------
def load_messages(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
    """, (session_id,))

    messages = cursor.fetchall()

    conn.close()

    return messages

def clear_chat_messages(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE session_id = ?
    """, (session_id,))

    conn.commit()
    conn.close()