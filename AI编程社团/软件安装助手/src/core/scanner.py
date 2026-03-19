import os
from pathlib import Path
from typing import List

from src.core.config_manager import SoftwareConfig
from src.utils.silent_params import get_silent_params


# 统一默认安装路径
DEFAULT_INSTALL_PATH = r"C:\Program Files (x86)"


def get_default_install_path(software_name: str) -> str:
    """
    获取默认安装路径

    Args:
        software_name: 软件名称（用于将来扩展特定软件的路径）

    Returns:
        默认安装路径
    """
    return DEFAULT_INSTALL_PATH


class Scanner:
    """软件包扫描器 - 扫描指定目录下的安装包"""

    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = ['.exe', '.msi', '.bat', '.cmd']

    def __init__(self):
        self.scanned_software: List[SoftwareConfig] = []

    def scan_directory(self, directory: str) -> List[SoftwareConfig]:
        """
        扫描目录下的安装包

        Args:
            directory: 要扫描的目录路径

        Returns:
            软件配置列表
        """
        self.scanned_software = []

        if not directory or not os.path.exists(directory):
            return []

        directory = Path(directory)

        # 遍历目录下的所有文件
        order = 0
        for file_path in sorted(directory.iterdir()):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    name = file_path.stem  # 文件名（不含扩展名）

                    # 获取静默安装参数和默认路径
                    params = get_silent_params(name, ext)
                    install_path = get_default_install_path(name)

                    config = SoftwareConfig(
                        name=name,
                        path=str(file_path.absolute()),
                        file_ext=ext,
                        params=params,
                        install_path=install_path,
                        order=order
                    )
                    self.scanned_software.append(config)
                    order += 1

        return self.scanned_software

    def scan_with_runtime_libs(self, packages_dir: str, runtime_libs_dir: str) -> List[SoftwareConfig]:
        """
        扫描软件包目录，并合并运行库

        Args:
            packages_dir: 软件包目录
            runtime_libs_dir: 运行库目录

        Returns:
            合并后的软件列表（运行库排在前面）
        """
        # 先扫描运行库
        runtime_software = []
        if runtime_libs_dir and os.path.exists(runtime_libs_dir):
            runtime_dir = Path(runtime_libs_dir)
            order = 0
            for file_path in sorted(runtime_dir.iterdir()):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext in self.SUPPORTED_EXTENSIONS:
                        name = file_path.stem
                        params = get_silent_params(name, ext)
                        install_path = get_default_install_path(name)
                        config = SoftwareConfig(
                            name=name,
                            path=str(file_path.absolute()),
                            file_ext=ext,
                            params=params,
                            install_path=install_path,
                            order=order
                        )
                        runtime_software.append(config)
                        order += 1

        # 扫描软件包
        packages_software = self.scan_directory(packages_dir)

        # 调整软件包的顺序（接在运行库后面）
        for config in packages_software:
            config.order += len(runtime_software)

        # 合并：运行库在前，软件在后
        return runtime_software + packages_software
