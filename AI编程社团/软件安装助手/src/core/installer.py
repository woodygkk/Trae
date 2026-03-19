import subprocess
import sys
import threading
import time
import ctypes
from ctypes import wintypes
from typing import Callable, Optional

from src.core.config_manager import SoftwareConfig
from src.utils.logger import InstallLogger

# Windows API 常量
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008
CREATE_UNICODE_ENVIRONMENT = 0x00000040
STARTF_USESHOWWINDOW = 0x00000001
SW_HIDE = 0


class InstallResult:
    """安装结果"""

    def __init__(self, success: bool, message: str = "", return_code: int = None):
        self.success = success
        self.message = message
        self.return_code = return_code


class Installer:
    """安装执行引擎"""

    # 安装超时时间（秒）
    INSTALL_TIMEOUT = 120

    def __init__(self, logger: InstallLogger):
        self.logger = logger
        self.is_running = False
        self.is_paused = False
        self.should_stop = False

    def install_single(self, config: SoftwareConfig) -> InstallResult:
        """
        安装单个软件

        Args:
            config: 软件配置

        Returns:
            安装结果
        """
        self.logger.info(f"开始安装 {config.name}{config.file_ext}...")

        try:
            # 构建安装命令
            cmd = self._build_command(config)

            # 执行安装（隐藏命令行窗口）
            if sys.platform == 'win32':
                # 使用 DETACHED_PROCESS 标志创建分离进程
                # 先将命令写入临时批处理文件执行
                import tempfile
                import os as os_module

                # 创建临时批处理文件
                with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as bat_file:
                    bat_file.write(cmd)
                    bat_path = bat_file.name

                try:
                    # 使用 DETACHED_PROCESS 运行批处理文件
                    result = subprocess.run(
                        ['cmd', '/c', bat_path],
                        capture_output=True,
                        text=True,
                        timeout=self.INSTALL_TIMEOUT,
                        creationflags=DETACHED_PROCESS
                    )
                finally:
                    # 删除临时批处理文件
                    try:
                        os_module.unlink(bat_path)
                    except:
                        pass
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.INSTALL_TIMEOUT,
                    shell=True
                )

            if result.returncode == 0:
                self.logger.success(f"{config.name} 安装完成")
                return InstallResult(True, "安装成功", result.returncode)
            else:
                error_msg = result.stderr if result.stderr else "安装程序返回非零退出码"
                self.logger.error(f"{config.name} 安装失败: {error_msg}")
                return InstallResult(False, error_msg, result.returncode)

        except subprocess.TimeoutExpired:
            self.logger.error(f"{config.name} 安装超时（超过{self.INSTALL_TIMEOUT}秒）")
            return InstallResult(False, f"安装超时（超过{self.INSTALL_TIMEOUT}秒）", -1)
        except Exception as e:
            self.logger.error(f"{config.name} 安装异常: {str(e)}")
            return InstallResult(False, str(e), -1)

    def _build_command(self, config: SoftwareConfig) -> str:
        """
        构建安装命令

        Args:
            config: 软件配置

        Returns:
            完整的安装命令
        """
        cmd = f'"{config.path}"'

        # 添加静默安装参数
        if config.params:
            cmd += f" {config.params}"

        # 添加自定义安装路径（如果有）- BAT/CMD文件不需要
        ext = config.file_ext.lower()
        if config.install_path and ext in [".exe", ".msi"]:
            if ext == ".msi":
                # MSI 使用 INSTALLPATH 属性
                cmd += f' INSTALLPATH="{config.install_path}"'
            else:
                # EXE 通常使用 /D 参数
                cmd += f' /D="{config.install_path}"'

        return cmd

    def batch_install(
        self,
        software_list: list,
        on_progress: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> dict:
        """
        批量安装

        Args:
            software_list: 软件列表
            on_progress: 进度回调 (current, total, software_name, status)
            on_error: 错误回调 (software_config, error_message) -> "retry"/"skip"/"stop"

        Returns:
            安装统计结果
        """
        self.is_running = True
        self.should_stop = False

        total = len(software_list)
        success_count = 0
        failed_count = 0
        skipped_count = 0

        for i, config in enumerate(software_list):
            # 检查是否停止
            if self.should_stop:
                self.logger.warning("安装已终止")
                break

            # 跳过未启用的软件
            if not config.enabled:
                config.status = "skipped"
                skipped_count += 1
                if on_progress:
                    on_progress(i + 1, total, config.name, "skipped")
                continue

            # 更新状态为安装中
            config.status = "installing"

            # 执行安装
            result = self.install_single(config)

            if result.success:
                config.status = "success"
                success_count += 1
                if on_progress:
                    on_progress(i + 1, total, config.name, "success")
            else:
                config.status = "failed"
                failed_count += 1

                # 询问用户如何处理
                if on_error:
                    action = on_error(config, result.message)
                    if action == "retry":
                        # 重试一次
                        result = self.install_single(config)
                        if result.success:
                            config.status = "success"
                            success_count += 1
                            failed_count -= 1
                            if on_progress:
                                on_progress(i + 1, total, config.name, "success")
                        else:
                            if on_progress:
                                on_progress(i + 1, total, config.name, "failed")
                    elif action == "skip":
                        config.status = "skipped"
                        skipped_count += 1
                        failed_count -= 1
                        if on_progress:
                            on_progress(i + 1, total, config.name, "skipped")
                    elif action == "stop":
                        self.should_stop = True
                        break
                else:
                    if on_progress:
                        on_progress(i + 1, total, config.name, "failed")

        self.is_running = False

        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "skipped": skipped_count
        }

    def stop(self):
        """停止安装"""
        self.should_stop = True
