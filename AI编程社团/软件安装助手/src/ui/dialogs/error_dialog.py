from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class ErrorDialog(QDialog):
    """错误处理对话框 - 安装失败时弹窗"""

    def __init__(self, software_name: str, error_message: str, parent=None):
        super().__init__(parent)
        self.software_name = software_name
        self.error_message = error_message
        self.action = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("安装失败")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # 警告图标和标题
        title_layout = QHBoxLayout()
        warning_label = QLabel("⚠")
        warning_label.setStyleSheet("font-size: 24px; color: #f44336;")
        title_layout.addWidget(warning_label)

        title_text = QLabel(f"安装失败: {self.software_name}")
        title_text.setStyleSheet("font-size: 16px; font-weight: bold; color: #f44336;")
        title_layout.addWidget(title_text)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        # 错误信息
        error_label = QLabel(f"错误信息:\n{self.error_message}")
        error_label.setStyleSheet("color: #666; padding: 10px;")
        error_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(error_label)

        # 分隔线
        separator = QLabel("─" * 40)
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setStyleSheet("color: #ccc;")
        layout.addWidget(separator)

        # 提示文字
        hint_label = QLabel("请选择处理方式:")
        hint_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(hint_label)

        # 按钮
        btn_layout = QVBoxLayout()

        # 重试按钮
        self.retry_btn = QPushButton("重试")
        self.retry_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.retry_btn.clicked.connect(lambda: self.set_action("retry"))
        btn_layout.addWidget(self.retry_btn)

        # 跳过按钮
        self.skip_btn = QPushButton("跳过此软件")
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.skip_btn.clicked.connect(lambda: self.set_action("skip"))
        btn_layout.addWidget(self.skip_btn)

        # 终止按钮
        self.stop_btn = QPushButton("终止全部安装")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.stop_btn.clicked.connect(lambda: self.set_action("stop"))
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def set_action(self, action: str):
        """设置操作并关闭对话框"""
        self.action = action
        self.accept()

    def get_action(self) -> str:
        """获取用户选择的操作"""
        return self.action or "skip"
