"""
Bitcoin Research Agent - 版本管理命令行工具

用法：
    python src/versioning/cli.py list
    python src/versioning/cli.py show <version_id>
    python src/versioning/cli.py compare <v1> <v2>
    python src/versioning/cli.py restore <version_id>
    python src/versioning/cli.py stats
"""

import sys
import os
import argparse
from datetime import datetime
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.versioning import VersionManager


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def cmd_list(args):
    """列出版本"""
    vm = VersionManager(verbose=False)
    
    versions = vm.list_versions(
        task_name=args.task,
        limit=args.limit
    )
    
    if not versions:
        print("没有找到版本")
        return
    
    print("\n" + "=" * 80)
    print(f"  版本列表 (共 {len(versions)} 个)")
    print("=" * 80)
    
    for v in versions:
        print(f"\n📦 {v['version_id']}")
        print(f"   任务: {v['task_name']}")
        print(f"   时间: {v['created_at']}")
        print(f"   配置: {len(v.get('config', {}))} 项")
        print(f"   输出: {len(v.get('artifacts', {}))} 个文件")
        
        # 显示输出文件
        for key, artifact in v.get('artifacts', {}).items():
            size = format_size(artifact.get('size', 0))
            print(f"      - {key}: {size}")
    
    print("\n" + "=" * 80)


def cmd_show(args):
    """显示版本详情"""
    vm = VersionManager(verbose=False)
    
    version = vm.get_version(args.version_id)
    
    if not version:
        print(f"❌ 版本不存在: {args.version_id}")
        return
    
    print("\n" + "=" * 80)
    print(f"  版本详情: {args.version_id}")
    print("=" * 80)
    
    print(f"\n📋 基本信息:")
    print(f"   版本ID: {version['version_id']}")
    print(f"   任务名称: {version['task_name']}")
    print(f"   创建时间: {version['created_at']}")
    print(f"   Git Commit: {version.get('git_commit', 'N/A')}")
    print(f"   Python版本: {version.get('python_version', 'N/A')}")
    print(f"   可重现: {'✅' if version.get('reproducible') else '❌'}")
    
    print(f"\n⚙️  配置参数:")
    for key, value in version.get('config', {}).items():
        print(f"   {key}: {value}")
    
    print(f"\n📦 输出文件:")
    for key, artifact in version.get('artifacts', {}).items():
        size = format_size(artifact.get('size', 0))
        print(f"   {key}:")
        print(f"      路径: {artifact.get('versioned_path')}")
        print(f"      大小: {size}")
        print(f"      哈希: {artifact.get('hash', 'N/A')[:16]}...")
    
    if version.get('metadata'):
        print(f"\n📝 元数据:")
        for key, value in version.get('metadata', {}).items():
            print(f"   {key}: {value}")
    
    print("\n" + "=" * 80)


def cmd_compare(args):
    """比较版本"""
    vm = VersionManager(verbose=False)
    
    comparison = vm.compare_versions(args.version1, args.version2)
    
    if 'error' in comparison:
        print(f"❌ {comparison['error']}")
        return
    
    print("\n" + "=" * 80)
    print(f"  版本比较")
    print("=" * 80)
    
    print(f"\n版本1: {comparison['version1']}")
    print(f"版本2: {comparison['version2']}")
    print(f"时间差: {comparison['time_diff'] / 3600:.2f} 小时")
    
    config_diff = comparison.get('config_diff', {})
    
    if config_diff.get('added'):
        print(f"\n➕ 新增配置:")
        for key, value in config_diff['added'].items():
            print(f"   {key}: {value}")
    
    if config_diff.get('removed'):
        print(f"\n➖ 删除配置:")
        for key, value in config_diff['removed'].items():
            print(f"   {key}: {value}")
    
    if config_diff.get('changed'):
        print(f"\n🔄 修改配置:")
        for key, change in config_diff['changed'].items():
            print(f"   {key}:")
            print(f"      旧: {change['old']}")
            print(f"      新: {change['new']}")
    
    artifacts_diff = comparison.get('artifacts_diff', {})
    
    if artifacts_diff.get('added'):
        print(f"\n➕ 新增文件: {', '.join(artifacts_diff['added'])}")
    
    if artifacts_diff.get('removed'):
        print(f"\n➖ 删除文件: {', '.join(artifacts_diff['removed'])}")
    
    if artifacts_diff.get('changed'):
        print(f"\n🔄 修改文件:")
        for change in artifacts_diff['changed']:
            size_diff = change['size_diff']
            sign = '+' if size_diff > 0 else ''
            print(f"   {change['key']}: {sign}{format_size(abs(size_diff))}")
    
    print("\n" + "=" * 80)


def cmd_restore(args):
    """恢复版本"""
    vm = VersionManager(verbose=True)
    
    success = vm.restore_version(args.version_id, args.output)
    
    if success:
        print(f"\n✅ 版本已恢复到: {args.output}")
    else:
        print(f"\n❌ 恢复失败")


def cmd_check(args):
    """检查可重现性"""
    vm = VersionManager(verbose=False)
    
    result = vm.check_reproducibility(args.version_id)
    
    print("\n" + "=" * 80)
    print(f"  可重现性检查: {args.version_id}")
    print("=" * 80)
    
    print(f"\n配置可用: {'✅' if result.get('config_available') else '❌'}")
    print(f"文件可用: {'✅' if result.get('artifacts_available') else '❌'}")
    print(f"Git记录: {'✅' if result.get('git_commit_recorded') else '❌'}")
    print(f"Python版本: {result.get('python_version', 'N/A')}")
    
    if result.get('reproducible'):
        print(f"\n✅ 该版本可重现")
    else:
        print(f"\n❌ 该版本不可重现")
        if result.get('integrity_error'):
            print(f"   错误: {result['integrity_error']}")
    
    print("\n" + "=" * 80)


def cmd_stats(args):
    """显示统计信息"""
    vm = VersionManager(verbose=False)
    
    stats = vm.get_statistics()
    
    print("\n" + "=" * 80)
    print("  版本管理统计")
    print("=" * 80)
    
    print(f"\n总版本数: {stats['total_versions']}")
    print(f"总大小: {stats['total_size_mb']} MB")
    print(f"存储位置: {stats['version_dir']}")
    
    if stats.get('task_counts'):
        print(f"\n任务统计:")
        for task, count in stats['task_counts'].items():
            print(f"   {task}: {count} 个版本")
    
    print("\n" + "=" * 80)


def cmd_history(args):
    """显示运行历史"""
    vm = VersionManager(verbose=False)
    
    history = vm.get_run_history(task_name=args.task, limit=args.limit)
    
    if not history:
        print("没有运行历史")
        return
    
    print("\n" + "=" * 80)
    print(f"  运行历史 (最近 {len(history)} 次)")
    print("=" * 80)
    
    for record in history:
        print(f"\n⏰ {record['created_at']}")
        print(f"   版本: {record['version_id']}")
        print(f"   任务: {record['task_name']}")
        print(f"   输出: {len(record.get('artifacts', {}))} 个文件")
    
    print("\n" + "=" * 80)


def main():
    """主函数"""
    # Force UTF-8 output for Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    parser = argparse.ArgumentParser(
        description='Bitcoin Research Agent 版本管理工具'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list 命令
    parser_list = subparsers.add_parser('list', help='列出版本')
    parser_list.add_argument('--task', help='筛选任务名称')
    parser_list.add_argument('--limit', type=int, default=10, help='显示数量')
    
    # show 命令
    parser_show = subparsers.add_parser('show', help='显示版本详情')
    parser_show.add_argument('version_id', help='版本ID')
    
    # compare 命令
    parser_compare = subparsers.add_parser('compare', help='比较版本')
    parser_compare.add_argument('version1', help='版本1 ID')
    parser_compare.add_argument('version2', help='版本2 ID')
    
    # restore 命令
    parser_restore = subparsers.add_parser('restore', help='恢复版本')
    parser_restore.add_argument('version_id', help='版本ID')
    parser_restore.add_argument('--output', default='restored', help='输出目录')
    
    # check 命令
    parser_check = subparsers.add_parser('check', help='检查可重现性')
    parser_check.add_argument('version_id', help='版本ID')
    
    # stats 命令
    parser_stats = subparsers.add_parser('stats', help='统计信息')
    
    # history 命令
    parser_history = subparsers.add_parser('history', help='运行历史')
    parser_history.add_argument('--task', help='筛选任务名称')
    parser_history.add_argument('--limit', type=int, default=20, help='显示数量')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    commands = {
        'list': cmd_list,
        'show': cmd_show,
        'compare': cmd_compare,
        'restore': cmd_restore,
        'check': cmd_check,
        'stats': cmd_stats,
        'history': cmd_history
    }
    
    command_func = commands.get(args.command)
    if command_func:
        command_func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

