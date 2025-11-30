# StockDBX

个人量化数据平台，专注于A股、ETF等金融数据的高效下载与管理。

## 快速开始

1. 确保安装了所有依赖：`pip install -r requirements.txt`
2. 运行 `python demo_run.py` 启动Demo。


# stockdbx 技术蓝图（v1.0）

> **最后更新**：2025-11-30  
> **目标**：构建安全、稳定、可扩展的本地量化数据基础设施  
> **核心理念**：基础数据只读化 · 派生数据可重建 · 职责严格分离

---

## 一、设计原则

- ✅ **单向数据流**：原始 → 复权 → 指标 → 策略（不可逆）
- ✅ **禁止覆盖写入**：基础库仅允许 `INSERT`
- ✅ **物理分库隔离**：不同类型数据独立存储
- ✅ **人工监督优先**：自动化服务于判断，而非替代
- ✅ **按需下载**：聚焦高价值标的（当前 ~3000 只）

---

## 二、数据库分层架构
E:\quant_data

├── base/                     ← 只读基础库
│   ├── daily.db              # 日线（10–20年）
│   └── dividend.db           # 分红送股记录
│
├── factors/                  ← 复权因子库
│   └── adj_factors.db        # (code, ex_date, forward_factor)
│
├── index/                    ← 指数库
│   └── index_daily.db        # 宽基/行业指数行情
│
├── derived/                  ← 派生指标库
│   └── indicators.db         # MA, MACD, RSI 等
│
└── output/                   ← 合并输出接口
└── merged_{date}.db      # 回测专用快照（不反写）


> **关键决策**：
> - 分红与日线**分离存储**
> - 小时线**暂缓**，仅对高分股按需下载
> - **绝不**在 `daily.db` 中追加指标或信号

---

## 三、核心模块路线图

### 🥇 近期重点（1–2 周）
| 模块 | 功能 |
|------|------|
| `factor_fetcher.py` | Baostock 获取复权因子 → `factors/adj_factors.db` |
| `index_fetcher.py` | 下载主流指数 → `index/index_daily.db` |
| `indicator_engine.py` | 计算前复权价格 + 技术指标 → `derived/indicators.db` |
| `merge_exporter.py` | 按需合并输出 → `output/merged_*.db` |

### 🥈 中期规划（1–2 月）
- 打分系统（流动性、波动率等）
- 虚拟分池（A+/B/C-）
- 异常检测
- 财务数据接入

### 🥉 长期愿景
- Web 可视化面板
- 策略回测框架对接
- 自动化任务调度

---

## 四、数据更新策略

| 数据类型 | 频率 | 时间窗口 | 触发脚本 |
|--------|------|--------|--------|
| 日线（Sina） | 每交易日 | 18:00–23:30 | `run_daily.py` |
| 复权因子（Baostock） | 每周一次 | 周末 20:00 | `run_factors_weekly.py` |
| 指数数据 | 每交易日 | 同日线 | `run_daily.py` |
| 指标计算 | 每交易日 | 23:30 后 | `run_indicators.py` |

> 所有脚本必须：检查交易日、重试机制、日志记录

---

## 五、股票池管理

- **主池文件**：`E:\quant_data\stock_pool\core_3000.csv`
  ```csv
  code,source,added_date
  sh600519,Tonghuashun,2025-11-29
  sz000858,Tonghuashun,2025-11-29
  
所有任务均基于此池，禁止硬编码
六、版本与发布
版本策略：语义化版本（SemVer）MAJOR.MINOR.PATCH
当前版本：v0.1.0（架构奠基版）
里程碑：v1.0.0 = 支持完整回测输入（日线+复权+指标）


---

## 📄 文件 2：`config/settings_template.py`

将以下内容保存为 `E:\MyFile\stockdbx\config\settings_template.py`  
**用户需复制为 `settings.py` 并填写本地路径**

```python
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


💡 使用说明：

复制 settings_template.py → settings.py
修改 DATA_ROOT = r"你的数据目录"（如 r"D:\quant"）
确保该目录存在，程序会自动创建子文件夹

✅ 下一步操作
创建目录：
powershell
编辑
mkdir E:\MyFile\stockdbx\docs
mkdir E:\MyFile\stockdbx\config
保存上述两个文件
初始化 Git（如前所述）
运行：
powershell
编辑
copy config\settings_template.py config\settings.py
# 编辑 settings.py，设置 DATA_ROOT
现在，你的项目已具备：

📘 完整的技术蓝图（团队共识基础）
⚙️ 可配置的模板（支持多环境部署）
🧱 清晰的工程结构
