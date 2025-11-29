# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/core\adjuster.py
# File Name: adjuster
# @ File: adjuster.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 21:29
"""
desc 功能：按需计算前复权价格（使用 daily_raw + dividend）
"""

# core/adjuster.py

import sqlite3
import pandas as pd
from datetime import datetime
from config.settings import DATABASE_PATH


def calculate_qfq_factor(code: str) -> pd.DataFrame:
    """
    计算某只股票的每日前复权因子
    返回: DataFrame with columns ['date', 'qfq_factor']
    """
    conn = sqlite3.connect(DATABASE_PATH)

    # 1. 获取原始行情日期（倒序）
    price_df = pd.read_sql_query(
        "SELECT date FROM daily_raw WHERE code=? ORDER BY date DESC",
        conn, params=(code,)
    )
    if price_df.empty:
        conn.close()
        return pd.DataFrame()

    # 2. 获取分红记录（倒序）
    div_df = pd.read_sql_query(
        "SELECT ex_date, div_cash, bonus_share, trans_share FROM dividend WHERE code=? ORDER BY ex_date DESC",
        conn, params=(code,)
    )
    conn.close()

    if div_df.empty:
        # 无分红，则复权因子=1.0
        price_df['qfq_factor'] = 1.0
        return price_df[['date', 'qfq_factor']]

    # 3. 从最新日开始，倒推复权因子
    factors = []
    current_factor = 1.0
    div_idx = 0
    div_dates = div_df['ex_date'].tolist()

    for _, row in price_df.iterrows():
        trade_date = row['date']
        # 若当日或之后有除权日，则应用该次分红
        while div_idx < len(div_dates) and trade_date <= div_dates[div_idx]:
            # 应用分红：factor *= (1 + 送股 + 转增)
            bonus = div_df.iloc[div_idx]['bonus_share']
            trans = div_df.iloc[div_idx]['trans_share']
            current_factor *= (1 + bonus + trans)
            div_idx += 1
        factors.append(current_factor)

    price_df['qfq_factor'] = factors
    return price_df[['date', 'qfq_factor']]


def generate_daily_adj_for_code(code: str):
    """
    为单只股票生成前复权日线，并写入 daily_adj 表
    """
    conn = sqlite3.connect(DATABASE_PATH)

    # 获取原始行情
    raw_df = pd.read_sql_query(
        "SELECT date, open, high, low, close, volume FROM daily_raw WHERE code=? ORDER BY date",
        conn, params=(code,)
    )
    if raw_df.empty:
        conn.close()
        return

    # 获取复权因子
    factor_df = calculate_qfq_factor(code)
    if factor_df.empty:
        conn.close()
        return

    # 合并
    merged = pd.merge(raw_df, factor_df, on='date', how='left')
    merged['qfq_factor'].fillna(method='bfill', inplace=True)  # 用未来因子填充（前复权逻辑）
    merged['qfq_factor'].fillna(1.0, inplace=True)

    # 计算复权价
    merged['qfq_open'] = merged['open'] * merged['qfq_factor']
    merged['qfq_high'] = merged['high'] * merged['qfq_factor']
    merged['qfq_low'] = merged['low'] * merged['qfq_factor']
    merged['qfq_close'] = merged['close'] * merged['qfq_factor']

    # 写入 daily_adj
    cur = conn.cursor()
    cur.execute(f"DELETE FROM daily_adj WHERE code=?", (code,))
    for _, row in merged.iterrows():
        cur.execute("""
            INSERT INTO daily_adj 
            (date, code, qfq_open, qfq_high, qfq_low, qfq_close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row['date'], code,
            row['qfq_open'], row['qfq_high'], row['qfq_low'], row['qfq_close'],
            int(row['volume'])
        ))
    conn.commit()
    conn.close()


def init_daily_adj_table():
    """创建 daily_adj 表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_adj (
            date TEXT NOT NULL,
            code TEXT NOT NULL,
            qfq_open REAL,
            qfq_high REAL,
            qfq_low REAL,
            qfq_close REAL,
            volume INTEGER,
            PRIMARY KEY (date, code)
        )
    """)
    conn.commit()
    conn.close()


def rebuild_all_adj():
    """重建所有股票的复权数据（每日收盘后运行）"""
    init_daily_adj_table()
    conn = sqlite3.connect(DATABASE_PATH)
    codes = pd.read_sql_query("SELECT DISTINCT code FROM daily_raw", conn)['code'].tolist()
    conn.close()

    for i, code in enumerate(codes):
        generate_daily_adj_for_code(code)
        if i % 100 == 0:
            print(f"复权进度: {i}/{len(codes)}")
    print("✅ 所有复权数据已更新！")