import sqlite3
import hashlib
from database_conn import get_database_connection

conn = get_database_connection()

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(conn=conn, username=None, password=None, email=None, phone=None):
    """Adds a new user to the database with exception handling for too long values."""
    hashed_password = hash_password(password)
    if len(username) > 60:
        raise ValueError("Username cannot be longer than 60 characters.")
    if len(email) > 200:
        raise ValueError("Email cannot be longer than 200 characters.")
    if len(password) > 120:
        raise ValueError("Password cannot be longer than 120 characters.")

    if phone is None or email is None or password is None or username is None:
        raise ValueError("All fields must be filled.")

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO USERS (Username, PasswordHash, Email, Phone)
            VALUES (?, ?, ?, ?)
            """,
            (username, hashed_password, email, phone),
        )

        conn.commit()
        print(f"User {username} added successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error adding user: {e}")
        raise e

def get_user(conn, username):
    """Retrieves user information by username."""

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT ID, Username, Email, Phone
            FROM USERS
            WHERE Username = ?
            """,
            (username,),
        )
        user = cursor.fetchone()

        if user:
            return {
                "ID": user[0],
                "Username": user[1],
                "Email": user[2],
                "Phone": user[3],
            }
        else:
            print("User not found.")
            return None
    except sqlite3.Error as e:
        print(f"Error retrieving user: {e}")
        return None

def get_user_with_verification(conn = conn, username = None, password = None):
    """Retrieves user information by username and password."""
    try:
        cursor = conn.cursor()
        # Verify if password matches hash
        if verify_user(conn, username, password):
            try:
                cursor.execute(
                    """
                    SELECT ID, Username, Email, Phone
                    FROM USERS
                    WHERE Username = ?
                    """,
                    (username,),
                )
                user = cursor.fetchone()
                if user:
                    return {
                        "ID": user[0],
                        "Username": user[1],
                        "Email": user[2],
                        "Phone": user[3],
                    }
                else:
                    print("User not found.")
                    return None
            except sqlite3.Error as e:
                print(f"Error retrieving user: {e}")
                return None
        else:
            return None
    except sqlite3.Error as e:
        print(f"Error retrieving user: {e}")
        return None

def verify_user(conn=conn, username=None, password=None):
    """Verifies if the username and password are correct."""
    hashed_password = hash_password(password)
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT PasswordHash
            FROM USERS
            WHERE Username = ?
            """,
            (username,),
        )
        result = cursor.fetchone()

        if result and result[0] == hashed_password:
            print("User verified successfully.")
            return True
        else:
            print("Invalid username or password.")
            return False
    except sqlite3.Error as e:
        print(f"Error verifying user: {e}")
        return False