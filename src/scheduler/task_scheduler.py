"""
Bitcoin Research Agent - 定时任务调度器

功能：
1. 自动定时更新数据
2. 自动生成分析报告
3. 日志记录和错误通知
4. 灵活的任务配置

支持：
- Python schedule 库（跨平台）
- Windows Task Scheduler 配置
- Linux cron 配置

作者：Bitcoin Research Agent Team
日期：2025-10-26
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import yaml
import json
import traceback

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入 Agent
try:
    from src.agent import BitcoinResearchAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    print("Warning: BitcoinResearchAgent not available")


class ScheduledTaskManager:
    """
    定时任务管理器
    
    功能：
    1. 管理多个定时任务
    2. 自动执行数据更新和分析
    3. 日志记录和错误处理
    4. 灵活的配置管理
    """
    
    def __init__(
        self,
        config_path: str = 'configs/schedule_config.yaml',
        log_dir: str = 'logs',
        verbose: bool = True
    ):
        """
        初始化任务调度器
        
        Args:
            config_path: 配置文件路径
            log_dir: 日志目录
            verbose: 是否打印详细信息
        """
        self.config_path = config_path
        self.log_dir = log_dir
        self.verbose = verbose
        
        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 配置日志
        self._setup_logging()
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化 Agent
        self.agent = None
        if AGENT_AVAILABLE and self.config.get('agent', {}).get('enabled', True):
            self._init_agent()
        
        # 注册任务
        self.tasks = {}
        self._register_tasks()
        
        self.log("✅ ScheduledTaskManager 初始化完成")
    
    def log(self, message: str, level: str = 'info'):
        """打印日志"""
        if self.verbose:
            print(f"[Scheduler] {message}")
        
        # 同时写入日志文件
        if level == 'info':
            logging.info(message)
        elif level == 'warning':
            logging.warning(message)
        elif level == 'error':
            logging.error(message)
    
    def _setup_logging(self):
        """配置日志系统"""
        log_file = os.path.join(
            self.log_dir,
            f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                self.log(f"配置文件加载成功: {self.config_path}")
                return config
            except Exception as e:
                self.log(f"配置文件加载失败: {e}，使用默认配置", 'warning')
        else:
            self.log(f"配置文件不存在: {self.config_path}，使用默认配置", 'warning')
        
        # 默认配置
        return {
            'agent': {
                'enabled': True,
                'llm_provider': 'openai',
                'llm_model': 'gpt-4o-mini',
                'api_key': None  # 从环境变量读取
            },
            'tasks': {
                'daily_analysis': {
                    'enabled': True,
                    'time': '09:00',
                    'description': '每日市场分析'
                },
                'weekly_report': {
                    'enabled': True,
                    'day': 'monday',
                    'time': '08:00',
                    'description': '每周市场报告'
                },
                'data_backup': {
                    'enabled': False,
                    'time': '23:00',
                    'description': '每日数据备份'
                }
            },
            'notifications': {
                'on_success': False,
                'on_error': True,
                'methods': ['log', 'file']  # 可扩展: email, slack, discord
            },
            'output': {
                'report_dir': 'reports',
                'data_dir': 'data/processed'
            }
        }
    
    def _init_agent(self):
        """初始化 AI Agent"""
        try:
            agent_config = self.config.get('agent', {})
            
            self.agent = BitcoinResearchAgent(
                llm_provider=agent_config.get('llm_provider', 'openai'),
                llm_model=agent_config.get('llm_model', 'gpt-4o-mini'),
                api_key=agent_config.get('api_key') or os.getenv('OPENAI_API_KEY'),
                verbose=False  # Agent 内部不打印太多信息
            )
            
            self.log("✅ AI Agent 初始化成功")
            
        except Exception as e:
            self.log(f"⚠️  AI Agent 初始化失败: {e}", 'warning')
            self.agent = None
    
    def _register_tasks(self):
        """注册所有任务"""
        tasks_config = self.config.get('tasks', {})
        
        # 每日分析任务
        if tasks_config.get('daily_analysis', {}).get('enabled'):
            daily_time = tasks_config['daily_analysis'].get('time', '09:00')
            schedule.every().day.at(daily_time).do(self.task_daily_analysis)
            self.tasks['daily_analysis'] = {
                'schedule': f"每天 {daily_time}",
                'description': '每日市场分析',
                'last_run': None,
                'status': 'active'
            }
            self.log(f"✅ 注册任务: 每日分析 ({daily_time})")
        
        # 每周报告任务
        if tasks_config.get('weekly_report', {}).get('enabled'):
            weekly_day = tasks_config['weekly_report'].get('day', 'monday')
            weekly_time = tasks_config['weekly_report'].get('time', '08:00')
            
            # 根据星期配置
            if weekly_day.lower() == 'monday':
                schedule.every().monday.at(weekly_time).do(self.task_weekly_report)
            elif weekly_day.lower() == 'friday':
                schedule.every().friday.at(weekly_time).do(self.task_weekly_report)
            # 可扩展其他星期
            
            self.tasks['weekly_report'] = {
                'schedule': f"每周 {weekly_day} {weekly_time}",
                'description': '每周市场报告',
                'last_run': None,
                'status': 'active'
            }
            self.log(f"✅ 注册任务: 每周报告 ({weekly_day} {weekly_time})")
        
        # 数据备份任务
        if tasks_config.get('data_backup', {}).get('enabled'):
            backup_time = tasks_config['data_backup'].get('time', '23:00')
            schedule.every().day.at(backup_time).do(self.task_data_backup)
            self.tasks['data_backup'] = {
                'schedule': f"每天 {backup_time}",
                'description': '数据备份',
                'last_run': None,
                'status': 'active'
            }
            self.log(f"✅ 注册任务: 数据备份 ({backup_time})")
    
    # ==================== 任务函数 ====================
    
    def task_daily_analysis(self):
        """任务：每日市场分析"""
        task_name = "daily_analysis"
        self.log(f"\n{'='*70}")
        self.log(f"开始执行: {task_name}")
        self.log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'='*70}")
        
        try:
            if not self.agent:
                self.log("Agent 未初始化，跳过任务", 'warning')
                return
            
            # 执行分析
            result = self.agent.run("生成今日比特币市场完整分析报告")
            
            # 保存报告
            if result.get('report'):
                output_dir = self.config.get('output', {}).get('report_dir', 'reports')
                os.makedirs(output_dir, exist_ok=True)
                
                report_file = os.path.join(
                    output_dir,
                    f"daily_report_{datetime.now().strftime('%Y%m%d')}.md"
                )
                
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(result['report'])
                
                self.log(f"✅ 报告已保存: {report_file}")
            
            # 更新任务状态
            self.tasks[task_name]['last_run'] = datetime.now().isoformat()
            self.tasks[task_name]['status'] = 'success'
            
            # 通知
            self._notify_success(task_name, "每日分析完成")
            
        except Exception as e:
            self.log(f"❌ 任务执行失败: {e}", 'error')
            self.log(traceback.format_exc(), 'error')
            
            self.tasks[task_name]['status'] = 'failed'
            self._notify_error(task_name, str(e))
        
        finally:
            self.log(f"{'='*70}\n")
    
    def task_weekly_report(self):
        """任务：每周市场报告"""
        task_name = "weekly_report"
        self.log(f"\n{'='*70}")
        self.log(f"开始执行: {task_name}")
        self.log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'='*70}")
        
        try:
            if not self.agent:
                self.log("Agent 未初始化，跳过任务", 'warning')
                return
            
            # 执行分析
            result = self.agent.run("生成本周比特币市场完整分析报告和展望")
            
            # 保存报告
            if result.get('report'):
                output_dir = self.config.get('output', {}).get('report_dir', 'reports')
                os.makedirs(output_dir, exist_ok=True)
                
                report_file = os.path.join(
                    output_dir,
                    f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
                )
                
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(result['report'])
                
                self.log(f"✅ 周报已保存: {report_file}")
            
            # 更新任务状态
            self.tasks[task_name]['last_run'] = datetime.now().isoformat()
            self.tasks[task_name]['status'] = 'success'
            
            # 通知
            self._notify_success(task_name, "每周报告完成")
            
        except Exception as e:
            self.log(f"❌ 任务执行失败: {e}", 'error')
            self.log(traceback.format_exc(), 'error')
            
            self.tasks[task_name]['status'] = 'failed'
            self._notify_error(task_name, str(e))
        
        finally:
            self.log(f"{'='*70}\n")
    
    def task_data_backup(self):
        """任务：数据备份"""
        task_name = "data_backup"
        self.log(f"\n{'='*70}")
        self.log(f"开始执行: {task_name}")
        self.log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'='*70}")
        
        try:
            import shutil
            from datetime import datetime
            
            # 备份目录
            data_dir = self.config.get('output', {}).get('data_dir', 'data/processed')
            backup_dir = os.path.join('backups', datetime.now().strftime('%Y%m%d'))
            
            if not os.path.exists(data_dir):
                self.log(f"数据目录不存在: {data_dir}", 'warning')
                return
            
            # 创建备份
            os.makedirs(backup_dir, exist_ok=True)
            shutil.copytree(data_dir, os.path.join(backup_dir, 'processed'), dirs_exist_ok=True)
            
            self.log(f"✅ 数据备份完成: {backup_dir}")
            
            # 更新任务状态
            self.tasks[task_name]['last_run'] = datetime.now().isoformat()
            self.tasks[task_name]['status'] = 'success'
            
        except Exception as e:
            self.log(f"❌ 备份失败: {e}", 'error')
            self.tasks[task_name]['status'] = 'failed'
            self._notify_error(task_name, str(e))
        
        finally:
            self.log(f"{'='*70}\n")
    
    # ==================== 通知系统 ====================
    
    def _notify_success(self, task_name: str, message: str):
        """成功通知"""
        notify_config = self.config.get('notifications', {})
        
        if not notify_config.get('on_success', False):
            return
        
        methods = notify_config.get('methods', ['log'])
        
        if 'log' in methods:
            self.log(f"✅ [{task_name}] {message}")
        
        if 'file' in methods:
            self._save_notification('success', task_name, message)
    
    def _notify_error(self, task_name: str, error: str):
        """错误通知"""
        notify_config = self.config.get('notifications', {})
        
        if not notify_config.get('on_error', True):
            return
        
        methods = notify_config.get('methods', ['log'])
        
        if 'log' in methods:
            self.log(f"❌ [{task_name}] 错误: {error}", 'error')
        
        if 'file' in methods:
            self._save_notification('error', task_name, error)
    
    def _save_notification(self, level: str, task_name: str, message: str):
        """保存通知到文件"""
        notify_file = os.path.join(
            self.log_dir,
            f"notifications_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
        notification = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'task': task_name,
            'message': message
        }
        
        # 读取现有通知
        notifications = []
        if os.path.exists(notify_file):
            try:
                with open(notify_file, 'r', encoding='utf-8') as f:
                    notifications = json.load(f)
            except:
                pass
        
        # 添加新通知
        notifications.append(notification)
        
        # 保存
        with open(notify_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False)
    
    # ==================== 运行和管理 ====================
    
    def run_once(self, task_name: str):
        """立即运行一次指定任务"""
        self.log(f"手动执行任务: {task_name}")
        
        if task_name == 'daily_analysis':
            self.task_daily_analysis()
        elif task_name == 'weekly_report':
            self.task_weekly_report()
        elif task_name == 'data_backup':
            self.task_data_backup()
        else:
            self.log(f"未知任务: {task_name}", 'warning')
    
    def list_tasks(self):
        """列出所有任务"""
        self.log("\n" + "="*70)
        self.log("已注册任务")
        self.log("="*70)
        
        for task_name, task_info in self.tasks.items():
            self.log(f"\n任务: {task_name}")
            self.log(f"  描述: {task_info['description']}")
            self.log(f"  调度: {task_info['schedule']}")
            self.log(f"  状态: {task_info['status']}")
            self.log(f"  上次运行: {task_info.get('last_run', 'Never')}")
        
        self.log("\n" + "="*70 + "\n")
    
    def start(self):
        """启动调度器（阻塞运行）"""
        self.log("\n" + "="*70)
        self.log("🚀 Bitcoin Research Agent 定时任务调度器启动")
        self.log("="*70)
        
        self.list_tasks()
        
        self.log("调度器运行中... (Ctrl+C 退出)")
        self.log("="*70 + "\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            self.log("\n\n" + "="*70)
            self.log("⏸️  调度器已停止")
            self.log("="*70)


def main():
    """主函数 - 启动调度器"""
    import argparse
    
    # Force UTF-8 output for Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    parser = argparse.ArgumentParser(description='Bitcoin Research Agent 定时任务调度器')
    parser.add_argument('--config', default='configs/schedule_config.yaml', help='配置文件路径')
    parser.add_argument('--run-once', help='立即运行指定任务（daily_analysis/weekly_report/data_backup）')
    parser.add_argument('--list', action='store_true', help='列出所有任务')
    
    args = parser.parse_args()
    
    # 创建调度器
    scheduler = ScheduledTaskManager(
        config_path=args.config,
        verbose=True
    )
    
    # 列出任务
    if args.list:
        scheduler.list_tasks()
        return
    
    # 运行单次任务
    if args.run_once:
        scheduler.run_once(args.run_once)
        return
    
    # 启动调度器
    scheduler.start()


if __name__ == '__main__':
    main()

