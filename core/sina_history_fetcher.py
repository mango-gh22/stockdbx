# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/core\sina_history_fetcher.py
# File Name: sina_history_fetcher
# @ File: sina_history_fetcher.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 21:42
"""
desc 功能：多线程下载单只股票 近 N 年原始日线（未复权）
"""

# core/sina_history_fetcher.py

import requests
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.settings import DATABASE_PATH

# 配置日志
logging.basicConfig(level=logging.INFO)

# 新浪历史K线接口（免费、无token）
SINA_KLINE_URL = (
    "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
    "CN_MarketData.getKLineData?symbol={code}&scale=240&ma=no&datalen={days}"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://finance.sina.com.cn/"
}


def fetch_single_stock_history(code: str, days: int = 1000):
    """
    下载单只股票的历史日线（原始价格，未复权）
    :param code: 如 'sh600519'
    :param days: 最大天数（新浪最多支持 ~1000 天 ≈ 4年）
    :return: list of dict, 每个元素为 {'date': '2025-01-01', 'open': ..., 'close': ...}
    """
    market_code = code  # sina 接口直接用 sh/sz 前缀
    url = SINA_KLINE_URL.format(code=market_code, days=days)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logging.warning(f"[{code}] HTTP {response.status_code}")
            return []

        data = response.json()
        if not isinstance(data, list):
            logging.warning(f"[{code}] 返回非列表: {str(data)[:100]}")
            return []

        result = []
        for item in data:
            try:
                result.append({
                    'date': item['day'],
                    'open': float(item['open']),
                    'high': float(item['high']),
                    'low': float(item['low']),
                    'close': float(item['close']),
                    'volume': int(float(item['volume']) / 100),  # sina 返回的是“股”，转为“手”
                    'amount': float(item['amount'])
                })
            except (ValueError, KeyError) as e:
                continue  # 跳过异常行
        return result
    except Exception as e:
        logging.error(f"[{code}] 下载失败: {e}")
        return []


def save_raw_data_to_db(code: str, data_list: list):
    """将原始行情写入 daily_raw 表"""
    import sqlite3
    if not data_list:
        return
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    for row in data_list:
        cur.execute("""
            INSERT OR IGNORE INTO daily_raw 
            (date, code, open, high, low, close, volume, amount, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['date'], code,
            row['open'], row['high'], row['low'], row['close'],
            row['volume'], row['amount'], 'sina'
        ))
    conn.commit()
    conn.close()


def download_all_history(stock_codes, days=1000, max_workers=8):
    """
    多线程下载所有股票历史日线
    :param stock_codes: ['sh600519', 'sz000858', ...]
    :param days: 请求天数
    :param max_workers: 线程数（建议 4~8）
    """
    total = len(stock_codes)
    logging.info(f"开始下载 {total} 只股票的历史日线（最多 {days} 天）...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_single_stock_history, code, days): code
            for code in stock_codes
        }

        completed = 0
        for future in as_completed(futures):
            code = futures[future]
            try:
                data = future.result()
                save_raw_data_to_db(code, data)
                completed += 1
                if completed % 50 == 0:
                    logging.info(f"进度: {completed}/{total}")
            except Exception as e:
                logging.error(f"[{code}] 异常: {e}")

    logging.info("✅ 历史日线下载完成！")