#!/usr/bin/env python
# coding: utf-8

import psycopg2 as db
import hashlib

def get_connection():
    conn = db.connect(
        host="localhost",
        database="cloudbox",
        user="postgres",
        password="khanzode"
    )
    return conn

conn = get_connection()
cur = conn.cursor()


def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS file_metadata (
        file_id SERIAL PRIMARY KEY,
        file_hash TEXT,
        file_name TEXT UNIQUE,
        file_size INTEGER,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_deleted BOOLEAN DEFAULT FALSE,
        restored_from_trash BOOLEAN DEFAULT FALSE
    )
    """)
    conn.commit() 


def get_file_hash(file):
    content = file.read()
    file_size = len(content)
    file_hash = hashlib.sha256(content).hexdigest()
    file.seek(0)
    return file_hash, file_size

def add_entry(filename, file_size, file_hash):
    cur.execute("""
        INSERT INTO file_metadata (file_hash, file_name, file_size) VALUES (%s, %s, %s)
    """, (file_hash, filename, file_size))

    conn.commit()
    print("File metadata inserted in DB")

def update_entry(filename, file_size, file_hash):
    cur.execute("""
        UPDATE file_metadata SET file_size = %s, file_hash = %s WHERE file_name = %s
    """, (file_size, file_hash, filename))

    conn.commit()
    print("File metadata updated in Db")


'''
    0 : file exists and not modified
    1 : file exists but modified
    2 : file doesnt exist
'''

def is_uploaded(filename, file_hash):
    cur.execute("""
        SELECT * FROM file_metadata WHERE file_name = %s
    """, (filename,))
    entry = cur.fetchone()

    if entry is not None:
        print(f"file hash in db: {entry[1]}")
    if entry is None:
            return "new"
    elif entry[1] == file_hash:
        return "duplicate"
    else:
        return "modified"


def move_to_trash(filename):
    cur.execute("""
        UPDATE file_metadata SET is_deleted = TRUE WHERE file_name = %s
    """, (filename,))
    conn.commit()


def restore(filename):
    cur.execute("""
        UPDATE file_metadata SET restored_from_trash = TRUE, is_deleted = FALSE WHERE file_name = %s
    """, (filename,))
    conn.commit()


def hard_delete(filename):
    cur.execute("""
        DELETE FROM file_metadata WHERE file_name = %s
    """, (filename,))
    conn.commit()


def is_in_trash(filename):
    cur.execute("""
        SELECT is_deleted from file_metadata where file_name = %s
    """, (filename,))

    result = cur.fetchone()
    if result is not None:
        return result[0]
    else:
        print("File not found")
        return None

