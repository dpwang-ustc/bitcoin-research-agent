# Bitcoin Research Agent - 开发路线图

## 📋 基于 Linear Issue 的开发计划

本文档将 Linear Issues 与代码实现进行映射，实现任务驱动开发。

---

## 🎯 第一阶段：数据收集与处理 (Foundation)

### ✅ WAL-10: 收集市场行情数据
**状态**: 部分完成  
**优先级**: P0  
**对应代码**: `src/data_loader.py`  
**已实现**:
- ✓ yfinance 集成
- ✓ BTC-USD 历史数据下载
- ✓ 重试机制

**待完善**:
- [ ] 添加多交易所数据源 (Binance, CoinGecko)
- [ ] 添加资金费率数据
- [ ] 实时数据流接入
- [ ] 数据验证与质量检查

**预计工时**: 2-3 天

---

### 🔲 WAL-11: 收集链上数据
**状态**: 未开始  
**优先级**: P0  
**对应代码**: `src/data/onchain_collector.py` (待创建)  
**技术方案**:
- Glassnode API / CryptoQuant API
- 指标：UTXO 分布、活跃地址、大额转账
- 数据存储：`data/raw/onchain/`

**依赖**: WAL-10  
**预计工时**: 3-4 天

---

### 🔲 WAL-12: 收集宏观与新闻数据
**状态**: 未开始  
**优先级**: P1  
**对应代码**: `src/data/macro_collector.py` (待创建)  
**技术方案**:
- 宏观数据：FRED API (DXY, VIX)
- 黄金价格：yfinance
- 新闻抓取：NewsAPI / CryptoPanic

**依赖**: WAL-10  
**预计工时**: 2-3 天

---

### ✅ WAL-13: 数据清洗与特征提取
**状态**: 部分完成  
**优先级**: P0  
**对应代码**: `src/feature_engineering.py`  
**已实现**:
- ✓ 基础技术指标 (MA7, MA30, Volatility, Return)

**待完善**:
- [ ] 时间对齐 (多数据源)
- [ ] 缺失值填补策略
- [ ] 异常值检测
- [ ] 更多技术指标 (RSI, MACD, Bollinger Bands)
- [ ] 资金流动指标

**依赖**: WAL-10, WAL-11, WAL-12  
**预计工时**: 2-3 天

---

## 🧠 第二阶段：模型构建与分析 (Intelligence)

### 🔲 WAL-14: 市场状态识别模型
**状态**: 未开始  
**优先级**: P1  
**对应代码**: `src/model/market_regime.py` (待创建)  
**技术方案**:
- 方法：Hidden Markov Model / K-Means 聚类
- 状态：震荡、趋势、恐慌、狂热
- 输出：Market Regime 指标

**依赖**: WAL-13  
**预计工时**: 4-5 天

---

### 🔲 WAL-15: 波动率与流动性分析
**状态**: 未开始  
**优先级**: P1  
**对应代码**: `src/analysis/volatility_analysis.py` (待创建)  
**技术方案**:
- 隐含波动率 (期权数据)
- 现货期货价差
- 订单簿深度分析
- GARCH 模型

**依赖**: WAL-13  
**预计工时**: 3-4 天

---

### 🔲 WAL-16: 主力资金追踪
**状态**: 未开始  
**优先级**: P2  
**对应代码**: `src/analysis/whale_tracking.py` (待创建)  
**技术方案**:
- 大额地址监控
- 交易所热钱包流动
- 资金流向可视化

**依赖**: WAL-11, WAL-13  
**预计工时**: 4-5 天

---

### 🔲 WAL-17: 情绪与新闻影响建模
**状态**: 未开始  
**优先级**: P1  
**对应代码**: `src/analysis/sentiment_analysis.py` (待创建)  
**技术方案**:
- LLM 情绪分类 (GPT-4 / Llama)
- 新闻源：Twitter, Reddit, News
- 情绪指数构建
- 价格影响滞后分析

**依赖**: WAL-12, WAL-13  
**预计工时**: 5-6 天

---

## 📊 第三阶段：可视化与报告 (Presentation)

### 🔲 WAL-18: 生成可视化面板
**状态**: 未开始  
**优先级**: P1  
**对应代码**: `src/dashboard/app.py` (待创建)  
**技术方案**:
- 框架：Streamlit
- 组件：行情、波动率、情绪、市场状态
- 交互式图表：Plotly

**依赖**: WAL-13, WAL-14, WAL-15, WAL-17  
**预计工时**: 4-5 天

---

### 🔲 WAL-19: 自动生成周报
**状态**: 未开始  
**优先级**: P2  
**对应代码**: `src/reports/weekly_report.py` (待创建)  
**技术方案**:
- 定时任务：每周执行
- LLM 生成报告 (GPT-4)
- 输出：Markdown / PDF

**依赖**: WAL-13, WAL-14, WAL-15  
**预计工时**: 3-4 天

---

### 🔲 WAL-20: 报告摘要智能体
**状态**: 未开始  
**优先级**: P2  
**对应代码**: `src/model/agent_reasoner.py` (已有框架)  
**技术方案**:
- 基础框架已存在
- 增强推理能力
- 集成 LLM (Claude / GPT-4)
- 生成自然语言市场洞察

**依赖**: WAL-14, WAL-15, WAL-17  
**预计工时**: 4-5 天

---

## 🤖 第四阶段：智能体与自动化 (Automation)

### 🔲 WAL-22: 集成 LangChain / Autogen 智能体框架
**状态**: 未开始  
**优先级**: P1  
**对应代码**: `src/agents/` (目录待创建)  
**技术方案**:
- 框架选择：LangChain
- 工具集成：数据查询、分析、报告生成
- 自驱动任务调度

**依赖**: WAL-20  
**预计工时**: 5-7 天

---

### 🔲 WAL-23: 数据定时更新机制
**状态**: 未开始  
**优先级**: P1  
**对应代码**: `scripts/scheduler.py` (待创建)  
**技术方案**:
- 方案：APScheduler / Airflow
- 频率：每日数据更新
- 监控与告警

**依赖**: WAL-10, WAL-11, WAL-12  
**预计工时**: 2-3 天

---

## 🔧 第五阶段：工程化与展示 (Production)

### 🔲 WAL-24: 模型与可视化版本管理
**状态**: 未开始  
**优先级**: P2  
**对应代码**: `.dvc/`, `mlflow/` (配置待创建)  
**技术方案**:
- 数据版本：DVC
- 模型版本：MLflow
- 可重现性保证

**预计工时**: 2-3 天

---

### 🔲 WAL-25: 设计项目网站或看板
**状态**: 未开始  
**优先级**: P2  
**对应代码**: `website/` (待创建)  
**技术方案**:
- 方案 1：Notion 看板
- 方案 2：Next.js 网站
- 展示项目成果

**依赖**: WAL-18  
**预计工时**: 4-5 天

---

### 🔲 WAL-26: 编写论文或白皮书
**状态**: 未开始  
**优先级**: P2  
**对应代码**: `docs/paper/` (待创建)  
**技术方案**:
- LaTeX / Markdown
- 内容：方法论、架构、发现
- 可发表质量

**依赖**: 所有分析任务完成  
**预计工时**: 7-10 天

---

### 🔲 WAL-27: 公开展示 Demo
**状态**: 未开始  
**优先级**: P2  
**对应代码**: `src/dashboard/app.py` (部署版本)  
**技术方案**:
- Streamlit Cloud / Vercel 部署
- 演示视频
- 文档完善

**依赖**: WAL-18, WAL-25  
**预计工时**: 2-3 天

---

## 📈 开发优先级建议

### Sprint 1 (当前 - 2 周后)
1. ✅ **WAL-10**: 完善市场数据收集
2. 🔲 **WAL-11**: 链上数据收集
3. 🔲 **WAL-13**: 完善特征工程

### Sprint 2 (2-4 周)
4. 🔲 **WAL-12**: 宏观与新闻数据
5. 🔲 **WAL-14**: 市场状态识别
6. 🔲 **WAL-15**: 波动率分析

### Sprint 3 (4-6 周)
7. 🔲 **WAL-17**: 情绪分析
8. 🔲 **WAL-18**: 可视化面板
9. 🔲 **WAL-20**: 增强智能体

### Sprint 4 (6-8 周)
10. 🔲 **WAL-22**: LangChain 集成
11. 🔲 **WAL-23**: 自动化调度
12. 🔲 **WAL-19**: 周报生成

### Sprint 5 (8-10 周)
13. 🔲 **WAL-16**: 资金追踪（进阶）
14. 🔲 **WAL-25**: 项目网站
15. 🔲 **WAL-27**: Demo 展示

---

## 🔄 工作流集成

### Git 分支命名规范
- 特性分支：`feature/WAL-{number}-{description}`
- 修复分支：`fix/WAL-{number}-{description}`
- 示例：`feature/WAL-11-onchain-data-collection`

### Commit 消息格式
```
[WAL-{number}] 描述

详细说明
```

### Linear 状态更新触发器
- 创建 PR → Linear 状态: In Progress
- 合并 PR → Linear 状态: Done
- 添加测试 → 添加评论到 Linear

---

## 📝 下一步行动

1. **立即开始**: 完善 WAL-10 (扩展数据源)
2. **准备环境**: 申请 API keys (Glassnode, CryptoQuant, NewsAPI)
3. **设置工具**: 配置 Git hooks 与 Linear 集成
4. **代码审查**: 建立代码质量标准

---

**更新时间**: 2025-10-24  
**维护者**: @dapeng


