# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx\demo_run.py
# File Name: demo_run
# @ File: demo_run.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 20:42
"""
desc 项目的入口文件，用于运行Demo
"""
# demo_run.py

from core.sina_fetcher import download_stocks
from core.data_saver import save_to_db
from schema.init_db import init_db  # 新增：确保表存在
import logging
from config.settings import LOG_PATH

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    # 初始化数据库（安全起见）
    init_db()

    # 测试股票（注意：必须带 sh/sz 前缀！）
    stock_list = [
        'sh600519', 'sh600036', 'sh601318',  # 沪市
        'sz000858', 'sz300750', 'sz002475'   # 深市
    ]

    logging.info("Starting demo run...")
    all_data = {}
    batch_results = download_stocks(stock_list)
    for batch_dict in batch_results:
        all_data.update(batch_dict)  # 合并所有批次

    if all_data:
        save_to_db(all_data)
        logging.info(f"Successfully saved {len(all_data)} stocks.")
    else:
        logging.warning("No data fetched.")