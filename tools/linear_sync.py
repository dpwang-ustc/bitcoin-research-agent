#!/usr/bin/env python3
"""
Linear Issue 同步工具

功能：
1. 列出所有 Bitcoin Research Agent 的 Issues
2. 基于代码实现情况评估任务完成度
3. 自动更新 Linear Issue 状态
4. 生成开发进度报告
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 任务与代码文件映射
TASK_CODE_MAPPING = {
    "WAL-10": {
        "title": "收集市场行情数据",
        "files": ["src/data_loader.py"],
        "status": "partial",  # partial, not_started, completed
        "completion": 0.6,
        "next_steps": [
            "添加 Binance API 集成",
            "添加 CoinGecko API 集成",
            "添加资金费率数据",
            "实现实时数据流"
        ]
    },
    "WAL-11": {
        "title": "收集链上数据",
        "files": ["src/data/onchain_collector.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "注册 Glassnode / CryptoQuant API",
            "实现 UTXO 分布数据收集",
            "实现活跃地址数据收集",
            "实现大额转账监控"
        ]
    },
    "WAL-12": {
        "title": "收集宏观与新闻数据",
        "files": ["src/data/macro_collector.py", "src/data/news_collector.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "集成 FRED API (DXY, VIX)",
            "添加黄金价格数据",
            "集成 NewsAPI / CryptoPanic",
            "实现新闻情绪预处理"
        ]
    },
    "WAL-13": {
        "title": "数据清洗与特征提取",
        "files": ["src/feature_engineering.py"],
        "status": "partial",
        "completion": 0.4,
        "next_steps": [
            "实现多数据源时间对齐",
            "添加缺失值填补策略",
            "添加异常值检测",
            "添加更多技术指标 (RSI, MACD, Bollinger)",
            "实现资金流动指标"
        ]
    },
    "WAL-14": {
        "title": "市场状态识别模型",
        "files": ["src/model/market_regime.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "实现 Hidden Markov Model",
            "实现 K-Means 聚类分析",
            "定义市场状态标签",
            "评估模型准确性"
        ]
    },
    "WAL-15": {
        "title": "波动率与流动性分析",
        "files": ["src/analysis/volatility_analysis.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "实现 GARCH 模型",
            "计算隐含波动率",
            "分析现货期货价差",
            "订单簿深度分析"
        ]
    },
    "WAL-16": {
        "title": "主力资金追踪",
        "files": ["src/analysis/whale_tracking.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "识别大额地址",
            "监控交易所热钱包",
            "分析资金流向",
            "构建鲸鱼活动指标"
        ]
    },
    "WAL-17": {
        "title": "情绪与新闻影响建模",
        "files": ["src/analysis/sentiment_analysis.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "集成 LLM API (GPT-4 / Claude)",
            "实现新闻情绪分类",
            "构建情绪指数",
            "分析价格影响滞后性"
        ]
    },
    "WAL-18": {
        "title": "生成可视化面板",
        "files": ["src/dashboard/app.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "设置 Streamlit 项目",
            "创建行情展示组件",
            "创建指标可视化组件",
            "添加交互式图表"
        ]
    },
    "WAL-19": {
        "title": "自动生成周报",
        "files": ["src/reports/weekly_report.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "设计周报模板",
            "实现数据汇总逻辑",
            "集成 LLM 生成报告",
            "配置定时任务"
        ]
    },
    "WAL-20": {
        "title": "报告摘要智能体",
        "files": ["src/model/agent_reasoner.py"],
        "status": "partial",
        "completion": 0.2,
        "next_steps": [
            "集成 LangChain",
            "增强推理能力",
            "实现多维度分析",
            "生成自然语言洞察"
        ]
    },
    "WAL-21": {
        "title": "在 Cursor 中构建项目仓库",
        "files": ["README.md", "requirements.txt", "src/"],
        "status": "partial",
        "completion": 0.7,
        "next_steps": [
            "完善项目文档",
            "添加单元测试",
            "配置 CI/CD",
            "发布到 GitHub"
        ]
    },
    "WAL-22": {
        "title": "集成 LangChain / Autogen 智能体框架",
        "files": ["src/agents/"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "安装 LangChain",
            "设计智能体架构",
            "实现工具调用",
            "构建任务调度器"
        ]
    },
    "WAL-23": {
        "title": "数据定时更新机制",
        "files": ["scripts/scheduler.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "选择调度框架 (APScheduler)",
            "配置定时任务",
            "实现错误告警",
            "添加日志监控"
        ]
    },
    "WAL-24": {
        "title": "模型与可视化版本管理",
        "files": [".dvc/config", "mlruns/"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "安装并配置 DVC",
            "安装并配置 MLflow",
            "版本化数据集",
            "版本化模型"
        ]
    },
    "WAL-25": {
        "title": "设计项目网站或看板",
        "files": ["website/"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "选择技术方案 (Notion / Next.js)",
            "设计网站结构",
            "实现功能展示",
            "部署上线"
        ]
    },
    "WAL-26": {
        "title": "编写论文或白皮书",
        "files": ["docs/paper/"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "整理研究方法",
            "撰写系统架构",
            "总结实验结果",
            "发布论文"
        ]
    },
    "WAL-27": {
        "title": "公开展示 Demo",
        "files": ["src/dashboard/app.py"],
        "status": "not_started",
        "completion": 0.0,
        "next_steps": [
            "部署 Streamlit 应用",
            "录制演示视频",
            "编写使用文档",
            "公开发布"
        ]
    }
}


class LinearSyncTool:
    """Linear Issue 同步工具类"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
    def check_file_exists(self, filepath: str) -> bool:
        """检查文件是否存在"""
        full_path = self.project_root / filepath
        return full_path.exists()
    
    def analyze_task_status(self, task_id: str) -> Dict:
        """分析任务状态"""
        if task_id not in TASK_CODE_MAPPING:
            return {"error": f"Task {task_id} not found"}
        
        task_info = TASK_CODE_MAPPING[task_id]
        files_status = []
        
        for filepath in task_info["files"]:
            exists = self.check_file_exists(filepath)
            files_status.append({
                "file": filepath,
                "exists": exists
            })
        
        # 计算实际完成度（基于文件存在情况）
        files_exist_count = sum(1 for f in files_status if f["exists"])
        auto_completion = files_exist_count / len(files_status) if files_status else 0
        
        return {
            "task_id": task_id,
            "title": task_info["title"],
            "manual_completion": task_info["completion"],
            "auto_completion": auto_completion,
            "status": task_info["status"],
            "files": files_status,
            "next_steps": task_info["next_steps"]
        }
    
    def generate_progress_report(self) -> str:
        """生成项目进度报告"""
        report_lines = [
            "# Bitcoin Research Agent - 开发进度报告",
            f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "---\n"
        ]
        
        # 统计数据
        total_tasks = len(TASK_CODE_MAPPING)
        completed_tasks = sum(1 for t in TASK_CODE_MAPPING.values() if t["status"] == "completed")
        partial_tasks = sum(1 for t in TASK_CODE_MAPPING.values() if t["status"] == "partial")
        not_started_tasks = sum(1 for t in TASK_CODE_MAPPING.values() if t["status"] == "not_started")
        
        avg_completion = sum(t["completion"] for t in TASK_CODE_MAPPING.values()) / total_tasks
        
        report_lines.append("## 📊 总体进度\n")
        report_lines.append(f"- 总任务数: {total_tasks}")
        report_lines.append(f"- 已完成: {completed_tasks} ({completed_tasks/total_tasks*100:.1f}%)")
        report_lines.append(f"- 进行中: {partial_tasks} ({partial_tasks/total_tasks*100:.1f}%)")
        report_lines.append(f"- 未开始: {not_started_tasks} ({not_started_tasks/total_tasks*100:.1f}%)")
        report_lines.append(f"- **平均完成度: {avg_completion*100:.1f}%**\n")
        
        # 进度条
        progress_bar_length = 50
        filled = int(avg_completion * progress_bar_length)
        bar = "█" * filled + "░" * (progress_bar_length - filled)
        report_lines.append(f"```\n[{bar}] {avg_completion*100:.1f}%\n```\n")
        
        report_lines.append("\n---\n")
        
        # 按阶段分组
        phases = {
            "数据收集与处理": ["WAL-10", "WAL-11", "WAL-12", "WAL-13"],
            "模型构建与分析": ["WAL-14", "WAL-15", "WAL-16", "WAL-17"],
            "可视化与报告": ["WAL-18", "WAL-19", "WAL-20"],
            "智能体与自动化": ["WAL-22", "WAL-23"],
            "工程化与展示": ["WAL-21", "WAL-24", "WAL-25", "WAL-26", "WAL-27"]
        }
        
        for phase_name, task_ids in phases.items():
            report_lines.append(f"\n## {phase_name}\n")
            
            for task_id in task_ids:
                status_info = self.analyze_task_status(task_id)
                status_emoji = {
                    "completed": "✅",
                    "partial": "🔄",
                    "not_started": "⬜"
                }.get(status_info["status"], "❓")
                
                report_lines.append(f"\n### {status_emoji} {task_id}: {status_info['title']}")
                report_lines.append(f"**完成度**: {status_info['manual_completion']*100:.0f}%  ")
                report_lines.append(f"**状态**: {status_info['status']}\n")
                
                # 文件状态
                report_lines.append("**相关文件**:")
                for file_info in status_info["files"]:
                    file_emoji = "✓" if file_info["exists"] else "✗"
                    report_lines.append(f"- {file_emoji} `{file_info['file']}`")
                
                # 下一步
                if status_info["next_steps"]:
                    report_lines.append("\n**下一步行动**:")
                    for step in status_info["next_steps"][:3]:  # 只显示前3个
                        report_lines.append(f"- [ ] {step}")
                
                report_lines.append("")
        
        # 建议
        report_lines.append("\n---\n")
        report_lines.append("## 🎯 当前建议\n")
        
        # 找出可以立即开始的任务
        ready_tasks = []
        for task_id, task_info in TASK_CODE_MAPPING.items():
            if task_info["status"] in ["not_started", "partial"]:
                ready_tasks.append((task_id, task_info))
        
        # 按优先级排序（基于任务编号）
        ready_tasks.sort(key=lambda x: x[0])
        
        report_lines.append("### 推荐下一步任务（按优先级排序）:\n")
        for i, (task_id, task_info) in enumerate(ready_tasks[:5], 1):
            report_lines.append(f"{i}. **{task_id}**: {task_info['title']} ({task_info['completion']*100:.0f}% 完成)")
        
        return "\n".join(report_lines)
    
    def list_active_tasks(self) -> List[Dict]:
        """列出当前活跃的任务（部分完成 + 未开始的前3个）"""
        active = []
        
        # 部分完成的任务
        for task_id, task_info in TASK_CODE_MAPPING.items():
            if task_info["status"] == "partial":
                active.append({
                    "task_id": task_id,
                    "title": task_info["title"],
                    "completion": task_info["completion"],
                    "priority": "high"
                })
        
        # 未开始但优先级高的任务（WAL-10 到 WAL-15）
        priority_tasks = [f"WAL-{i}" for i in range(10, 16)]
        for task_id in priority_tasks:
            if task_id in TASK_CODE_MAPPING and TASK_CODE_MAPPING[task_id]["status"] == "not_started":
                active.append({
                    "task_id": task_id,
                    "title": TASK_CODE_MAPPING[task_id]["title"],
                    "completion": 0,
                    "priority": "medium"
                })
        
        return active[:5]  # 返回前5个


def main():
    """主函数"""
    import sys
    import io
    
    # 设置 UTF-8 输出（兼容 Windows）
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    tool = LinearSyncTool()
    
    # 生成进度报告
    report = tool.generate_progress_report()
    
    # 保存报告
    report_path = Path("PROGRESS_REPORT.md")
    report_path.write_text(report, encoding="utf-8")
    print(f"✓ 进度报告已生成: {report_path}")
    
    # 显示活跃任务
    print("\n>> 当前推荐任务:")
    active_tasks = tool.list_active_tasks()
    for task in active_tasks:
        priority_mark = "[高]" if task["priority"] == "high" else "[中]"
        print(f"  {priority_mark} {task['task_id']}: {task['title']} ({task['completion']*100:.0f}%)")
    
    print(f"\n>> 查看完整报告: {report_path}")


if __name__ == "__main__":
    main()

