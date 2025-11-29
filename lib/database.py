# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/lib\database.py
# File Name: database
# @ File: database.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 21:30
"""
desc 
"""
# lib/database.py

import sqlite3
from config.settings import DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def save_daily_raw(data_list):
    """批量保存原始行情数据"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.executemany("""
            INSERT OR REPLACE INTO daily_raw 
            (date, code, open, high, low, close, volume, amount, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data_list)