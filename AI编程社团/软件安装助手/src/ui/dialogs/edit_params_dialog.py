from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt

from src.core.config_manager import SoftwareConfig


class EditParamsDialog(QDialog):
    """参数编辑对话框"""

    def __init__(self, config: SoftwareConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"编辑 - {self.config.name}")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # 软件信息
        info_group = QGroupBox("软件信息")
        info_layout = QFormLayout()

        info_layout.addRow("软件名称:", QLabel(self.config.name))
        info_layout.addRow("文件类型:", QLabel(self.config.file_ext.upper()))
        info_layout.addRow("文件路径:", QLabel(self.config.path))

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 安装参数
        params_group = QGroupBox("安装参数")
        params_layout = QFormLayout()

        self.params_input = QLineEdit()
        self.params_input.setText(self.config.params)
        self.params_input.setPlaceholderText("如: /S /norestart")
        params_layout.addRow("静默安装参数:", self.params_input)

        self.install_path_input = QLineEdit()
        self.install_path_input.setText(self.config.install_path)
        self.install_path_input.setPlaceholderText("留空使用默认安装路径")
        params_layout.addRow("自定义安装路径:", self.install_path_input)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # 常用参数提示
        hint_label = QLabel(
            "提示:\n"
            "• EXE 常用参数: /S, /silent, /quiet, -s\n"
            "• MSI 常用参数: /qn /norestart, /passive\n"
            "• 自定义路径格式: /D=\"C:\\Program Files\\App\""
        )
        hint_label.setStyleSheet("color: #666; font-size: 12px;")
        hint_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(hint_label)

        # 按钮
        btn_layout = QHBoxLayout()

        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_params(self) -> str:
        """获取参数"""
        return self.params_input.text().strip()

    def get_install_path(self) -> str:
        """获取安装路径"""
        return self.install_path_input.text().strip()
