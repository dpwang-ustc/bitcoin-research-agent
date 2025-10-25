# Bitcoin Research Agent - 特征工程指南

## 📋 概述

本文档介绍 Bitcoin Research Agent 项目的特征工程流程，包括数据收集、清洗、特征提取和多数据源整合。

**生成日期**: 2025-10-25  
**版本**: 1.0  
**对应任务**: WAL-13 数据清洗与特征提取

---

## 🎯 特征工程目标

1. ✅ **数据清洗**: 处理缺失值、异常值、重复数据
2. ✅ **技术指标**: 生成 40+ 个技术分析指标
3. ✅ **多源整合**: 合并市场、链上、宏观、新闻数据
4. ✅ **时间对齐**: 统一不同数据源的时间索引
5. ✅ **特征标准化**: 为机器学习模型准备数据

---

## 📊 数据源

### 1. 市场数据 (Market Data)
- **来源**: yfinance (BTC-USD)
- **时间范围**: 2018-01-01 至今
- **原始特征**: Open, High, Low, Close, Volume
- **更新频率**: 每日

### 2. 链上数据 (Onchain Data)
- **来源**: Glassnode / CryptoQuant (待集成)
- **指标**: UTXO分布、活跃地址、大额转账
- **状态**: 🔲 未实现

### 3. 宏观数据 (Macro Data)
- **来源**: FRED API, yfinance
- **指标**: DXY (美元指数), VIX (恐慌指数), 黄金价格
- **状态**: ✅ 部分集成

### 4. 新闻情感 (News Sentiment)
- **来源**: NewsAPI / CryptoPanic (待集成)
- **指标**: 情感得分、新闻数量、关键词
- **状态**: 🔲 未实现

---

## 🔧 技术指标列表

### 价格指标 (14个)
1. `Return` - 日收益率
2. `Return_1d` - 1天收益率
3. `Return_7d` - 7天收益率
4. `Return_30d` - 30天收益率
5. `Log_Return` - 对数收益率
6. `Volatility_7d` - 7天波动率
7. `Volatility_30d` - 30天波动率
8. `Price_Range` - 价格范围 (High - Low)
9. `Price_Range_Pct` - 价格范围百分比
10. `Close_Position` - 收盘价相对位置
11-14. `MA7/MA30/MA50/MA200` - 简单移动平均

### 移动平均线 (10个)
- **SMA**: MA7, MA14, MA30, MA50, MA200
- **EMA**: EMA7, EMA14, EMA30, EMA50, EMA200

### 技术指标 (9个)
1. `RSI14` - 相对强弱指标
2. `MACD` - MACD线
3. `MACD_Signal` - MACD信号线
4. `MACD_Hist` - MACD柱状图
5. `BB_Middle` - 布林带中轨
6. `BB_Upper` - 布林带上轨
7. `BB_Lower` - 布林带下轨
8. `BB_Width` - 布林带宽度
9. `BB_PercentB` - 布林带位置

### 成交量指标 (6个)
1. `Volume_MA7` - 成交量7天均值
2. `Volume_MA30` - 成交量30天均值
3. `Volume_Change` - 成交量变化率
4. `PVT` - 价量趋势
5. `OBV` - 能量潮
6. `ATR14` - 平均真实波幅

### 异常值标记 (2个)
1. `Close_outlier` - 价格异常值标记
2. `Volume_outlier` - 成交量异常值标记

**总计**: 42个市场特征

---

## 🚀 使用方法

### 方法1: 使用 FeatureEngineer 类

```python
import pandas as pd
from src.feature_engineering import FeatureEngineer

# 加载数据
df = pd.read_csv('data/raw/bitcoin_price.csv', index_col=0, parse_dates=True)

# 创建特征工程器
engineer = FeatureEngineer(verbose=True)

# 完整流程
df_processed = engineer.process_pipeline(
    df,
    clean=True,               # 数据清洗
    add_features=True,        # 添加技术指标
    detect_outliers=True,     # 异常值检测
    handle_missing=True,      # 处理缺失值
    output_path='data/processed/bitcoin_features.csv'
)
```

### 方法2: 使用便捷函数

```python
from src.feature_engineering import add_features

df = pd.read_csv('data/raw/bitcoin_price.csv', index_col=0, parse_dates=True)
df_processed = add_features(df)
```

### 方法3: 数据整合（多数据源）

```python
from src.data.data_integrator import DataIntegrator

# 创建数据整合器
integrator = DataIntegrator(data_dir='data', verbose=True)

# 整合所有数据源
df_integrated = integrator.integrate_all_data(
    add_market_features=True,  # 添加市场技术指标
    align_method='outer',      # 时间对齐方式
    fill_method='ffill'        # 缺失值填补
)

# 保存到 data/processed/integrated_features.csv
```

---

## 📁 项目结构

```
bitcoin-research-agent/
├── data/
│   ├── raw/                          # 原始数据
│   │   ├── bitcoin_price.csv         # 市场数据
│   │   ├── macro_gold_test.csv       # 黄金价格
│   │   ├── macro_vix_test.csv        # VIX指数
│   │   └── onchain_data.csv          # 链上数据 (待添加)
│   └── processed/                    # 处理后数据
│       ├── bitcoin_features.csv      # 市场特征
│       └── integrated_features.csv   # 整合特征
├── src/
│   ├── feature_engineering.py        # 特征工程核心模块
│   ├── data/
│   │   └── data_integrator.py        # 数据整合模块
│   └── data_loader.py                # 数据下载
└── tests/
    └── test_feature_engineering.py   # 测试脚本
```

---

## 🔍 数据清洗策略

### 1. 缺失值处理
- **前向填充** (ffill): 用前一个有效值填充
- **后向填充** (bfill): 用后一个有效值填充
- **插值法** (interpolate): 线性插值
- **均值填充** (mean/median): 用列均值/中位数填充
- **删除** (drop): 删除缺失值

```python
# 示例
df = engineer.handle_missing_values(df, strategy='ffill', limit=3)
```

### 2. 异常值检测
- **IQR方法**: 四分位距离 (Q3 - Q1)
- **Z-score方法**: 标准差倍数

```python
# IQR方法 (推荐)
df = engineer.detect_outliers(
    df, 
    columns=['Close', 'Volume'],
    method='iqr',
    threshold=3.0
)

# Z-score方法
df = engineer.detect_outliers(
    df,
    columns=['Close', 'Volume'],
    method='zscore',
    threshold=3.0
)
```

### 3. 数据清洗
- 确保数值列类型正确
- 转换索引为 DatetimeIndex
- 按时间排序
- 删除重复行

---

## 📈 特征工程流程

```mermaid
graph LR
    A[原始数据] --> B[数据清洗]
    B --> C[技术指标计算]
    C --> D[异常值检测]
    D --> E[缺失值填补]
    E --> F[特征输出]
```

### 完整流程示例

```bash
# 1. 下载市场数据
python src/data_loader.py

# 2. 单独运行特征工程
python src/feature_engineering.py

# 3. 整合多数据源
python src/data/data_integrator.py

# 4. 运行测试
python tests/test_feature_engineering.py
```

---

## 📊 输出数据格式

### bitcoin_features.csv
- **行数**: ~2655 (取决于数据范围)
- **列数**: 42
- **索引**: Date (datetime)
- **内容**: 市场数据 + 技术指标

### integrated_features.csv
- **行数**: ~2655
- **列数**: 52+ (取决于可用数据源)
- **索引**: Date (datetime)
- **内容**: 市场 + 链上 + 宏观 + 新闻

---

## 🔄 数据更新

### 手动更新
```bash
python src/data_loader.py
python src/data/data_integrator.py
```

### 自动更新 (待实现 - WAL-23)
将通过定时任务（Airflow / APScheduler）实现每日自动更新。

---

## 🎯 下一步计划

### 已完成 ✅
- [x] 基础市场数据收集
- [x] 技术指标计算 (42个)
- [x] 数据清洗与缺失值处理
- [x] 异常值检测
- [x] 多数据源时间对齐
- [x] 数据整合脚本

### 待完成 🔲
- [ ] 链上数据收集 (WAL-11)
- [ ] 完整宏观数据接入 (WAL-12)
- [ ] 新闻情感分析 (WAL-17)
- [ ] 特征选择与降维
- [ ] 数据版本管理 (DVC)
- [ ] 自动更新机制 (WAL-23)

---

## 📚 参考资料

### 技术指标
- [TA-Lib Documentation](https://ta-lib.org/)
- [Investopedia - Technical Indicators](https://www.investopedia.com/terms/t/technicalindicator.asp)

### Python库
- **pandas**: 数据处理
- **numpy**: 数值计算
- **yfinance**: 金融数据下载

---

## 🐛 常见问题

### Q1: 数据下载失败？
**A**: 检查网络连接，yfinance 会重试3次。如果仍失败，可能是 Yahoo Finance API 限流。

### Q2: 特征计算后数据量减少？
**A**: 正常现象。技术指标需要历史数据窗口，前面的数据会被删除。例如 MA200 需要200天历史。

### Q3: 缺失值过多？
**A**: 检查数据源的时间范围是否一致。使用 `align_method='inner'` 只保留所有源都有的时间点。

### Q4: 如何添加自定义指标？
**A**: 在 `FeatureEngineer` 类中添加新方法，然后在 `add_all_features()` 中调用。

---

## 📞 联系方式

- **项目**: Bitcoin Research Agent
- **维护者**: @dapeng
- **更新日期**: 2025-10-25

---

**WAL-13 完成度: 90%** 🎉

