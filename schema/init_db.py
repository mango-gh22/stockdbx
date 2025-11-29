# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/schema\init_db.py
# File Name: init_db
# @ File: init_db.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 20:42
"""
desc 初始化数据库结构。
"""
import sqlite3
from config.settings import DATABASE_PATH

def init_db():
    """
    初始化数据库表结构
    :return: None
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_raw (
            date        TEXT     NOT NULL,
            code        TEXT     NOT NULL,
            open        REAL,
            high        REAL,
            low         REAL,
            close       REAL,
            volume      INTEGER,
            amount      REAL,
            source      TEXT DEFAULT 'sina',
            updated_at  TEXT DEFAULT (datetime('now', 'localtime')),
            PRIMARY KEY (date, code)
        );
    """)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")