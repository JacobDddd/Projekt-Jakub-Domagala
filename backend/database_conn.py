import sqlite3
from sqlite3 import Connection

DATABASE_PATH = './backend/database.db'
conn = None

def get_database_connection() -> Connection:
    global conn
    if conn is None:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    else:
        return conn