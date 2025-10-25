# Linear Issue 驱动开发工作流

本文档介绍如何使用 Linear Issues 驱动 Bitcoin Research Agent 的开发流程。

---

## 🎯 工作流概览

```
Linear Issue → 查看路线图 → 启动任务 → 编写代码 → 提交代码 → 更新进度 → 关闭 Issue
```

---

## 📚 核心工具

### 1. **进度同步工具** (`tools/linear_sync.py`)

**功能**：
- 生成项目整体进度报告
- 检查代码文件完成情况
- 推荐下一步任务
- 输出 Markdown 格式报告

**使用方法**：
```bash
python tools/linear_sync.py
```

**输出**：
- `PROGRESS_REPORT.md` - 详细进度报告
- 控制台显示推荐任务列表

**运行频率**：建议每天运行一次，或完成重要里程碑后运行

---

### 2. **任务启动工具** (`tools/start_task.py`)

**功能**：
- 显示任务开发指南
- 自动创建 Git 分支
- 生成文件框架代码
- 提供 Checklist

**使用方法**：
```bash
python tools/start_task.py WAL-11
```

**交互流程**：
1. 显示任务详细指南
2. 询问是否创建 Git 分支
3. 询问是否创建文件框架
4. 输出下一步行动建议

**支持的任务**：
- WAL-10: 市场行情数据收集
- WAL-11: 链上数据收集
- WAL-12: 宏观与新闻数据
- WAL-13: 数据清洗与特征提取
- 更多任务持续添加中...

---

### 3. **开发路线图** (`DEVELOPMENT_ROADMAP.md`)

**功能**：
- 所有任务的详细技术方案
- 任务依赖关系
- 预估工时
- Sprint 规划建议

**使用场景**：
- 开始新任务前查阅技术方案
- 了解任务依赖关系
- 规划开发周期

---

## 🔄 完整工作流示例

### 场景：开始 WAL-11（链上数据收集）

#### 第 1 步：查看当前进度

```bash
python tools/linear_sync.py
```

输出：
```
>> 当前推荐任务:
  [高] WAL-10: 收集市场行情数据 (60%)
  [高] WAL-13: 数据清洗与特征提取 (40%)
  [中] WAL-11: 收集链上数据 (0%)
```

#### 第 2 步：查看路线图

打开 `DEVELOPMENT_ROADMAP.md`，找到 WAL-11 部分：

```markdown
### 🔲 WAL-11: 收集链上数据
**状态**: 未开始
**优先级**: P0
**技术方案**:
- Glassnode API / CryptoQuant API
- 指标：UTXO 分布、活跃地址、大额转账
...
```

#### 第 3 步：启动任务

```bash
python tools/start_task.py WAL-11
```

交互：
```
🚀 开始任务: WAL-11

📖 WAL-11 开发指南：收集链上数据
...

是否创建 Git 分支? (y/n): y
✓ 已创建并切换到分支: feature/wal-11-onchain-data

是否创建文件框架? (y/n): y
✓ 已创建文件: src/data/onchain_collector.py
✓ 已创建文件: configs/api_keys.example.yaml
```

#### 第 4 步：准备 API Keys

1. 注册 Glassnode: https://studio.glassnode.com/settings/api
2. 注册 CryptoQuant: https://cryptoquant.com/settings/api
3. 复制配置文件：
```bash
cp configs/api_keys.example.yaml configs/api_keys.yaml
```
4. 填入你的 API Keys

#### 第 5 步：编写代码

打开生成的文件框架：
- `src/data/onchain_collector.py`

根据开发指南实现功能：
```python
# 实现 get_active_addresses()
# 实现 get_utxo_age_distribution()
# 实现 get_whale_transactions()
# ...
```

#### 第 6 步：测试代码

```bash
python src/data/onchain_collector.py
```

#### 第 7 步：提交代码

```bash
git add .
git commit -m "[WAL-11] 实现链上数据收集器基础功能

- 集成 Glassnode API
- 实现活跃地址数据获取
- 实现 UTXO 分布分析
- 添加 API Keys 配置文件
"
```

#### 第 8 步：更新 Linear（手动）

打开 Linear Issue WAL-11：
- 更新状态为 "In Progress"
- 添加评论：已完成基础框架，待完善...
- 更新完成度百分比

#### 第 9 步：更新本地进度

编辑 `tools/linear_sync.py`，更新 WAL-11 的完成度：
```python
"WAL-11": {
    "status": "partial",  # 从 not_started 改为 partial
    "completion": 0.4,    # 从 0.0 改为 0.4
    ...
}
```

重新生成进度报告：
```bash
python tools/linear_sync.py
```

#### 第 10 步：继续迭代

根据 `next_steps` 继续完善功能，直到任务完成。

---

## 🎨 Git 工作流规范

### 分支命名

```
feature/WAL-{number}-{description}
fix/WAL-{number}-{description}
docs/WAL-{number}-{description}
```

示例：
- `feature/wal-11-onchain-data`
- `fix/wal-10-api-retry`
- `docs/wal-21-readme-update`

### Commit 消息格式

```
[WAL-{number}] 简短描述

详细说明（可选）
- 具体改动 1
- 具体改动 2
```

示例：
```
[WAL-11] 实现 Glassnode API 集成

- 添加活跃地址数据获取
- 添加 UTXO 分布分析
- 配置 API Keys 管理
```

### 代码审查

提交 Pull Request 时：
1. 标题包含 Issue 编号：`[WAL-11] 链上数据收集器`
2. 描述中关联 Linear Issue
3. 添加测试结果截图
4. 更新 CHANGELOG（如适用）

---

## 📊 进度追踪

### 每日检查

```bash
# 查看今日推荐任务
python tools/linear_sync.py

# 查看 Git 状态
git status
```

### 每周回顾

1. 检查 `PROGRESS_REPORT.md`
2. 更新 Linear 看板
3. 调整下周计划
4. 团队同步进度

---

## 💡 最佳实践

### 1. **任务拆分**

将大任务拆分为小步骤：
- WAL-11 链上数据 → 活跃地址 → UTXO 分布 → 大额转账
- 每个小步骤独立提交

### 2. **增量开发**

不要等到完美才提交：
- 先实现基础框架（20%）
- 再实现核心功能（60%）
- 最后完善细节（100%）

### 3. **文档先行**

开始编码前：
1. 阅读 `DEVELOPMENT_ROADMAP.md` 的技术方案
2. 使用 `start_task.py` 查看开发指南
3. 准备好所需的 API Keys 和依赖

### 4. **测试驱动**

每个模块都应该：
- 有 `if __name__ == "__main__"` 测试代码
- 能独立运行和验证
- 输出清晰的日志

### 5. **持续同步**

定期运行：
```bash
# 本地进度更新
python tools/linear_sync.py

# Linear 手动更新（通过 MCP）
# 或使用 Cursor 的 Linear 集成
```

---

## 🔧 配置文件管理

### API Keys

**不要提交到 Git：**
- `configs/api_keys.yaml`
- `.env`

**应该提交：**
- `configs/api_keys.example.yaml`

**设置 `.gitignore`：**
```
configs/api_keys.yaml
.env
*.key
```

### 环境变量

推荐使用环境变量：
```bash
# Linux / Mac
export GLASSNODE_API_KEY="your_key"

# Windows
set GLASSNODE_API_KEY=your_key
```

或使用 `.env` 文件（配合 python-dotenv）

---

## 📖 参考资源

### Linear 相关
- [Linear Issue 列表](https://linear.app/walk-and-book/team/WAL/bitcoin-research-agent)
- [项目看板](https://linear.app/walk-and-book/project/bitcoin-research-agent)

### 技术文档
- `DEVELOPMENT_ROADMAP.md` - 完整开发路线图
- `PROGRESS_REPORT.md` - 最新进度报告
- `README.md` - 项目介绍

### API 文档
- [Glassnode API](https://docs.glassnode.com/)
- [CryptoQuant API](https://docs.cryptoquant.com/)
- [Binance API](https://binance-docs.github.io/apidocs/)
- [CoinGecko API](https://www.coingecko.com/en/api/documentation)

---

## ❓ 常见问题

### Q: 如何选择下一个任务？

A: 运行 `python tools/linear_sync.py`，查看推荐任务列表。优先完成：
1. 进行中的任务（partial）
2. 优先级高的未开始任务（P0）
3. 无依赖的基础任务

### Q: 如何更新任务完成度？

A: 编辑 `tools/linear_sync.py` 中的 `TASK_CODE_MAPPING`：
```python
"WAL-11": {
    "status": "partial",  # not_started / partial / completed
    "completion": 0.5,    # 0.0 ~ 1.0
    ...
}
```

### Q: 如何与 Linear 同步？

A: 目前采用手动同步方式：
1. 本地工具生成进度报告
2. 手动更新 Linear Issue 状态
3. （未来）可以通过 Linear API 自动同步

### Q: 任务之间有依赖怎么办？

A: 查看 `DEVELOPMENT_ROADMAP.md` 中的 "依赖" 字段：
- 先完成依赖任务
- 或调整优先级
- 或并行开发（如果可能）

---

## 🚀 快速命令参考

```bash
# 查看进度
python tools/linear_sync.py

# 启动任务
python tools/start_task.py WAL-XX

# 创建分支
git checkout -b feature/wal-xx-description

# 提交代码
git add .
git commit -m "[WAL-XX] description"

# 运行测试
python src/path/to/module.py

# 查看 Git 状态
git status
git log --oneline -10
```

---

**祝开发顺利！** 🎉

如有问题，请查看：
- `DEVELOPMENT_ROADMAP.md` - 技术方案
- `PROGRESS_REPORT.md` - 当前进度
- Linear Issue 评论区 - 团队讨论


