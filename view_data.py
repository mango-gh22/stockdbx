# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx\view_data.py
# File Name: view_data
# @ File: view_data.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 20:57
"""
desc 临时快速查询
"""

# view_data.py
# _*_ coding: utf-8 _*_

import sqlite3
from config.settings import DATABASE_PATH
from datetime import datetime


def main():
    print("🔍 正在连接数据库:", DATABASE_PATH)

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()

        # 检查表是否存在
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_raw';")
        if not cur.fetchone():
            print("❌ 表 daily_raw 不存在！请先运行 run_init.py")
            return

        # 获取最新日期
        cur.execute("SELECT MAX(date) FROM daily_raw;")
        latest_date = cur.fetchone()[0]
        print(f"\n📌 数据库最新日期: {latest_date}")

        if not latest_date:
            print("⚠️  daily_raw 表为空")
            return

        # 查询该日期的前5条记录
        print(f"\n📊 {latest_date} 的前5条行情数据:")
        cur.execute("""
            SELECT date, code, open, high, low, close, volume 
            FROM daily_raw 
            WHERE date = ? 
            ORDER BY code 
            LIMIT 5
        """, (latest_date,))

        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print("⚠️  该日期无数据")

        # 统计总记录数
        cur.execute("SELECT COUNT(*) FROM daily_raw;")
        total = cur.fetchone()[0]
        print(f"\n📈 daily_raw 总记录数: {total}")

        conn.close()

    except Exception as e:
        print("❌ 数据库错误:", e)


if __name__ == "__main__":
    main()

