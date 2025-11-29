# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/core\data_saver.py
# File Name: data_saver
# @ File: data_saver.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 20:41
"""
desc 6.负责将获取的数据安全地写入SQLite数据库
"""

# core/data_saver.py

import sqlite3
from datetime import datetime
from config.settings import DATABASE_PATH

def save_to_db(data_dict):
    """
    将 {code: {字段}} 格式的数据写入 daily_raw 表
    注意：此处 date 使用当天日期（因为新浪只返回最新日线）
    """
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    for code, info in data_dict.items():
        cursor.execute("""
            INSERT OR REPLACE INTO daily_raw 
            (date, code, open, high, low, close, volume, amount, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            today,
            code,
            info['open'],
            info['high'],
            info['low'],
            info['close'],
            info['volume'],
            info['amount'],
            'sina'
        ))
    conn.commit()
    conn.close()