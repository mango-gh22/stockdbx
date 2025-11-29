# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx\run_init.py
# File Name: run_init
# @ File: run_init.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 21:31
"""
desc 首次初始化 功能：一键初始化全市场历史数据（行情 + 分红）
"""

# run_init.py

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到路径（确保能导入 core / lib）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.stock_utils import get_all_active_codes
from core.sina_history_fetcher import download_all_history
from core.dividend_fetcher import download_all_dividends
from schema.init_db import init_db  # 确保表存在

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    print("🚀 开始初始化量化数据库...")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 初始化数据库表结构
    init_db()
    print("✅ 数据库表已创建")

    # 2. 获取股票列表
    stock_list = get_all_active_codes()
    print(f"📊 共获取 {len(stock_list)} 只活跃股票")

    # 3. 下载历史日线（原始价格）
    print("\n📥 正在下载历史日线（新浪多线程）...")
    download_all_history(stock_list, days=1000, max_workers=6)  # 约 20~40 分钟

    # 4. 下载分红送股记录
    print("\n💰 正在下载分红送股记录（Baostock）...")
    download_all_dividends()  # 约 1~3 分钟

    print("\n🎉 初始化完成！")
    print("下一步建议：")
    print("  - 运行 `python view_data.py` 查看数据")
    print("  - 每日收盘后运行 `run_daily.py` 更新最新行情")


if __name__ == "__main__":
    main()