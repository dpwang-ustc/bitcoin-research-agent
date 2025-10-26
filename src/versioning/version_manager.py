"""
Bitcoin Research Agent - 版本管理系统

功能：
1. 输出版本管理（报告、图表、数据）
2. 配置版本追踪
3. 运行历史记录
4. 可重现性保证
5. 版本比较和回滚

作者：Bitcoin Research Agent Team
日期：2025-10-26
"""

import os
import json
import hashlib
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys


class VersionManager:
    """
    版本管理器
    
    管理所有输出、配置和运行历史的版本
    """
    
    def __init__(
        self,
        version_dir: str = 'versions',
        verbose: bool = True
    ):
        """
        初始化版本管理器
        
        Args:
            version_dir: 版本存储目录
            verbose: 是否打印详细信息
        """
        self.version_dir = Path(version_dir)
        self.verbose = verbose
        
        # 创建目录结构
        self.version_dir.mkdir(exist_ok=True)
        (self.version_dir / 'runs').mkdir(exist_ok=True)
        (self.version_dir / 'artifacts').mkdir(exist_ok=True)
        (self.version_dir / 'configs').mkdir(exist_ok=True)
        
        self.log("✅ VersionManager 初始化完成")
    
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[VersionManager] {message}")
    
    # ==================== 版本创建 ====================
    
    def create_version(
        self,
        task_name: str,
        config: Dict[str, Any],
        outputs: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建新版本
        
        Args:
            task_name: 任务名称（如 'daily_analysis', 'weekly_report'）
            config: 配置参数
            outputs: 输出文件路径 {'report': 'path/to/report.md', ...}
            metadata: 额外元数据
        
        Returns:
            version_id: 版本ID
        """
        # 生成版本ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        version_id = f"{task_name}_{timestamp}"
        
        self.log(f"创建版本: {version_id}")
        
        # 创建版本目录
        version_path = self.version_dir / 'runs' / version_id
        version_path.mkdir(exist_ok=True)
        
        # 保存配置
        config_file = version_path / 'config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # 复制输出文件
        artifacts = {}
        for key, source_path in outputs.items():
            if os.path.exists(source_path):
                # 计算文件哈希
                file_hash = self._compute_file_hash(source_path)
                
                # 复制到版本目录
                dest_path = version_path / Path(source_path).name
                shutil.copy2(source_path, dest_path)
                
                artifacts[key] = {
                    'original_path': source_path,
                    'versioned_path': str(dest_path),
                    'hash': file_hash,
                    'size': os.path.getsize(source_path)
                }
            else:
                self.log(f"⚠️  文件不存在: {source_path}", 'warning')
        
        # 创建版本元数据
        version_metadata = {
            'version_id': version_id,
            'task_name': task_name,
            'created_at': datetime.now().isoformat(),
            'config': config,
            'artifacts': artifacts,
            'metadata': metadata or {},
            'git_commit': self._get_git_commit(),
            'python_version': sys.version.split()[0],
            'reproducible': True
        }
        
        # 保存元数据
        metadata_file = version_path / 'metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(version_metadata, f, indent=2, ensure_ascii=False)
        
        # 更新运行历史
        self._update_run_history(version_metadata)
        
        self.log(f"✅ 版本创建完成: {version_id}")
        return version_id
    
    # ==================== 版本查询 ====================
    
    def list_versions(
        self,
        task_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        列出版本
        
        Args:
            task_name: 筛选任务名称
            limit: 返回数量限制
        
        Returns:
            版本列表
        """
        runs_dir = self.version_dir / 'runs'
        
        if not runs_dir.exists():
            return []
        
        # 获取所有版本
        versions = []
        for version_dir in sorted(runs_dir.iterdir(), reverse=True):
            if not version_dir.is_dir():
                continue
            
            metadata_file = version_dir / 'metadata.json'
            if not metadata_file.exists():
                continue
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 筛选任务
            if task_name and metadata.get('task_name') != task_name:
                continue
            
            versions.append(metadata)
            
            if len(versions) >= limit:
                break
        
        return versions
    
    def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """
        获取版本详情
        
        Args:
            version_id: 版本ID
        
        Returns:
            版本元数据
        """
        version_path = self.version_dir / 'runs' / version_id
        metadata_file = version_path / 'metadata.json'
        
        if not metadata_file.exists():
            self.log(f"❌ 版本不存在: {version_id}", 'error')
            return None
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_latest_version(self, task_name: str) -> Optional[Dict[str, Any]]:
        """
        获取最新版本
        
        Args:
            task_name: 任务名称
        
        Returns:
            版本元数据
        """
        versions = self.list_versions(task_name=task_name, limit=1)
        return versions[0] if versions else None
    
    # ==================== 版本比较 ====================
    
    def compare_versions(
        self,
        version_id1: str,
        version_id2: str
    ) -> Dict[str, Any]:
        """
        比较两个版本
        
        Args:
            version_id1: 版本1 ID
            version_id2: 版本2 ID
        
        Returns:
            比较结果
        """
        v1 = self.get_version(version_id1)
        v2 = self.get_version(version_id2)
        
        if not v1 or not v2:
            return {'error': '版本不存在'}
        
        comparison = {
            'version1': version_id1,
            'version2': version_id2,
            'config_diff': self._compare_dicts(v1.get('config', {}), v2.get('config', {})),
            'time_diff': (
                datetime.fromisoformat(v2['created_at']) - 
                datetime.fromisoformat(v1['created_at'])
            ).total_seconds(),
            'artifacts_diff': self._compare_artifacts(
                v1.get('artifacts', {}),
                v2.get('artifacts', {})
            )
        }
        
        return comparison
    
    # ==================== 可重现性 ====================
    
    def check_reproducibility(self, version_id: str) -> Dict[str, Any]:
        """
        检查版本可重现性
        
        Args:
            version_id: 版本ID
        
        Returns:
            可重现性检查结果
        """
        version = self.get_version(version_id)
        
        if not version:
            return {'reproducible': False, 'error': '版本不存在'}
        
        checks = {
            'version_id': version_id,
            'config_available': bool(version.get('config')),
            'artifacts_available': all(
                os.path.exists(a['versioned_path']) 
                for a in version.get('artifacts', {}).values()
            ),
            'git_commit_recorded': bool(version.get('git_commit')),
            'python_version': version.get('python_version'),
            'reproducible': True
        }
        
        # 验证文件完整性
        for key, artifact in version.get('artifacts', {}).items():
            versioned_path = artifact.get('versioned_path')
            if os.path.exists(versioned_path):
                current_hash = self._compute_file_hash(versioned_path)
                if current_hash != artifact.get('hash'):
                    checks['reproducible'] = False
                    checks['integrity_error'] = f"{key} hash mismatch"
        
        return checks
    
    # ==================== 版本恢复 ====================
    
    def restore_version(
        self,
        version_id: str,
        output_dir: str = 'restored'
    ) -> bool:
        """
        恢复版本
        
        Args:
            version_id: 版本ID
            output_dir: 输出目录
        
        Returns:
            是否成功
        """
        version = self.get_version(version_id)
        
        if not version:
            self.log(f"❌ 版本不存在: {version_id}", 'error')
            return False
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 复制配置
        version_path = self.version_dir / 'runs' / version_id
        shutil.copy2(version_path / 'config.json', output_path / 'config.json')
        
        # 复制输出文件
        for key, artifact in version.get('artifacts', {}).items():
            versioned_path = artifact.get('versioned_path')
            if os.path.exists(versioned_path):
                dest_path = output_path / Path(versioned_path).name
                shutil.copy2(versioned_path, dest_path)
                self.log(f"恢复文件: {key} -> {dest_path}")
        
        self.log(f"✅ 版本恢复完成: {version_id} -> {output_dir}")
        return True
    
    # ==================== 运行历史 ====================
    
    def _update_run_history(self, version_metadata: Dict[str, Any]):
        """更新运行历史"""
        history_file = self.version_dir / 'run_history.jsonl'
        
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(version_metadata, ensure_ascii=False) + '\n')
    
    def get_run_history(
        self,
        task_name: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取运行历史
        
        Args:
            task_name: 筛选任务名称
            limit: 返回数量限制
        
        Returns:
            运行历史列表
        """
        history_file = self.version_dir / 'run_history.jsonl'
        
        if not history_file.exists():
            return []
        
        history = []
        with open(history_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if task_name and record.get('task_name') != task_name:
                        continue
                    history.append(record)
                except:
                    pass
        
        # 返回最新的记录
        return list(reversed(history))[:limit]
    
    # ==================== 辅助函数 ====================
    
    def _compute_file_hash(self, filepath: str) -> str:
        """计算文件 MD5 哈希"""
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()
    
    def _get_git_commit(self) -> Optional[str]:
        """获取当前 Git commit"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return None
    
    def _compare_dicts(self, dict1: Dict, dict2: Dict) -> Dict[str, Any]:
        """比较两个字典"""
        diff = {
            'added': {},
            'removed': {},
            'changed': {}
        }
        
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        
        # 新增的键
        for key in keys2 - keys1:
            diff['added'][key] = dict2[key]
        
        # 删除的键
        for key in keys1 - keys2:
            diff['removed'][key] = dict1[key]
        
        # 修改的键
        for key in keys1 & keys2:
            if dict1[key] != dict2[key]:
                diff['changed'][key] = {
                    'old': dict1[key],
                    'new': dict2[key]
                }
        
        return diff
    
    def _compare_artifacts(
        self,
        artifacts1: Dict[str, Any],
        artifacts2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """比较输出文件"""
        diff = {
            'added': list(set(artifacts2.keys()) - set(artifacts1.keys())),
            'removed': list(set(artifacts1.keys()) - set(artifacts2.keys())),
            'changed': []
        }
        
        for key in set(artifacts1.keys()) & set(artifacts2.keys()):
            if artifacts1[key].get('hash') != artifacts2[key].get('hash'):
                diff['changed'].append({
                    'key': key,
                    'size_diff': artifacts2[key].get('size', 0) - artifacts1[key].get('size', 0)
                })
        
        return diff
    
    # ==================== 统计信息 ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        runs_dir = self.version_dir / 'runs'
        
        if not runs_dir.exists():
            return {'total_versions': 0}
        
        versions = list(runs_dir.iterdir())
        
        # 按任务统计
        task_counts = {}
        total_size = 0
        
        for version_dir in versions:
            if not version_dir.is_dir():
                continue
            
            metadata_file = version_dir / 'metadata.json'
            if not metadata_file.exists():
                continue
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            task_name = metadata.get('task_name', 'unknown')
            task_counts[task_name] = task_counts.get(task_name, 0) + 1
            
            # 计算总大小
            for artifact in metadata.get('artifacts', {}).values():
                total_size += artifact.get('size', 0)
        
        return {
            'total_versions': len(versions),
            'task_counts': task_counts,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'version_dir': str(self.version_dir)
        }


def main():
    """示例：版本管理器使用"""
    # Force UTF-8 output for Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - 版本管理器示例")
    print("=" * 70 + "\n")
    
    # 创建版本管理器
    vm = VersionManager(verbose=True)
    
    # 示例：创建版本
    print("\n1. 创建版本示例")
    print("-" * 70)
    
    version_id = vm.create_version(
        task_name='test_task',
        config={
            'llm_model': 'gpt-4o-mini',
            'temperature': 0.7,
            'max_tokens': 1024
        },
        outputs={
            'report': 'reports/daily_report_20251026.md'
        },
        metadata={
            'description': '测试版本',
            'author': 'test'
        }
    )
    
    print(f"\n创建的版本ID: {version_id}")
    
    # 示例：列出版本
    print("\n2. 列出版本")
    print("-" * 70)
    
    versions = vm.list_versions(limit=5)
    for v in versions:
        print(f"- {v['version_id']} ({v['task_name']}) - {v['created_at']}")
    
    # 示例：获取统计信息
    print("\n3. 统计信息")
    print("-" * 70)
    
    stats = vm.get_statistics()
    print(f"总版本数: {stats['total_versions']}")
    print(f"总大小: {stats['total_size_mb']} MB")
    print(f"任务统计: {stats['task_counts']}")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()

