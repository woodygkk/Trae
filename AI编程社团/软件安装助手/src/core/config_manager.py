import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


def is_winpe() -> bool:
    """检测是否在WinPE环境下"""
    # 检查是否在WinPE环境
    # WinPE通常没有用户配置文件目录
    if hasattr(sys, 'winpe'):
        return sys.winpe
    # 通过检查环境判断
    try:
        # WinPE下某些系统路径不存在
        if not os.path.exists(os.path.expanduser("~")):
            return True
        # 检查注册表或特定文件
        if os.path.exists(r"C:\Windows\System32\winpe"):
            return True
    except:
        pass
    return False


class SoftwareConfig:
    """软件配置数据类"""

    def __init__(self, name: str, path: str, file_ext: str,
                 params: str = "", install_path: str = "",
                 enabled: bool = True, order: int = 0):
        self.name = name
        self.path = path
        self.file_ext = file_ext
        self.params = params
        self.install_path = install_path
        self.enabled = enabled
        self.order = order
        self.status = "pending"  # pending, installing, success, failed, skipped

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "file_ext": self.file_ext,
            "params": self.params,
            "install_path": self.install_path,
            "enabled": self.enabled,
            "order": self.order,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SoftwareConfig':
        config = cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            file_ext=data.get("file_ext", ""),
            params=data.get("params", ""),
            install_path=data.get("install_path", ""),
            enabled=data.get("enabled", True),
            order=data.get("order", 0)
        )
        config.status = data.get("status", "pending")
        return config


class ConfigManager:
    """配置管理器 - 负责保存和加载软件配置"""

    def __init__(self, config_file: str = "config/software_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.software_list: List[SoftwareConfig] = []
        self.packages_dir: str = ""

    def load(self) -> List[SoftwareConfig]:
        """加载配置文件"""
        if not self.config_file.exists():
            return []

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.packages_dir = data.get("packages_dir", "")
            self.software_list = [
                SoftwareConfig.from_dict(item)
                for item in data.get("software_list", [])
            ]

            # 按order排序
            self.software_list.sort(key=lambda x: x.order)

            return self.software_list
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return []

    def save(self, packages_dir: str = "", software_list: List[SoftwareConfig] = None):
        """
        保存配置文件

        Args:
            packages_dir: 软件包目录
            software_list: 软件列表
        """
        if software_list is not None:
            self.software_list = software_list
        if packages_dir:
            self.packages_dir = packages_dir

        data = {
            "packages_dir": self.packages_dir,
            "software_list": [
                config.to_dict() for config in self.software_list
            ]
        }

        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # WinPE环境下可能是只读系统，保存失败不崩溃
            print(f"保存配置失败: {e}")

    def update_software(self, index: int, params: str = None, install_path: str = None):
        """更新单个软件配置"""
        if 0 <= index < len(self.software_list):
            if params is not None:
                self.software_list[index].params = params
            if install_path is not None:
                self.software_list[index].install_path = install_path

    def get_software(self, index: int) -> Optional[SoftwareConfig]:
        """获取指定索引的软件配置"""
        if 0 <= index < len(self.software_list):
            return self.software_list[index]
        return None

    def get_software_by_name(self, name: str) -> Optional[SoftwareConfig]:
        """根据名称查找软件配置"""
        for config in self.software_list:
            if config.name == name:
                return config
        return None

    def set_software_status(self, index: int, status: str):
        """设置软件安装状态"""
        if 0 <= index < len(self.software_list):
            self.software_list[index].status = status
