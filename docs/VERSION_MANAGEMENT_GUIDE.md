# Bitcoin Research Agent - 版本管理指南

**版本**: v1.0.0  
**日期**: 2025-10-26  
**适用于**: WAL-24 模型与可视化版本管理

---

## 📋 概述

本指南介绍如何使用 Bitcoin Research Agent 的版本管理系统，确保所有输出、配置和结果的可追溯性和可重现性。

### 核心功能

1. **版本控制** - 自动追踪所有输出版本
2. **配置管理** - 记录每次运行的参数
3. **运行历史** - 完整的执行历史记录
4. **可重现性** - 确保结果可重现
5. **版本比较** - 对比不同版本的差异
6. **版本恢复** - 回滚到任意历史版本

---

## 🚀 快速开始

### 1. 基本用法

```python
from src.versioning import VersionManager

# 创建版本管理器
vm = VersionManager()

# 创建新版本
version_id = vm.create_version(
    task_name='daily_analysis',
    config={
        'llm_model': 'gpt-4o-mini',
        'temperature': 0.7
    },
    outputs={
        'report': 'reports/daily_report_20251026.md',
        'chart': 'data/processed/plots/price_chart.png'
    },
    metadata={
        'description': '每日市场分析',
        'author': 'auto'
    }
)

print(f"版本已创建: {version_id}")
```

### 2. 命令行使用

```bash
# 列出所有版本
python src/versioning/cli.py list

# 查看版本详情
python src/versioning/cli.py show daily_analysis_20251026_090000

# 比较两个版本
python src/versioning/cli.py compare v1 v2

# 恢复版本
python src/versioning/cli.py restore daily_analysis_20251026_090000

# 查看统计信息
python src/versioning/cli.py stats

# 查看运行历史
python src/versioning/cli.py history
```

---

## 📚 详细功能

### 1. 版本创建

#### 1.1 完整示例

```python
from src.versioning import VersionManager

vm = VersionManager(
    version_dir='versions',  # 版本存储目录
    verbose=True            # 显示详细信息
)

# 创建版本
version_id = vm.create_version(
    task_name='weekly_report',  # 任务名称
    config={                     # 配置参数
        'llm_provider': 'openai',
        'llm_model': 'gpt-4o-mini',
        'temperature': 0.7,
        'max_tokens': 1024,
        'data_range': '2025-10-20 to 2025-10-26'
    },
    outputs={                    # 输出文件
        'report': 'reports/weekly_report_20251026.md',
        'sentiment_chart': 'data/processed/plots/sentiment.png',
        'volatility_chart': 'data/processed/plots/volatility.png',
        'data': 'data/processed/integrated_features.csv'
    },
    metadata={                   # 元数据
        'description': '2025年第43周市场报告',
        'author': 'scheduler',
        'tags': ['weekly', 'automated']
    }
)
```

#### 1.2 自动记录的信息

版本创建时，系统会自动记录：
- ✅ 版本ID（时间戳）
- ✅ 配置参数
- ✅ 输出文件哈希
- ✅ 文件大小
- ✅ Git commit ID
- ✅ Python 版本
- ✅ 创建时间

### 2. 版本查询

#### 2.1 列出版本

```python
# 列出所有版本（最新10个）
versions = vm.list_versions(limit=10)

# 筛选特定任务
daily_versions = vm.list_versions(task_name='daily_analysis', limit=20)

# 遍历版本
for v in versions:
    print(f"{v['version_id']} - {v['created_at']}")
```

#### 2.2 获取版本详情

```python
# 获取特定版本
version = vm.get_version('daily_analysis_20251026_090000')

# 访问配置
config = version['config']
print(f"LLM: {config['llm_model']}")

# 访问输出文件
for key, artifact in version['artifacts'].items():
    print(f"{key}: {artifact['versioned_path']}")

# 获取最新版本
latest = vm.get_latest_version('daily_analysis')
```

### 3. 版本比较

#### 3.1 比较两个版本

```python
comparison = vm.compare_versions(
    'daily_analysis_20251026_090000',
    'daily_analysis_20251025_090000'
)

# 配置差异
config_diff = comparison['config_diff']
print(f"新增配置: {config_diff['added']}")
print(f"删除配置: {config_diff['removed']}")
print(f"修改配置: {config_diff['changed']}")

# 文件差异
artifacts_diff = comparison['artifacts_diff']
print(f"新增文件: {artifacts_diff['added']}")
print(f"修改文件: {artifacts_diff['changed']}")

# 时间差
time_diff_hours = comparison['time_diff'] / 3600
print(f"时间差: {time_diff_hours:.2f} 小时")
```

### 4. 可重现性检查

#### 4.1 检查版本

```python
# 检查版本是否可重现
result = vm.check_reproducibility('daily_analysis_20251026_090000')

if result['reproducible']:
    print("✅ 该版本可重现")
else:
    print("❌ 该版本不可重现")
    print(f"原因: {result.get('integrity_error', 'Unknown')}")

# 检查项
print(f"配置可用: {result['config_available']}")
print(f"文件可用: {result['artifacts_available']}")
print(f"Git记录: {result['git_commit_recorded']}")
print(f"Python版本: {result['python_version']}")
```

### 5. 版本恢复

#### 5.1 恢复到指定版本

```python
# 恢复版本到 restored/ 目录
success = vm.restore_version(
    'daily_analysis_20251026_090000',
    output_dir='restored/v1'
)

if success:
    print("✅ 版本已恢复")
    # 使用恢复的配置
    with open('restored/v1/config.json', 'r') as f:
        config = json.load(f)
        # 使用 config 重新运行
```

### 6. 运行历史

#### 6.1 查看历史

```python
# 获取所有运行历史
history = vm.get_run_history(limit=50)

# 筛选特定任务
daily_history = vm.get_run_history(task_name='daily_analysis', limit=30)

# 分析历史
for record in history:
    print(f"{record['created_at']}: {record['task_name']}")
    print(f"  版本: {record['version_id']}")
    print(f"  输出: {len(record['artifacts'])} 个文件")
```

### 7. 统计信息

#### 7.1 获取统计

```python
stats = vm.get_statistics()

print(f"总版本数: {stats['total_versions']}")
print(f"总大小: {stats['total_size_mb']} MB")
print(f"存储位置: {stats['version_dir']}")

# 任务统计
for task, count in stats['task_counts'].items():
    print(f"  {task}: {count} 个版本")
```

---

## 🔧 集成到现有系统

### 1. 集成到 Agent

```python
from src.agent import BitcoinResearchAgent
from src.versioning import VersionManager

# 创建 Agent 和版本管理器
agent = BitcoinResearchAgent()
vm = VersionManager()

# 运行分析
result = agent.run("生成本周市场分析报告")

# 创建版本
if result.get('report'):
    version_id = vm.create_version(
        task_name='agent_analysis',
        config={
            'task': result.get('task_type'),
            'llm_model': 'gpt-4o-mini'
        },
        outputs={
            'report': 'reports/weekly_report.md'
        },
        metadata={
            'agent_version': '1.0.0',
            'task_steps': len(result.get('messages', []))
        }
    )
```

### 2. 集成到 Scheduler

```python
from src.scheduler import ScheduledTaskManager
from src.versioning import VersionManager

class VersionedScheduler(ScheduledTaskManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vm = VersionManager()
    
    def task_daily_analysis(self):
        # 运行任务
        result = super().task_daily_analysis()
        
        # 创建版本
        version_id = self.vm.create_version(
            task_name='scheduled_daily_analysis',
            config=self.config.get('agent', {}),
            outputs={
                'report': 'reports/daily_report_latest.md'
            },
            metadata={
                'scheduled': True,
                'scheduler_version': '1.0.0'
            }
        )
```

### 3. 集成到 Dashboard

```python
import streamlit as st
from src.versioning import VersionManager

# 在 Dashboard 中显示版本历史
st.title("📦 版本管理")

vm = VersionManager()

# 显示最近版本
versions = vm.list_versions(limit=10)

for v in versions:
    st.subheader(v['version_id'])
    st.write(f"任务: {v['task_name']}")
    st.write(f"时间: {v['created_at']}")
    
    # 可重现性状态
    reproducible = vm.check_reproducibility(v['version_id'])
    if reproducible['reproducible']:
        st.success("✅ 可重现")
    else:
        st.error("❌ 不可重现")
    
    # 恢复按钮
    if st.button(f"恢复 {v['version_id']}"):
        vm.restore_version(v['version_id'])
        st.success("版本已恢复")
```

---

## 📊 版本目录结构

```
versions/
├── runs/                        # 运行版本
│   ├── daily_analysis_20251026_090000/
│   │   ├── config.json         # 配置参数
│   │   ├── metadata.json       # 版本元数据
│   │   ├── daily_report_20251026.md  # 输出文件
│   │   └── sentiment_chart.png
│   │
│   └── weekly_report_20251027_080000/
│       ├── config.json
│       ├── metadata.json
│       └── weekly_report_20251027.md
│
├── artifacts/                   # 共享文件（未来扩展）
├── configs/                     # 配置快照（未来扩展）
└── run_history.jsonl           # 运行历史日志
```

---

## 🎯 最佳实践

### 1. 命名约定

```python
# 任务命名
task_names = {
    'daily_analysis': '每日分析',
    'weekly_report': '每周报告',
    'market_regime': '市场状态分析',
    'volatility_study': '波动率研究',
    'sentiment_tracking': '情绪追踪'
}

# 版本ID自动生成
# 格式: {task_name}_{YYYYMMDD}_{HHMMSS}
# 例如: daily_analysis_20251026_090000
```

### 2. 配置记录

```python
# 记录所有关键参数
config = {
    # LLM 配置
    'llm_provider': 'openai',
    'llm_model': 'gpt-4o-mini',
    'temperature': 0.7,
    'max_tokens': 1024,
    
    # 数据配置
    'data_start': '2025-10-20',
    'data_end': '2025-10-26',
    'data_source': 'yfinance',
    
    # 分析配置
    'indicators': ['RSI', 'MACD', 'BB'],
    'window_sizes': [7, 14, 30],
    
    # 其他配置
    'version': '1.0.0',
    'environment': 'production'
}
```

### 3. 元数据添加

```python
# 添加有用的元数据
metadata = {
    'description': '详细的任务描述',
    'author': 'auto|manual|username',
    'tags': ['daily', 'automated', 'production'],
    'status': 'success|failed|partial',
    'execution_time': 180.5,  # 秒
    'data_points': 2854,
    'analysis_type': 'comprehensive'
}
```

### 4. 定期清理

```python
# 定期清理旧版本
def cleanup_old_versions(vm: VersionManager, keep_days: int = 30):
    """清理超过30天的版本"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    versions = vm.list_versions(limit=1000)
    
    for v in versions:
        created = datetime.fromisoformat(v['created_at'])
        if created < cutoff_date:
            # 可以选择删除或归档
            print(f"旧版本: {v['version_id']}")
```

---

## 🐛 故障排除

### 问题 1: 文件哈希不匹配

```python
# 检查文件完整性
result = vm.check_reproducibility('version_id')

if not result['reproducible']:
    print(f"错误: {result.get('integrity_error')}")
    
    # 解决方案：重新创建版本
    vm.create_version(...)
```

### 问题 2: 版本目录占用空间过大

```bash
# 查看统计信息
python src/versioning/cli.py stats

# 清理策略：
# 1. 删除重复文件（使用哈希去重）
# 2. 压缩旧版本
# 3. 移动到归档存储
```

### 问题 3: Git commit未记录

```bash
# 确保在Git仓库中运行
git status

# 确保Git配置正确
git config --list
```

---

## 📚 API 参考

### VersionManager

```python
class VersionManager:
    def __init__(self, version_dir='versions', verbose=True)
    
    def create_version(
        task_name: str,
        config: Dict,
        outputs: Dict[str, str],
        metadata: Optional[Dict] = None
    ) -> str
    
    def list_versions(
        task_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]
    
    def get_version(version_id: str) -> Optional[Dict]
    
    def get_latest_version(task_name: str) -> Optional[Dict]
    
    def compare_versions(version_id1: str, version_id2: str) -> Dict
    
    def check_reproducibility(version_id: str) -> Dict
    
    def restore_version(version_id: str, output_dir: str = 'restored') -> bool
    
    def get_run_history(
        task_name: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]
    
    def get_statistics() -> Dict
```

---

## ✅ 检查清单

部署版本管理系统前确认：

- [ ] 已创建 versions/ 目录
- [ ] 已配置 .gitignore（忽略 versions/）
- [ ] 已配置 .dvcignore（如果使用DVC）
- [ ] 已测试版本创建功能
- [ ] 已测试版本查询功能
- [ ] 已测试可重现性检查
- [ ] 已集成到现有模块
- [ ] 已设置定期清理策略
- [ ] 已培训团队成员使用

---

**更新日期**: 2025-10-26  
**版本**: v1.0.0  
**维护**: Bitcoin Research Agent Team

