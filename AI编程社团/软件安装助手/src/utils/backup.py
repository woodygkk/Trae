import os
import shutil
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class BackupItem:
    """备份项"""
    name: str
    source_path: str
    size: int  # bytes
    category: str  # desktop/download/document/favorite


class FileBackup:
    """文件备份管理器"""

    def __init__(self):
        self.backup_items: List[BackupItem] = []

    def get_user_dirs(self) -> Dict[str, str]:
        """
        获取用户目录

        Returns:
            目录字典 {category: path}
        """
        user_home = Path.home()

        dirs = {
            'desktop': user_home / 'Desktop',
            'download': user_home / 'Downloads',
            'document': user_home / 'Documents',
            'favorite': user_home / 'Favorites'
        }

        # 过滤不存在的目录
        return {k: str(v) for k, v in dirs.items() if v.exists()}

    def scan_directory(self, directory: str, category: str) -> List[BackupItem]:
        """
        扫描目录下的文件

        Args:
            directory: 目录路径
            category: 类别名称

        Returns:
            文件列表
        """
        items = []
        dir_path = Path(directory)

        if not dir_path.exists():
            return items

        try:
            for item in dir_path.iterdir():
                if item.is_file():
                    try:
                        size = item.stat().st_size
                        items.append(BackupItem(
                            name=item.name,
                            source_path=str(item.absolute()),
                            size=size,
                            category=category
                        ))
                    except (PermissionError, OSError):
                        pass
        except (PermissionError, OSError):
            pass

        return items

    def scan_all(self) -> List[BackupItem]:
        """
        扫描所有用户目录

        Returns:
            所有文件列表
        """
        self.backup_items = []
        user_dirs = self.get_user_dirs()

        for category, directory in user_dirs.items():
            items = self.scan_directory(directory, category)
            self.backup_items.extend(items)

        return self.backup_items

    def get_category_items(self, category: str) -> List[BackupItem]:
        """获取指定类别的文件"""
        return [item for item in self.backup_items if item.category == category]

    def get_category_size(self, category: str) -> int:
        """获取指定类别的总大小"""
        return sum(item.size for item in self.get_category_items(category))

    def backup(self,
               backup_dir: str,
               categories: List[str] = None,
               progress_callback=None) -> Dict[str, int]:
        """
        备份文件

        Args:
            backup_dir: 备份目标目录
            categories: 要备份的类别列表，None表示全部
            progress_callback: 进度回调 (current, total, filename)

        Returns:
            统计结果 {success, failed, skipped}
        """
        if categories is None:
            categories = ['desktop', 'download', 'document', 'favorite']

        result = {'success': 0, 'failed': 0, 'skipped': 0}
        backup_path = Path(backup_dir)

        # 创建备份目录结构
        for category in categories:
            (backup_path / category).mkdir(parents=True, exist_ok=True)

        # 统计要备份的文件
        to_backup = [item for item in self.backup_items
                     if item.category in categories]

        total = len(to_backup)

        for i, item in enumerate(to_backup):
            if progress_callback:
                progress_callback(i + 1, total, item.name)

            try:
                source = Path(item.source_path)
                dest = backup_path / item.category / item.name

                # 如果目标文件已存在，跳过
                if dest.exists():
                    result['skipped'] += 1
                    continue

                # 复制文件
                shutil.copy2(source, dest)
                result['success'] += 1

            except Exception:
                result['failed'] += 1

        return result

    @staticmethod
    def format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
