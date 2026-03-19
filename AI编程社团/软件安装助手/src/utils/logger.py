import logging
import os
import sys
from datetime import datetime
from pathlib import Path


class InstallLogger:
    """安装日志管理器"""

    def __init__(self, log_dir: str = "logs"):
        """
        初始化日志管理器

        Args:
            log_dir: 日志目录
        """
        self.log_dir = None
        self.log_file = None
        self.file_handler = None
        self.in_memory_only = False
        self.log_file_created = False  # 标记日志文件是否已创建

        # 只设置日志目录，不立即创建文件
        try:
            self.log_dir = Path(log_dir)
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            self.in_memory_only = True

        # 配置日志（不添加文件处理器）
        self.logger = logging.getLogger("InstallLogger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        # 内存日志（用于界面显示）
        self.memory_logs = []

    def _ensure_log_file(self):
        """确保日志文件已创建"""
        if self.log_file_created or self.in_memory_only:
            return

        try:
            # 生成日志文件名（按日期）
            self.log_file = self.log_dir / f"install_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            self.file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            self.file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s: %(message)s',
                datefmt='%H:%M:%S'
            )
            self.file_handler.setFormatter(file_formatter)
            self.logger.addHandler(self.file_handler)
            self.log_file_created = True
        except Exception:
            self.in_memory_only = True

    def add_log(self, message: str, level: str = "INFO"):
        """
        添加日志

        Args:
            message: 日志消息
            level: 日志级别 (INFO/WARNING/ERROR/SUCCESS)
        """
        # 确保日志文件已创建
        self._ensure_log_file()

        # 记录到文件
        if level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "SUCCESS":
            self.logger.info(f"✓ {message}")

        # 保存到内存
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.memory_logs.append({
            'time': timestamp,
            'message': message,
            'level': level
        })

    def info(self, message: str):
        self.add_log(message, "INFO")

    def warning(self, message: str):
        self.add_log(message, "WARNING")

    def error(self, message: str):
        self.add_log(message, "ERROR")

    def success(self, message: str):
        self.add_log(message, "SUCCESS")

    def get_logs(self) -> list:
        """获取所有日志"""
        return self.memory_logs.copy()

    def clear(self):
        """清空内存日志"""
        self.memory_logs.clear()

    def get_log_file_path(self) -> str:
        """获取日志文件路径"""
        if self.in_memory_only or not self.log_file:
            return "（内存日志，仅界面显示）"
        return str(self.log_file)
