# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx\run_daily.py
# File Name: run_daily
# @ File: run_daily.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 21:45
"""
desc 每日更新：
"""

# run_daily.py

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.stock_utils import get_all_active_codes
from core.sina_fetcher import download_stocks_fast
from lib.database import save_daily_raw
from datetime import datetime

def main():
    print("🌅 开始更新今日行情...")
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"日期: {today}")

    codes = get_all_active_codes()
    print(f"共 {len(codes)} 只股票")

    # 获取今日数据
    data_dict = download_stocks_fast(codes, max_workers=8)

    # 转为列表并保存
    data_list = []
    for code, d in data_dict.items():
        data_list.append((
            d['date'], code,
            d['open'], d['high'], d['low'], d['close'],
            d['volume'], d['amount'], 'sina'
        ))

    if data_list:
        save_daily_raw(data_list)
        print(f"✅ 已保存 {len(data_list)} 条记录到 daily_raw")
    else:
        print("⚠️ 未获取到任何有效数据")

if __name__ == "__main__":
    main()