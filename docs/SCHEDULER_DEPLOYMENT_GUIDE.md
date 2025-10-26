# Bitcoin Research Agent - 定时任务部署指南

**版本**: v1.0.0  
**日期**: 2025-10-26  
**适用于**: WAL-23 定时任务调度

---

## 📋 概述

本指南提供了多种方式部署 Bitcoin Research Agent 的定时任务调度器，实现自动化的数据更新和报告生成。

### 支持的部署方式

1. **Python Schedule** - 推荐用于开发和测试
2. **Linux Cron** - 推荐用于生产环境（Linux/Mac）
3. **Windows Task Scheduler** - 推荐用于生产环境（Windows）
4. **Docker + Cron** - 推荐用于容器化部署
5. **Systemd Service** - 推荐用于 Linux 服务器

---

## 🚀 方式 1: Python Schedule（最简单）

### 优点
- ✅ 跨平台（Windows/Linux/Mac）
- ✅ 配置简单
- ✅ 易于调试
- ✅ 支持动态配置

### 缺点
- ⚠️ 需要持续运行
- ⚠️ 不够可靠（进程可能被杀）

### 快速开始

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置

编辑 `configs/schedule_config.yaml`:

```yaml
agent:
  enabled: true
  llm_provider: "openai"
  llm_model: "gpt-4o-mini"

tasks:
  daily_analysis:
    enabled: true
    time: "09:00"
  
  weekly_report:
    enabled: true
    day: "monday"
    time: "08:00"
```

#### 3. 设置 API Key

```bash
# Windows
set OPENAI_API_KEY=sk-...

# Linux/Mac
export OPENAI_API_KEY=sk-...
```

#### 4. 启动调度器

**Windows:**
```bash
start_scheduler.bat
```

**Linux/Mac:**
```bash
chmod +x start_scheduler.sh
./start_scheduler.sh
```

**或直接运行:**
```bash
python src/scheduler/task_scheduler.py
```

#### 5. 测试

```bash
# 列出所有任务
python src/scheduler/task_scheduler.py --list

# 立即运行一次
python src/scheduler/task_scheduler.py --run-once daily_analysis
```

---

## 🐧 方式 2: Linux Cron（生产推荐）

### 优点
- ✅ 系统级调度，可靠
- ✅ 资源占用少
- ✅ 广泛支持

### 缺点
- ⚠️ 仅限 Linux/Mac
- ⚠️ 配置相对复杂

### 部署步骤

#### 1. 创建执行脚本

创建 `/usr/local/bin/btc-daily-analysis.sh`:

```bash
#!/bin/bash
# Bitcoin Research Agent - 每日分析

# 设置环境
export OPENAI_API_KEY="sk-..."
export PATH="/usr/local/bin:/usr/bin:/bin"

# 切换到项目目录
cd /path/to/bitcoin-research-agent

# 激活虚拟环境（如果有）
source venv/bin/activate

# 运行任务
python3 src/scheduler/task_scheduler.py --run-once daily_analysis

# 记录日志
echo "[$(date)] Daily analysis completed" >> logs/cron.log
```

#### 2. 设置权限

```bash
chmod +x /usr/local/bin/btc-daily-analysis.sh
```

#### 3. 配置 Cron

```bash
# 编辑 crontab
crontab -e

# 添加以下内容：

# 每天 9:00 运行每日分析
0 9 * * * /usr/local/bin/btc-daily-analysis.sh

# 每周一 8:00 运行周报
0 8 * * 1 /usr/local/bin/btc-weekly-report.sh

# 查看日志: tail -f logs/cron.log
```

#### 4. Cron 表达式说明

```
* * * * *
│ │ │ │ │
│ │ │ │ └── 星期 (0-7, 0和7都表示周日)
│ │ │ └──── 月份 (1-12)
│ │ └────── 日期 (1-31)
│ └──────── 小时 (0-23)
└────────── 分钟 (0-59)
```

**常用示例**:
```bash
0 9 * * *       # 每天 9:00
0 */6 * * *     # 每 6 小时
30 8 * * 1      # 每周一 8:30
0 0 1 * *       # 每月 1 号午夜
0 9 * * 1-5     # 周一到周五 9:00
```

#### 5. 验证

```bash
# 查看 cron 日志
tail -f /var/log/cron  # CentOS/RHEL
tail -f /var/log/syslog | grep CRON  # Ubuntu/Debian

# 手动测试
/usr/local/bin/btc-daily-analysis.sh
```

---

## 🪟 方式 3: Windows Task Scheduler（生产推荐）

### 优点
- ✅ Windows 原生，可靠
- ✅ 图形界面，易于管理
- ✅ 支持条件触发

### 缺点
- ⚠️ 仅限 Windows

### 部署步骤

#### 1. 创建执行脚本

创建 `C:\BTC-Agent\run_daily_analysis.bat`:

```batch
@echo off
REM Bitcoin Research Agent - 每日分析

REM 设置环境变量
set OPENAI_API_KEY=sk-...

REM 切换到项目目录
cd /d D:\Projects\bitcoin-research-agent

REM 运行任务
python src\scheduler\task_scheduler.py --run-once daily_analysis

REM 记录日志
echo [%date% %time%] Daily analysis completed >> logs\taskscheduler.log
```

#### 2. 打开任务计划程序

```
开始菜单 → 搜索 "任务计划程序" → 打开
```

#### 3. 创建基本任务

1. **右键** "任务计划程序库" → "创建基本任务"
2. **名称**: `BTC Agent - Daily Analysis`
3. **描述**: `Bitcoin Research Agent 每日市场分析`

#### 4. 配置触发器

1. **触发器**: 每天
2. **开始时间**: 09:00:00
3. **重复**: 每天
4. **启用**: ☑️

#### 5. 配置操作

1. **操作**: 启动程序
2. **程序/脚本**: `C:\BTC-Agent\run_daily_analysis.bat`
3. **起始于（可选）**: `D:\Projects\bitcoin-research-agent`

#### 6. 高级设置

1. **条件**:
   - ☑️ 仅当计算机使用交流电源时
   - ☑️ 如果计算机进入空闲状态，则停止

2. **设置**:
   - ☑️ 如果任务失败，每隔多久重试一次: 10 分钟
   - ☑️ 最多重试次数: 3
   - ☑️ 允许按需运行任务

#### 7. 验证

右键任务 → "运行"，检查日志：

```
logs\taskscheduler.log
```

#### 8. 使用命令行创建（高级）

```powershell
# 创建每日分析任务
schtasks /create /tn "BTC Agent - Daily Analysis" /tr "C:\BTC-Agent\run_daily_analysis.bat" /sc daily /st 09:00

# 创建每周报告任务
schtasks /create /tn "BTC Agent - Weekly Report" /tr "C:\BTC-Agent\run_weekly_report.bat" /sc weekly /d MON /st 08:00

# 查看任务
schtasks /query /tn "BTC Agent - Daily Analysis"

# 立即运行
schtasks /run /tn "BTC Agent - Daily Analysis"

# 删除任务
schtasks /delete /tn "BTC Agent - Daily Analysis" /f
```

---

## 🐳 方式 4: Docker + Cron

### 优点
- ✅ 容器化，隔离环境
- ✅ 易于部署和迁移
- ✅ 资源可控

### 部署步骤

#### 1. 创建 Dockerfile

`Dockerfile.scheduler`:

```dockerfile
FROM python:3.10-slim

# 安装依赖
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 安装 cron
RUN apt-get update && apt-get install -y cron

# 创建 crontab
RUN echo "0 9 * * * cd /app && python3 src/scheduler/task_scheduler.py --run-once daily_analysis >> /var/log/cron.log 2>&1" > /etc/cron.d/btc-agent
RUN chmod 0644 /etc/cron.d/btc-agent
RUN crontab /etc/cron.d/btc-agent

# 创建日志
RUN touch /var/log/cron.log

# 启动 cron
CMD cron && tail -f /var/log/cron.log
```

#### 2. 构建镜像

```bash
docker build -f Dockerfile.scheduler -t btc-agent-scheduler .
```

#### 3. 运行容器

```bash
docker run -d \
  --name btc-scheduler \
  -e OPENAI_API_KEY=sk-... \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/logs:/app/logs \
  btc-agent-scheduler
```

#### 4. 查看日志

```bash
docker logs -f btc-scheduler
```

---

## ⚙️ 方式 5: Systemd Service（Linux 服务器）

### 优点
- ✅ 开机自启动
- ✅ 自动重启
- ✅ 日志集成

### 部署步骤

#### 1. 创建服务文件

`/etc/systemd/system/btc-agent-scheduler.service`:

```ini
[Unit]
Description=Bitcoin Research Agent Scheduler
After=network.target

[Service]
Type=simple
User=btcagent
WorkingDirectory=/home/btcagent/bitcoin-research-agent
Environment="OPENAI_API_KEY=sk-..."
ExecStart=/usr/bin/python3 /home/btcagent/bitcoin-research-agent/src/scheduler/task_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 启用服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable btc-agent-scheduler

# 启动服务
sudo systemctl start btc-agent-scheduler

# 查看状态
sudo systemctl status btc-agent-scheduler

# 查看日志
journalctl -u btc-agent-scheduler -f
```

---

## 📊 监控和维护

### 1. 日志管理

```bash
# 日志位置
logs/scheduler_YYYYMMDD.log  # 每日日志
logs/notifications_YYYYMMDD.json  # 通知记录

# 查看最新日志
tail -f logs/scheduler_$(date +%Y%m%d).log

# 清理旧日志（保留 30 天）
find logs -name "scheduler_*.log" -mtime +30 -delete
```

### 2. 报告管理

```bash
# 报告位置
reports/daily_report_YYYYMMDD.md  # 每日报告
reports/weekly_report_YYYYMMDD.md  # 每周报告

# 查看最新报告
cat reports/daily_report_$(date +%Y%m%d).md
```

### 3. 健康检查

创建 `scripts/health_check.sh`:

```bash
#!/bin/bash
# 健康检查脚本

# 检查今天的报告是否生成
TODAY=$(date +%Y%m%d)
REPORT="reports/daily_report_$TODAY.md"

if [ -f "$REPORT" ]; then
    echo "✅ 今日报告已生成"
    exit 0
else
    echo "❌ 今日报告未生成！"
    # 发送告警（可选）
    exit 1
fi
```

### 4. 告警通知

可以集成多种通知方式：

#### Email 通知（示例）

```python
import smtplib
from email.mime.text import MIMEText

def send_email_notification(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'btc-agent@example.com'
    msg['To'] = 'admin@example.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email', 'your-password')
        server.send_message(msg)
```

#### Slack 通知（示例）

```python
import requests

def send_slack_notification(message):
    webhook_url = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    payload = {'text': message}
    requests.post(webhook_url, json=payload)
```

---

## 🔒 安全建议

### 1. API Key 管理

```bash
# 不要在代码中硬编码 API Key
# 使用环境变量
export OPENAI_API_KEY=sk-...

# 或使用密钥管理工具
# - AWS Secrets Manager
# - Azure Key Vault
# - HashiCorp Vault
```

### 2. 权限控制

```bash
# 脚本和配置文件权限
chmod 700 start_scheduler.sh
chmod 600 configs/schedule_config.yaml

# 日志目录权限
chmod 755 logs
chmod 644 logs/*.log
```

### 3. 网络安全

- 使用 HTTPS 访问 API
- 配置防火墙规则
- 限制出站连接

---

## 🐛 故障排除

### 问题 1: 任务没有执行

**检查**:
```bash
# 1. 检查服务状态
systemctl status btc-agent-scheduler  # Linux
Get-ScheduledTask -TaskName "BTC Agent*"  # Windows

# 2. 检查日志
tail -f logs/scheduler_*.log

# 3. 手动运行测试
python src/scheduler/task_scheduler.py --run-once daily_analysis
```

### 问题 2: API 错误

**检查**:
```bash
# 1. 验证 API Key
echo $OPENAI_API_KEY

# 2. 测试 API 连接
python -c "from openai import OpenAI; client = OpenAI(); print(client.models.list())"
```

### 问题 3: 内存不足

**解决方案**:
```bash
# 限制 Python 内存使用
export MALLOC_ARENA_MAX=2

# 或在 systemd service 中限制
MemoryLimit=512M
```

---

## 📚 参考资源

- **Python Schedule**: https://schedule.readthedocs.io/
- **Cron**: https://crontab.guru/
- **Systemd**: https://www.freedesktop.org/software/systemd/man/systemd.service.html
- **Docker**: https://docs.docker.com/

---

## ✅ 检查清单

部署前确认：

- [ ] 已安装所有依赖 (`pip install -r requirements.txt`)
- [ ] 已配置 API Key
- [ ] 已测试手动运行 (`--run-once`)
- [ ] 已配置定时任务
- [ ] 已设置日志记录
- [ ] 已配置告警通知（可选）
- [ ] 已设置健康检查（可选）
- [ ] 已配置自动重启
- [ ] 已测试完整流程

---

**更新日期**: 2025-10-26  
**版本**: v1.0.0  
**维护**: Bitcoin Research Agent Team

