# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/config\settings.py
# File Name: settings
# @ File: settings.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/29 20:19
"""
desc 4. 配置文件 定义数据库路径和其他全局设置
"""

import os

# 数据库路径（核心！）
DATABASE_PATH = r"E:\quant_data\stockdbx.db"

# 日志路径
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "demo.log")

# 是否启用重试
ENABLE_RETRY = True
MAX_RETRIES = 3

# 每批处理多少只股票
BATCH_SIZE = 30

# 新浪行情接口地址模板
SINA_API_TEMPLATE = "http://hq.sinajs.cn/list={codes}"