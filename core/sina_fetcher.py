# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/core\sina_fetcher.py
# File Name: sina_fetcher
# @ File: sina_fetcher.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 20:38
"""
desc 5. 负责从新浪获取股票行情数据
"""

# core/sina_fetcher.py

import requests
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)

# 新浪实时行情接口（免费）
SINA_REALTIME_URL = "http://hq.sinajs.cn/list={codes}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "http://finance.sina.com.cn/"
}


def fetch_single_stock_today(code: str):
    """
    获取单只股票今日行情（原始价格，未复权）
    :param code: 如 'sh600519'
    :return: dict or None if failed/stopped
    """
    # sina 接口使用小写
    sina_code = code.lower()
    url = SINA_REALTIME_URL.format(codes=sina_code)

    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        response.encoding = 'gbk'  # sina 返回 gbk 编码

        text = response.text.strip()
        if not text or 'FAILED' in text or len(text) < 50:
            return None

        # 解析格式: var hq_str_sh600519="贵州茅台,1446.50,1455.50,...";
        prefix = f"var hq_str_{sina_code}=\""
        if not text.startswith(prefix):
            return None

        data_str = text[len(prefix):-2]  # 去掉结尾的 ";
        fields = data_str.split(',')

        if len(fields) < 33:
            return None

        # 字段顺序（关键部分）
        name = fields[0]
        open_price = float(fields[1]) if fields[1] else 0.0
        close_yest = float(fields[2]) if fields[2] else 0.0
        price_now = float(fields[3]) if fields[3] else 0.0
        high = float(fields[4]) if fields[4] else 0.0
        low = float(fields[5]) if fields[5] else 0.0
        volume = int(fields[8]) if fields[8] else 0  # 成交量（手）
        amount = float(fields[9]) if fields[9] else 0.0  # 成交额（元）

        # 若开盘价为0，通常表示停牌
        if open_price == 0.0:
            return None

        # 今日收盘价用最新价（盘中）或已收盘价（收盘后）
        close = price_now

        today = datetime.now().strftime("%Y-%m-%d")

        return {
            'date': today,
            'code': code,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'amount': amount
        }

    except Exception as e:
        logging.debug(f"[{code}] 实时行情获取失败: {e}")
        return None


def download_stocks_fast(stock_codes, max_workers=10):
    """
    多线程获取所有股票今日行情
    :param stock_codes: ['sh600519', 'sz000858', ...]
    :return: dict {code: data_dict}
    """
    result = {}
    total = len(stock_codes)
    logging.info(f"开始获取 {total} 只股票的今日行情...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_code = {
            executor.submit(fetch_single_stock_today, code): code
            for code in stock_codes
        }

        completed = 0
        for future in as_completed(future_to_code):
            code = future_to_code[future]
            try:
                data = future.result()
                if data:
                    result[code] = data
                completed += 1
                if completed % 100 == 0:
                    logging.info(f"进度: {completed}/{total}")
            except Exception as e:
                logging.error(f"[{code}] 异常: {e}")

    logging.info(f"✅ 今日行情获取完成！成功 {len(result)} / {total} 只")
    return result