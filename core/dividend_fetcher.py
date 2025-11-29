# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/core\dividend_fetcher.py
# File Name: dividend_fetcher
# @ File: dividend_fetcher.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 21:29
"""
desc 功能：用 Baostock 仅下载分红送股记录（全市场只需几分钟）
"""

# core/dividend_fetcher.py

import baostock as bs
import sqlite3
import logging
from config.settings import DATABASE_PATH
from lib.stock_utils import get_all_active_codes  # 假设你有此函数返回 ['sh.600519', 'sz.000858']

logging.basicConfig(level=logging.INFO)


def init_dividend_table():
    """创建 dividend 表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dividend (
            code TEXT NOT NULL,
            ex_date TEXT NOT NULL,      -- 除权除息日
            div_cash REAL DEFAULT 0.0,  -- 每股派现（元）
            bonus_share REAL DEFAULT 0.0, -- 送股比例（10送3 → 0.3）
            trans_share REAL DEFAULT 0.0, -- 转增比例
            PRIMARY KEY (code, ex_date)
        )
    """)
    conn.commit()
    conn.close()


def fetch_and_save_dividend_for_code(bs_code: str):
    """
    下载单只股票的分红记录（从2005至今）
    :param bs_code: 格式如 'sh.600519'
    """
    try:
        # 查询2005-2025所有分红（Baostock 支持跨年）
        rs = bs.query_dividend_data(code=bs_code, year="2005", yearType="report")
        data_list = []
        while (rs.error_code == '0') and rs.next():
            row = rs.get_row_data()
            # Baostock 字段: [code, dividOperateDate, perCashDiv, perBonusShare, perTransShare]
            ex_date = row[1]  # 除权日
            if not ex_date or ex_date == '':
                continue
            data_list.append((
                bs_code.replace('.', ''),  # 转为 'sh600519'
                ex_date,
                float(row[2]) if row[2] else 0.0,
                float(row[3]) if row[3] else 0.0,
                float(row[4]) if row[4] else 0.0
            ))

        if data_list:
            conn = sqlite3.connect(DATABASE_PATH)
            cur = conn.cursor()
            cur.executemany("""
                INSERT OR REPLACE INTO dividend 
                (code, ex_date, div_cash, bonus_share, trans_share)
                VALUES (?, ?, ?, ?, ?)
            """, data_list)
            conn.commit()
            conn.close()
            return len(data_list)
    except Exception as e:
        logging.error(f"[{bs_code}] 分红下载失败: {e}")
        return 0
    return 0


def download_all_dividends():
    """下载全市场分红记录（高效，因数据量极小）"""
    init_dividend_table()

    # 登录 Baostock
    bs.login()
    logging.info("已登录 Baostock")

    # 获取股票列表（需转换为 Baostock 格式）
    sina_codes = get_all_active_codes()  # 返回 ['sh600519', 'sz000858']
    bs_codes = [code[:2] + '.' + code[2:] for code in sina_codes]  # → ['sh.600519', 'sz.000858']

    total = len(bs_codes)
    success_count = 0
    for i, code in enumerate(bs_codes):
        n = fetch_and_save_dividend_for_code(code)
        success_count += n
        if i % 100 == 0:
            logging.info(f"分红进度: {i}/{total}, 已获取 {success_count} 条记录")

    bs.logout()
    logging.info(f"✅ 全市场分红数据下载完成！共 {success_count} 条记录。")