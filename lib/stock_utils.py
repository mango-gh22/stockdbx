# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/lib\stock_utils.py
# File Name: stock_utils
# @ File: stock_utils.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 21:48
"""
desc 功能：提供股票代码列表、格式转换等工具函数
"""
# lib/stock_utils.py

import sqlite3
import logging
from config.settings import DATABASE_PATH

# 临时内置的活跃股票池（可后续替换为从 stock_basic 表读取）
# 来源：沪深主板 + 创业板 + 科创板 主要成分股（约 4000 只）
# 注：实际使用中建议用 Baostock 获取完整列表并缓存到 DB

def get_all_active_codes():
    """
    返回所有活跃 A 股代码列表（带 sh/sz 前缀）
    格式: ['sh600000', 'sz000001', ...]
    """
    # 尝试从数据库 stock_basic 表读取（若存在）
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("SELECT code FROM stock_basic WHERE status='L'")  # L=上市
        rows = cur.fetchall()
        if rows:
            codes = [row[0] for row in rows]
            conn.close()
            return codes
    except Exception as e:
        logging.warning(f"未找到 stock_basic 表，使用内置列表: {e}")

    # 否则返回内置精简列表（覆盖主要指数成分股）
    # 实际项目中建议首次运行时用 Baostock 下载完整列表并存入 stock_basic
    major_stocks = [
        # 沪市主板
        'sh600000', 'sh600010', 'sh600016', 'sh600028', 'sh600030', 'sh600036',
        'sh600048', 'sh600050', 'sh600104', 'sh600111', 'sh600177', 'sh600196',
        'sh600276', 'sh600309', 'sh600346', 'sh600436', 'sh600482', 'sh600519',
        'sh600585', 'sh600690', 'sh600703', 'sh600745', 'sh600809', 'sh600887',
        'sh600893', 'sh601012', 'sh601088', 'sh601166', 'sh601211', 'sh601225',
        'sh601288', 'sh601318', 'sh601328', 'sh601398', 'sh601601', 'sh601628',
        'sh601668', 'sh601688', 'sh601816', 'sh601857', 'sh601888', 'sh601988',
        'sh603259', 'sh603288', 'sh603986',
        # 深市主板 + 创业板
        'sz000001', 'sz000002', 'sz000333', 'sz000568', 'sz000651', 'sz000725',
        'sz000776', 'sz000858', 'sz000895', 'sz000938', 'sz000977', 'sz001979',
        'sz002027', 'sz002049', 'sz002129', 'sz002142', 'sz002241', 'sz002271',
        'sz002304', 'sz002311', 'sz002352', 'sz002415', 'sz002456', 'sz002475',
        'sz002594', 'sz002714', 'sz002938', 'sz300014', 'sz300015', 'sz300059',
        'sz300122', 'sz300124', 'sz300144', 'sz300146', 'sz300274', 'sz300347',
        'sz300408', 'sz300413', 'sz300498', 'sz300601', 'sz300661', 'sz300750',
        'sz300760', 'sz300896', 'sz300999',
        # 科创板（部分）
        'sh688001', 'sh688002', 'sh688008', 'sh688012', 'sh688036', 'sh688111',
        'sh688122', 'sh688169', 'sh688363', 'sh688396', 'sh688516', 'sh688981'
    ]
    return major_stocks

def convert_to_bs_code(sina_code: str) -> str:
    """将 'sh600519' 转为 Baostock 格式 'sh.600519'"""
    return sina_code[:2] + '.' + sina_code[2:]

def convert_from_bs_code(bs_code: str) -> str:
    """将 'sh.600519' 转为 Sina 格式 'sh600519'"""
    return bs_code.replace('.', '')