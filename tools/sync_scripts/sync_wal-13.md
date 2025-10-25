# WAL-13 Linear 同步脚本

## 使用方法
在 Cursor 中，请求 AI 助手执行以下操作：

### 1. 添加进度评论

请使用 Linear MCP 工具为 Issue WAL-13 添加以下评论：

```markdown
## 📊 开发进度更新

**更新时间**: 2025-10-24 15:05
**完成度**: 40%
**状态**: 🔄 partial

### 相关代码文件
- ✓ `src/feature_engineering.py`

### 下一步行动
1. 实现多数据源时间对齐
2. 添加缺失值填补策略
3. 添加异常值检测
4. 添加更多技术指标 (RSI, MACD, Bollinger)
5. 实现资金流动指标

---
*此评论由自动化工具生成 (tools/sync_to_linear.py)*
```

### 2. 更新 Issue 状态

根据完成度更新状态：
- 0%: Todo
- 1-99%: In Progress  
- 100%: Done

当前建议状态：**In Progress**

### 3. Cursor AI 命令示例

你可以直接对 Cursor AI 说：

> "请使用 Linear MCP 工具为 Issue WAL-13 添加进度评论，内容在 tools\sync_scripts\sync_wal-13.md 文件中"

---

**生成时间**: 2025-10-24 15:05:18
