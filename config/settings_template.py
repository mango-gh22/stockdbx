# _*_ coding: utf-8 _*_
# File Path: E:/MyFile/stockdbx/config\settings_template.py
# File Name: settings_template
# @ File: settings_template.py
# @ Author: m_mango
# @ PyCharm
# @ Date：2025/11/30 1:08
"""
desc 
"""

# ---

## 📄 文件 2：`config/settings_template.py`

# 将以下内容保存为 `E:\MyFile\stockdbx\config\settings_template.py`
# **用户需复制为 `settings.py` 并填写本地路径**

# ```
# python
# config/settings_template.py
# ⚠️ 请复制此文件为 settings.py，并根据你的环境修改路径

import os
from pathlib import Path

# ==============================
# 🔧 项目根目录（自动识别）
# ==============================
PROJECT_ROOT = Path(__file__).parent.parent  # E:\MyFile\stockdbx

# ==============================
# 🗃️ 数据存储根目录（必须修改！）
# ==============================
# 建议使用独立盘符，避免与代码混在一起
DATA_ROOT = r"E:\quant_data"  # ←←←【请修改为你自己的路径】

# 自动构建子目录（无需手动创建）
BASE_DB_DIR     = os.path.join(DATA_ROOT, "base")
FACTORS_DB_DIR  = os.path.join(DATA_ROOT, "factors")
INDEX_DB_DIR    = os.path.join(DATA_ROOT, "index")
DERIVED_DB_DIR  = os.path.join(DATA_ROOT, "derived")
OUTPUT_DB_DIR   = os.path.join(DATA_ROOT, "output")
STOCK_POOL_DIR  = os.path.join(DATA_ROOT, "stock_pool")

# ==============================
# 📁 数据库文件路径
# ==============================
DAILY_DB_PATH      = os.path.join(BASE_DB_DIR, "daily.db")
DIVIDEND_DB_PATH   = os.path.join(BASE_DB_DIR, "dividend.db")

ADJ_FACTORS_DB_PATH = os.path.join(FACTORS_DB_DIR, "adj_factors.db")

INDEX_DAILY_DB_PATH = os.path.join(INDEX_DB_DIR, "index_daily.db")

INDICATORS_DB_PATH = os.path.join(DERIVED_DB_DIR, "indicators.db")

# ==============================
# 📋 股票池文件
# ==============================
STOCK_POOL_CSV = os.path.join(STOCK_POOL_DIR, "core_3000.csv")

# ==============================
# ⏰ 更新时间窗口（24小时制）
# ==============================
UPDATE_WINDOW_START = "18:00"   # 开始尝试下载
UPDATE_WINDOW_END   = "23:30"   # 最晚完成时间
MAX_RETRY           = 3
RETRY_INTERVAL_MIN  = 10        # 重试间隔（分钟）

# ==============================
# 🌐 网络请求配置
# ==============================
REQUEST_TIMEOUT = 15            # 秒
MAX_WORKERS     = 8             # 多线程并发数

# ==============================
# 📝 日志配置
# ==============================
LOG_LEVEL = "INFO"
LOG_FILE  = os.path.join(PROJECT_ROOT, "logs", "stockdbx.log")