# AI Agent 使用指南

## 📋 概述

Bitcoin Research Agent 现在集成了AI智能体（WAL-20），能够使用大语言模型（LLM）生成高质量的市场洞察和分析报告。

## 🤖 支持的 LLM 提供商

### 1. OpenAI（推荐）⭐⭐⭐⭐⭐

**支持模型**:
- `gpt-4o` - 最强大，最昂贵
- `gpt-4o-mini` - **推荐**，性价比最高
- `gpt-4-turbo` - 平衡性能和成本
- `gpt-3.5-turbo` - 最便宜

**配置方法**:
```bash
# 设置环境变量
export OPENAI_API_KEY="your-api-key-here"

# 或在代码中传入
agent = MarketInsightAgent(
    provider="openai",
    model="gpt-4o-mini",
    api_key="your-api-key-here"
)
```

**获取 API Key**:
1. 访问 https://platform.openai.com/api-keys
2. 注册/登录账号
3. 创建新的 API Key
4. 充值（建议 $5-10 即可）

**成本估算**:
- GPT-4o-mini: ~$0.01 / 周报（约 ¥0.07）
- GPT-4o: ~$0.05 / 周报（约 ¥0.35）

---

### 2. Anthropic Claude ⭐⭐⭐⭐⭐

**支持模型**:
- `claude-3-5-sonnet-20241022` - **推荐**，最新最强
- `claude-3-opus-20240229` - 最强大
- `claude-3-sonnet-20240229` - 平衡
- `claude-3-haiku-20240307` - 最快最便宜

**配置方法**:
```bash
# 设置环境变量
export ANTHROPIC_API_KEY="your-api-key-here"

# 或在代码中传入
agent = MarketInsightAgent(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    api_key="your-api-key-here"
)
```

**获取 API Key**:
1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 创建新的 API Key
4. 充值（建议 $5-10 即可）

**成本估算**:
- Claude 3.5 Sonnet: ~$0.02 / 周报（约 ¥0.14）
- Claude 3 Haiku: ~$0.005 / 周报（约 ¥0.035）

---

### 3. Ollama（本地部署）⭐⭐⭐⭐

**支持模型**:
- `llama3.1:8b` - **推荐**，8B 参数
- `llama3.1:70b` - 70B 参数，需要强大显卡
- `qwen2.5:7b` - 中文优化
- `deepseek-r1:7b` - 推理优化

**配置方法**:
```bash
# 1. 安装 Ollama
# MacOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
# Windows: 下载安装包 https://ollama.com/download

# 2. 启动 Ollama 服务
ollama serve

# 3. 下载模型
ollama pull llama3.1:8b

# 4. 使用
agent = MarketInsightAgent(
    provider="ollama",
    model="llama3.1:8b"
)
```

**优势**:
- ✅ 完全免费
- ✅ 数据隐私（本地运行）
- ✅ 无需网络（离线可用）
- ✅ 无调用限制

**劣势**:
- ❌ 需要较好的硬件（推荐 16GB+ RAM）
- ❌ 质量略低于 GPT-4/Claude
- ❌ 速度较慢（取决于硬件）

---

## 📦 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或单独安装 AI 相关依赖
pip install openai anthropic
```

---

## 🚀 快速开始

### 1. 使用 AI 生成周报

```python
from src.reports.weekly_report_generator import WeeklyReportGenerator

# 创建生成器（使用 OpenAI）
generator = WeeklyReportGenerator(
    use_ai=True,
    ai_provider="openai",
    ai_model="gpt-4o-mini",
    api_key="your-key",  # 或设置环境变量
    verbose=True
)

# 生成周报
report = generator.generate_report()
print(report)
```

### 2. 直接使用 AI Agent

```python
from src.model.agent_reasoner import MarketInsightAgent

# 创建 Agent
agent = MarketInsightAgent(
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.7
)

# 分析市场数据
stats = {
    'price': {'current': 67500, 'week_return': 3.5},
    'regime': {'current_regime': '趋势'},
    'sentiment': {'current': 68, 'current_category': '贪婪'},
    # ... 更多数据
}

# 生成洞察
analysis = agent.analyze_market_data(stats)
summary = agent.generate_executive_summary(stats)
outlook = agent.generate_outlook(stats)

print(analysis)
```

### 3. 在 Dashboard 中启用 AI

修改 `src/dashboard/app.py`:

```python
# 在周报生成部分
generator = WeeklyReportGenerator(
    use_ai=True,  # 启用 AI
    ai_provider="openai",
    verbose=False
)
```

---

## 🔧 高级配置

### 1. 调整生成温度

```python
agent = MarketInsightAgent(
    provider="openai",
    temperature=0.7,  # 0.0 = 确定性，1.0 = 创造性
    max_tokens=2000   # 最大生成长度
)
```

- **低温度 (0.0-0.3)**: 更保守、更一致的输出
- **中温度 (0.5-0.7)**: 平衡创造性和准确性（推荐）
- **高温度 (0.8-1.0)**: 更有创造性，但可能不太准确

### 2. 回退到规则生成

如果 API 调用失败，系统会自动回退到规则生成：

```python
generator = WeeklyReportGenerator(
    use_ai=True,  # 尝试使用 AI
    verbose=True  # 打印回退信息
)

# 如果 AI 失败，自动使用规则生成
report = generator.generate_report()
```

### 3. 完全禁用 AI

```python
generator = WeeklyReportGenerator(
    use_ai=False  # 只使用规则生成
)
```

---

## 💰 成本优化建议

### 1. 选择合适的模型

| 使用场景 | 推荐模型 | 月成本估算 |
|---------|---------|-----------|
| 个人学习 | Ollama (本地) | ¥0 |
| 小规模使用 | GPT-4o-mini | ¥2-5/月 |
| 专业分析 | Claude 3.5 Sonnet | ¥5-10/月 |
| 商业应用 | GPT-4o | ¥10-20/月 |

### 2. 减少调用次数

```python
# 只在需要时生成 AI 洞察
generator = WeeklyReportGenerator(
    use_ai=True,
    verbose=True
)

# 一周生成一次即可
report = generator.generate_report()
```

### 3. 使用缓存

```python
# 缓存生成的报告，避免重复调用
import os
from datetime import datetime

report_file = f"reports/weekly_{datetime.now().strftime('%Y%m%d')}.md"

if os.path.exists(report_file):
    with open(report_file, 'r', encoding='utf-8') as f:
        report = f.read()
else:
    report = generator.generate_report(output_path=report_file)
```

---

## 🐛 故障排除

### 问题 1: API Key 错误

```
ValueError: OpenAI API key not found
```

**解决方法**:
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 设置环境变量
export OPENAI_API_KEY="sk-..."

# 或在代码中传入
agent = MarketInsightAgent(api_key="sk-...")
```

### 问题 2: 连接超时

```
TimeoutError: API request timed out
```

**解决方法**:
1. 检查网络连接
2. 使用代理（如果在国内）
3. 切换到 Ollama 本地模型

### 问题 3: 余额不足

```
Error: Insufficient quota
```

**解决方法**:
1. 访问 https://platform.openai.com/account/billing
2. 充值账户（建议 $5-10）
3. 或切换到免费的 Ollama

### 问题 4: 导入错误

```
ImportError: No module named 'openai'
```

**解决方法**:
```bash
pip install openai anthropic
```

---

## 📊 效果对比

### 规则生成 vs AI 生成

**规则生成**（原有方式）:
```
本周市场上涨3.85%，处于趋势状态，市场情绪为贪婪。
```

**AI 生成**（GPT-4o-mini）:
```
本周比特币市场表现强劲，价格上涨3.85%至67,500美元，突破关键阻力位。
市场从震荡转为趋势状态，表明多头力量占据主导。情绪指标显示市场进入
贪婪区域，配合主力吸筹行为，短期看涨趋势明显。然而，需要警惕情绪过
热带来的回调风险。建议在65,000-66,000区间寻找回调买入机会。
```

**对比**:
- ✅ AI 生成更自然、更详细
- ✅ AI 能识别更复杂的模式
- ✅ AI 给出更具体的操作建议
- ❌ AI 需要 API 成本
- ❌ AI 响应速度较慢（2-5秒）

---

## 🎯 最佳实践

1. **开发阶段**: 使用 Ollama 本地模型（免费）
2. **测试阶段**: 使用 GPT-4o-mini（便宜）
3. **生产阶段**: 使用 Claude 3.5 Sonnet（质量最好）
4. **商业应用**: 考虑 GPT-4o（最强大）

---

## 📚 相关资源

- OpenAI API 文档: https://platform.openai.com/docs
- Anthropic API 文档: https://docs.anthropic.com/
- Ollama 文档: https://ollama.com/
- 项目代码: `src/model/agent_reasoner.py`

---

## ❓ 常见问题

### Q: 必须使用 API 吗？
A: 不必须。可以使用 Ollama 本地运行，完全免费。

### Q: 哪个模型最好？
A: 对于成本效益，推荐 GPT-4o-mini。对于质量，推荐 Claude 3.5 Sonnet。

### Q: 数据会泄露吗？
A: OpenAI 和 Anthropic 不会使用 API 数据训练模型。或使用 Ollama 本地运行，完全隐私。

### Q: 一周报告要花多少钱？
A: GPT-4o-mini 约 ¥0.07，Claude 3.5 Sonnet 约 ¥0.14，一月不到 ¥1。

---

**更新日期**: 2025-10-26  
**版本**: WAL-20  
**作者**: Bitcoin Research Agent Team

