import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

import pytest
import sqlite3
from user_verification import hash_password, add_user, get_user, verify_user
import hashlib


TEST_DATABASE_PATH = "./backend/database.db"
conn = sqlite3.connect(TEST_DATABASE_PATH)

def test_hash_password():
    password = "password123"
    hashed = hash_password(password)
    assert hashed == hashlib.sha256(password.encode()).hexdigest()

def test_add_user():
    try:
        add_user(conn, "testuser", "password123", "test@example.com", "1234567890")
    except sqlite3.IntegrityError:
        pass
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS WHERE Username = ?", ("testuser",))
    user = cursor.fetchone()
    assert user is not None
    assert user[1] == "testuser"

def test_add_user_duplicate():
    with pytest.raises(sqlite3.IntegrityError):
        add_user(conn, "testuser", "password123", "test@example.com", "1234567890")

def test_get_user():
    try:
        add_user(conn, "testuser", "password123", "test@example.com", "1234567890")
    except sqlite3.IntegrityError:
        pass
    user = get_user(conn, "testuser")
    assert user is not None
    assert user["Username"] == "testuser"

def test_get_user_nonexistent():
    user = get_user(conn, "nonexistentuser")
    assert user is None

def test_verify_user():
    try:
        add_user(conn, "testuser", "password123", "test@example.com", "1234567890")
    except sqlite3.IntegrityError:
        pass
    assert verify_user(conn, "testuser", "password123") is True

def test_verify_user_wrong_password():
    try:
        add_user(conn, "testuser", "password123", "test@example.com", "1234567890")
    except sqlite3.IntegrityError:
        pass
    assert verify_user(conn, "testuser", "wrongpassword") is False

def test_verify_user_nonexistent():
    assert verify_user(conn, "nonexistentuser", "password123") is False
