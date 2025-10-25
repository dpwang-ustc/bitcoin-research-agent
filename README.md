# Bitcoin Research Agent

An AI-powered research agent for analyzing and reasoning about Bitcoin market dynamics.

## 🎯 项目概述

Bitcoin Research Agent 是一个基于 AI 的比特币市场研究工具，集成了多维度数据收集、智能分析和自动化报告功能。

### 核心功能

- 📊 **多源数据收集**: 市场行情、链上数据、宏观经济、新闻情绪
- 🧠 **智能分析**: 市场状态识别、波动率分析、资金追踪、情绪建模
- 📈 **可视化面板**: 交互式图表展示关键指标
- 🤖 **AI 智能体**: 自动生成研究报告和市场洞察
- 🔄 **自动化**: 定时数据更新和周报生成

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行基础数据收集

```bash
python src/data_loader.py
```

### 3. 特征工程

```bash
python src/feature_engineering.py
```

### 4. 查看项目进度

```bash
python tools/linear_sync.py
```

---

## 📂 项目结构

```
bitcoin-research-agent/
├── data/                      # 数据目录
│   ├── raw/                   # 原始数据
│   │   ├── bitcoin_price.csv
│   │   ├── onchain/          # 链上数据（待实现）
│   │   ├── news/             # 新闻数据（待实现）
│   │   └── macro/            # 宏观数据（待实现）
│   ├── processed/            # 处理后的数据
│   │   └── bitcoin_features.csv
│   └── external/             # 外部数据
│
├── src/                      # 源代码
│   ├── data/                 # 数据收集模块（待完善）
│   │   ├── binance_collector.py
│   │   ├── onchain_collector.py
│   │   ├── macro_collector.py
│   │   └── news_collector.py
│   ├── model/                # 模型模块
│   │   ├── agent_reasoner.py
│   │   ├── baseline_regression.py
│   │   └── market_regime.py  # 待实现
│   ├── analysis/             # 分析模块（待实现）
│   ├── dashboard/            # 可视化面板（待实现）
│   ├── reports/              # 报告生成（待实现）
│   ├── agents/               # 智能体框架（待实现）
│   ├── data_loader.py        # ✓ 数据加载
│   └── feature_engineering.py # ✓ 特征工程
│
├── configs/                  # 配置文件
│   └── api_keys.example.yaml # API 配置示例
│
├── tools/                    # 开发工具
│   ├── linear_sync.py        # 进度同步工具
│   └── start_task.py         # 任务启动工具
│
├── docs/                     # 文档
│   └── LINEAR_WORKFLOW.md    # 开发工作流
│
├── notebooks/                # Jupyter notebooks
├── tests/                    # 测试
├── scripts/                  # 脚本
│
├── DEVELOPMENT_ROADMAP.md    # 开发路线图
├── PROGRESS_REPORT.md        # 进度报告
└── README.md                 # 本文件
```

---

## 📋 开发路线图

本项目基于 **Linear Issues 驱动开发**。查看完整路线图：[DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)

### 当前进度：10.6%

- ✅ **WAL-10**: 收集市场行情数据（60% 完成）
- ✅ **WAL-13**: 数据清洗与特征提取（40% 完成）
- ✅ **WAL-20**: 报告摘要智能体（20% 完成）
- ✅ **WAL-21**: 项目仓库构建（70% 完成）
- 🔲 14 个任务待开始

查看最新进度：`python tools/linear_sync.py`

---

## 🛠️ 开发工作流

### 1. 查看项目进度

```bash
python tools/linear_sync.py
```

### 2. 启动新任务

```bash
python tools/start_task.py WAL-11
```

### 3. 开发与提交

```bash
# 编写代码
# ...

# 提交
git add .
git commit -m "[WAL-11] 实现链上数据收集"
```

详细工作流：[docs/LINEAR_WORKFLOW.md](docs/LINEAR_WORKFLOW.md)

---

## 🔧 配置

### API Keys 配置

1. 复制配置模板：
```bash
cp configs/api_keys.example.yaml configs/api_keys.yaml
```

2. 填入你的 API Keys：
- [Glassnode](https://studio.glassnode.com/settings/api)
- [CryptoQuant](https://cryptoquant.com/settings/api)
- [NewsAPI](https://newsapi.org/account)
- [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)

⚠️ **注意**：不要将 `api_keys.yaml` 提交到 Git！

---

## 📊 使用示例

### 下载比特币价格数据

```python
from src.data_loader import load_bitcoin_data

df = load_bitcoin_data(start='2020-01-01')
print(df.tail())
```

### 特征工程

```python
from src.feature_engineering import add_features
import pandas as pd

df = pd.read_csv('data/raw/bitcoin_price.csv', index_col=0, parse_dates=True)
df = add_features(df)
print(df[['Close', 'MA7', 'MA30', 'Volatility']].tail())
```

### 基础回归模型

```python
from src.model.baseline_regression import train_regression_model

model = train_regression_model()
```

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定模块测试
python src/data_loader.py
python src/feature_engineering.py
```

---

## 📚 文档

- [开发路线图](DEVELOPMENT_ROADMAP.md) - 完整技术方案和任务规划
- [开发工作流](docs/LINEAR_WORKFLOW.md) - Linear Issue 驱动开发指南
- [进度报告](PROGRESS_REPORT.md) - 实时项目进度（自动生成）

---

## 🤝 贡献

本项目采用 **Linear Issue 驱动开发** 模式：

1. 查看 [Linear 看板](https://linear.app/walk-and-book/team/WAL/bitcoin-research-agent)
2. 选择一个 Issue 开始
3. 使用 `python tools/start_task.py WAL-XX` 启动
4. 提交代码并更新 Linear

详见：[docs/LINEAR_WORKFLOW.md](docs/LINEAR_WORKFLOW.md)

---

## 📄 License

MIT License

---

## 👥 团队

- **Walk and Book Team**
- Linear 项目管理
- Cursor AI 辅助开发

---

## 🔗 相关链接

- [Linear 项目](https://linear.app/walk-and-book/team/WAL/bitcoin-research-agent)
- [Glassnode](https://glassnode.com/)
- [CryptoQuant](https://cryptoquant.com/)
- [Binance API](https://binance-docs.github.io/apidocs/)
- [CoinGecko API](https://www.coingecko.com/en/api)