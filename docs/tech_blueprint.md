📜 stockdbx 项目技术纲要（v1.0）
目标：构建一个安全、稳定、可扩展的本地量化数据基础设施

核心理念：基础数据只读化 · 派生数据可重建 · 职责严格分离

一、总体架构原则
原则	说明
✅ 单向数据流	原始数据 → 复权因子 → 指标/信号 → 可视化/策略（不可逆）
✅ 禁止覆盖写入	基础库（日线、分红）仅允许 INSERT，禁止 UPDATE/DELETE
✅ 物理隔离	不同类型数据分库存储，避免耦合
✅ 人工监督优先	自动化服务于人工判断，而非替代
✅ 按需下载	非全市场覆盖，聚焦高价值标的（当前 ~3000 只）
二、数据库分层设计（物理分库）
text
编辑
E:\quant_data\
├── base/                     ←【只读基础库】
│   ├── daily.db              # 日线（10–20年），仅 sh/sz 主力股
│   └── dividend.db           # 分红送股 + 配股记录（Baostock）
│
├── factors/                  ←【复权因子库】
│   └── adj_factors.db        # 存储 (code, ex_date, ratio) 复权因子
│
├── index/                    ←【指数库】（近期新增）
│   └── index_daily.db        # 宽基/行业指数行情（000300.SH, 399975.SZ...）
│
├── derived/                  ←【派生指标库】（近期重点）
│   └── indicators.db         # 技术指标（MA, MACD, RSI...），按需计算
│
└── output/                   ←【合并输出接口】
    └── merged_{date}.db      # 按需生成：日线+复权+指标 合并视图（供回测/策略使用）
🔸 关键决策：

分红与日线分离 → ✅ 同意！dividend.db 独立，更新频率低（周/月）
小时线暂缓 → ✅ 仅对高分值股票按需下载（后期再议）
不搞“大合并库” → ✅ 坚决避免 daily_raw 被污染
三、核心模块规划（按优先级）
🥇 近期重点（1–2 周内完成）
模块	功能	输出
1. 复权因子下载器
core/factor_fetcher.py	调用 Baostock 获取 adjust_factor
→ 去重 + 增量写入 factors/adj_factors.db	(code, ex_date, forward_factor)
2. 指数数据下载器
core/index_fetcher.py	下载主流指数日线（沪深300、中证500、创业板指等）	index_daily.db
3. 指标计算引擎
core/indicator_engine.py	读 base/daily.db + factors/adj_factors.db
→ 计算前复权价格 → 生成 MA/MACD → 写入 derived/indicators.db	技术指标表
4. 数据合并输出器
core/merge_exporter.py	按策略需求，JOIN 基础+复权+指标
→ 生成 output/merged_20251129.db（或 CSV）	干净、完整的回测输入
💡 合并输出特点：

按日期/股票池生成快照
仅供外部使用（策略/回测），不反写回任何源库
文件名含时间戳，支持版本追溯
🥈 中期规划（1–2 个月）
模块	说明
打分系统	基于流动性、波动率、停牌频率等生成 score（0–100）
虚拟分池	根据分数划分 A+/A/B/C-，存入 pools.db
异常检测	识别跳空缺口、量价背离、数据缺失等
财务数据接入	通过 Baostock/Tushare 获取季报/年报（ROE、营收增速等）
🥉 长期愿景
Web 可视化面板（Streamlit/Dash）
策略与回测框架对接（如 Backtrader）
自动化任务调度（Windows Task / Airflow）
四、数据更新策略
数据类型	更新频率	时间窗口	触发方式
日线（Sina）	每交易日	18:00–23:30	run_daily.py
分红/复权因子（Baostock）	每周一次（或每月）	周末 20:00	run_factors_weekly.py
指数数据	每交易日	同日线	与日线同步
指标计算	每交易日（晚于日线）	23:30 后	run_indicators.py
⚠️ 重要：所有更新脚本必须：

检查是否为交易日
重试机制（网络不稳定）
日志记录（成功/失败/跳过）
五、股票池管理（核心输入）
主池文件：E:\quant_data\stock_pool\core_3000.csv
csv
编辑
code,source,added_date
sh600519,Tonghuashun,2025-11-29
sz000858,Tonghuashun,2025-11-29
...
所有下载/计算任务均基于此池
禁止硬编码股票列表
六、项目结构（最终确认）
text
编辑
E:\MyFile\stockdbx\
├── core/
│   ├── sina_fetcher.py       # 今日快照
│   ├── history_fetcher.py    # 历史日线（初始化用）
│   ├── factor_fetcher.py     # ← 新增：复权因子
│   ├── index_fetcher.py      # ← 新增：指数
│   ├── indicator_engine.py   # ← 新增：指标计算
│   └── merge_exporter.py     # ← 新增：合并输出
│
├── lib/
│   ├── stock_utils.py        # get_selected_codes()
│   └── db_router.py          # 连接不同 DB 的路由
│
├── config/
│   └── settings.py           # 所有路径、时间、参数
│
├── schema/                   # 各 DB 的建表语句
│
├── run_daily.py              # 主更新入口
├── run_factors_weekly.py     # ← 新增
└── view_data.py              # 查看工具（按库分类）
七、下一步行动建议
✅ 立即创建 factors/adj_factors.db 表结构
✅ 编写 factor_fetcher.py（调用 Baostock 获取复权因子）
✅ 定义 merge_exporter.py 的输出格式（建议 Parquet 或 SQLite 快照）
📝 整理 core_3000.csv 股票池（从同花顺导出并标准化）
结语
你已建立起一套逻辑严密、边界清晰、演进有序的技术路线。

这份纲要将成为 stockdbx 项目的“宪法”——后续所有代码、讨论、扩展，都应以此为准绳。

🔄 后续对话建议：

请以 “基于技术纲要 v1.0，请提供 XXX 模块的完整代码” 开头，

我将确保输出与整体架构完全一致。