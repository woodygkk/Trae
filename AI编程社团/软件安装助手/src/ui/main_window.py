from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QMessageBox, QProgressBar, QGroupBox, QLineEdit, QCheckBox,
    QTabWidget, QScrollArea, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor

from src.core.config_manager import ConfigManager, SoftwareConfig
from src.core.scanner import Scanner, DEFAULT_INSTALL_PATH
from src.core.installer import Installer, InstallResult
from src.utils.logger import InstallLogger
from src.utils.backup import FileBackup


class InstallThread(QThread):
    """安装线程"""

    progress_signal = pyqtSignal(int, int, str, str)  # current, total, name, status
    error_signal = pyqtSignal(object, str)  # config, error_message
    finished_signal = pyqtSignal(dict)  # result

    def __init__(self, installer: Installer, software_list: list):
        super().__init__()
        self.installer = installer
        self.software_list = software_list

    def run(self):
        result = self.installer.batch_install(
            self.software_list,
            on_progress=self._on_progress,
            on_error=self._on_error
        )
        self.finished_signal.emit(result)

    def _on_progress(self, current, total, name, status):
        self.progress_signal.emit(current, total, name, status)

    def _on_error(self, config, error_message):
        self.error_signal.emit(config, error_message)


class MainWindow(QWidget):
    """主窗口"""

    def __init__(self):
        super().__init__()

        # 初始化组件
        self.config_manager = ConfigManager()
        self.scanner = Scanner()
        self.logger = InstallLogger()
        self.installer = Installer(self.logger)
        self.backup = FileBackup()

        # 运行库目录
        self.runtime_libs_dir = "resources/runtime_libs"

        # 软件列表
        self.software_list: list[SoftwareConfig] = []

        # 安装线程
        self.install_thread: InstallThread = None

        # 初始化UI
        self.init_ui()

        # 加载配置
        self.load_config()

    def check_winpe(self) -> bool:
        """检测是否在WinPE环境下"""
        import os
        try:
            # WinPE下用户目录通常不存在
            user_home = os.path.expanduser("~")
            if not os.path.exists(user_home):
                return True
            # 检查WinPE特征文件
            if os.path.exists(r"C:\Windows\System32\winpe"):
                return True
        except:
            pass
        return False

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("批量软件安装工具 v1.0  作者: IT运维工具")
        self.setMinimumSize(900, 750)

        # ===== 全局样式 =====
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
                font-size: 15px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #333;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                gridline-color: #f0f0f0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #333;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 2px solid #2196F3;
                font-weight: bold;
                color: #333;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
                background-color: #f0f0f0;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #bdbdbd;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #64B5F6);
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 2px;
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #666;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2196F3;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e3f2fd;
            }
            QLabel {
                color: #333;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 创建Tab控件
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # ===== Tab 1: 软件安装 =====
        install_widget = QWidget()
        install_layout = QVBoxLayout()
        install_layout.setSpacing(10)

        # ===== 1. 软件包目录选择 =====
        dir_group = QGroupBox("软件包目录")
        dir_layout = QHBoxLayout()

        self.dir_label = QLabel("当前目录: 未选择")
        self.dir_label.setStyleSheet("color: #666; padding: 5px;")
        dir_layout.addWidget(self.dir_label, 1)

        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_btn)

        dir_group.setLayout(dir_layout)
        install_layout.addWidget(dir_group)

        # ===== 2. 软件列表 =====
        list_group = QGroupBox("软件列表")
        list_layout = QVBoxLayout()

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "", "序号", "软件名称", "类型", "参数", "安装路径", "状态", "操作"
        ])
        # 隐藏垂直表头（行号）
        self.table.verticalHeader().setVisible(False)
        # 设置列宽度
        self.table.setColumnWidth(0, 40)  # 复选框列
        self.table.setColumnWidth(1, 50)  # 序号列
        self.table.setColumnWidth(3, 60)  # 类型列
        self.table.setColumnWidth(4, 50)  # 参数列
        self.table.setColumnWidth(6, 80)  # 状态列
        self.table.setColumnWidth(7, 80)  # 操作列（编辑按钮）
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # 复选框状态变化时保存
        self.table.itemChanged.connect(self.on_checkbox_changed)
        list_layout.addWidget(self.table)

        # 列表操作按钮
        btn_layout = QHBoxLayout()

        self.scan_btn = QPushButton("扫描文件夹")
        self.scan_btn.clicked.connect(self.scan_software)
        btn_layout.addWidget(self.scan_btn)

        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.clicked.connect(self.clear_list)
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()

        # 全选/反选切换按钮
        self.toggle_select_btn = QPushButton("全选")
        self.toggle_select_btn.clicked.connect(self.toggle_select)
        self.toggle_select_btn.setMinimumWidth(60)
        btn_layout.addWidget(self.toggle_select_btn)

        # 移动按钮
        self.move_up_btn = QPushButton("上移")
        self.move_up_btn.clicked.connect(self.move_up)
        btn_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("下移")
        self.move_down_btn.clicked.connect(self.move_down)
        btn_layout.addWidget(self.move_down_btn)

        list_layout.addLayout(btn_layout)
        list_group.setLayout(list_layout)
        install_layout.addWidget(list_group, 1)

        # ===== 3. 安装日志 =====
        log_group = QGroupBox("安装日志")
        log_layout = QVBoxLayout()

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(2)
        self.log_table.setHorizontalHeaderLabels(["时间", "日志"])
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.log_table.setMaximumHeight(150)
        log_layout.addWidget(self.log_table)

        log_group.setLayout(log_layout)
        install_layout.addWidget(log_group)

        # ===== 4. 进度条 =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m (%p%)")
        install_layout.addWidget(self.progress_bar)

        # ===== 5. 操作按钮 =====
        action_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始批量安装")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #66BB6A);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #43A047, stop:1 #5CB85C);
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.start_btn.clicked.connect(self.start_install)
        action_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止安装")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f44336, stop:1 #E57373);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E53935, stop:1 #EF5350);
            }
            QPushButton:pressed {
                background-color: #C62828;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_install)
        self.stop_btn.setEnabled(False)
        action_layout.addWidget(self.stop_btn)

        action_layout.addStretch()

        # 查看日志按钮
        self.view_log_btn = QPushButton("查看日志文件")
        self.view_log_btn.clicked.connect(self.view_log_file)
        action_layout.addWidget(self.view_log_btn)

        install_layout.addLayout(action_layout)

        # 设置Tab 1
        install_widget.setLayout(install_layout)
        self.tabs.addTab(install_widget, "软件安装")

        # ===== Tab 2: 文件备份 =====
        # 检测WinPE环境
        self.is_winpe = self.check_winpe()

        if self.is_winpe:
            # WinPE环境下显示提示
            backup_widget = QWidget()
            backup_layout = QVBoxLayout()
            warning_label = QLabel(
                "当前运行在WinPE环境下，\n文件备份功能不可用。\n\n"
                "WinPE环境没有用户目录，\n无法进行文件备份。"
            )
            warning_label.setStyleSheet("""
                color: #FF9800;
                font-size: 20px;
                padding: 30px;
                background-color: #FFF8E1;
                border-radius: 10px;
                border: 2px dashed #FFB74D;
            """)
            warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            backup_layout.addWidget(warning_label)
            backup_widget.setLayout(backup_layout)
        else:
            # 正常环境下创建备份功能
            backup_widget = QWidget()
            backup_layout = QVBoxLayout()
            backup_layout.setSpacing(10)

            self.init_backup_ui(backup_layout)

            backup_widget.setLayout(backup_layout)

        self.tabs.addTab(backup_widget, "文件备份")

        # 主布局只包含Tab控件
        self.setLayout(main_layout)

    def browse_directory(self):
        """选择软件包目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择软件包目录",
            self.dir_label.text().replace("当前目录: ", "") or "C:/"
        )

        if directory:
            self.packages_dir = directory
            self.dir_label.setText(f"当前目录: {directory}")
            self.config_manager.packages_dir = directory

            # 自动扫描
            self.scan_software()

    def scan_software(self):
        """扫描软件包"""
        if not hasattr(self, 'packages_dir') or not self.packages_dir:
            QMessageBox.warning(self, "提示", "请先选择软件包目录")
            return

        self.logger.info(f"开始扫描目录: {self.packages_dir}")
        self.logger.info("=" * 40)

        # 扫描软件包（包含运行库）
        self.software_list = self.scanner.scan_with_runtime_libs(
            self.packages_dir,
            self.runtime_libs_dir
        )

        # 更新界面
        self.update_table()
        self.update_log_table()

        self.logger.info(f"扫描完成，共找到 {len(self.software_list)} 个软件")

        # 保存配置
        self.save_config()

    def clear_list(self):
        """清空列表"""
        self.software_list.clear()
        self.update_table()
        self.config_manager.software_list = []
        self.save_config()

    def update_table(self):
        """更新软件列表表格"""
        self.table.setRowCount(len(self.software_list))

        for i, config in enumerate(self.software_list):
            # 复选框
            checkbox = QTableWidgetItem()
            checkbox.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox.setCheckState(Qt.CheckState.Checked if config.enabled else Qt.CheckState.Unchecked)
            checkbox.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, checkbox)

            # 序号（居中显示）
            item = QTableWidgetItem(str(i + 1))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, item)

            # 软件名称
            self.table.setItem(i, 2, QTableWidgetItem(config.name))

            # 类型
            self.table.setItem(i, 3, QTableWidgetItem(config.file_ext.upper()))

            # 参数
            self.table.setItem(i, 4, QTableWidgetItem(config.params))

            # 安装路径
            display_path = config.install_path if config.install_path else DEFAULT_INSTALL_PATH
            self.table.setItem(i, 5, QTableWidgetItem(display_path))

            # 状态
            status_item = QTableWidgetItem(self._get_status_text(config.status))
            status_item.setData(Qt.ItemDataRole.UserRole, config.status)
            self.table.setItem(i, 6, status_item)
            self._update_status_color(status_item, config.status)

            # 操作按钮
            edit_btn = QPushButton("编辑")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_software(idx))
            self.table.setCellWidget(i, 7, edit_btn)

    def on_checkbox_changed(self, item):
        """复选框状态变化时更新配置"""
        if item.column() == 0:  # 复选框列
            row = item.row()
            if 0 <= row < len(self.software_list):
                self.software_list[row].enabled = (item.checkState() == Qt.CheckState.Checked)
                # 如果重新勾选且之前状态是跳过或失败，重置为待安装
                if self.software_list[row].enabled:
                    if self.software_list[row].status in ["skipped", "failed"]:
                        self.software_list[row].status = "pending"
                        # 更新表格显示
                        status_item = self.table.item(row, 6)
                        if status_item:
                            status_item.setText(self._get_status_text("pending"))
                            self._update_status_color(status_item, "pending")
                self.save_config()

    def toggle_select(self):
        """全选/反选切换"""
        # 检查是否全部已选
        all_selected = all(s.enabled for s in self.software_list)

        # 暂时禁用复选框变化信号
        self.table.itemChanged.disconnect()

        if all_selected:
            # 全部已选 -> 反选（取消全部）
            for i in range(len(self.software_list)):
                self.software_list[i].enabled = False
                item = self.table.item(i, 0)
                if item:
                    item.setCheckState(Qt.CheckState.Unchecked)
            self.toggle_select_btn.setText("全选")
        else:
            # 未全选 -> 全选
            for i in range(len(self.software_list)):
                self.software_list[i].enabled = True
                item = self.table.item(i, 0)
                if item:
                    item.setCheckState(Qt.CheckState.Checked)
            self.toggle_select_btn.setText("反选")

        # 重新连接信号
        self.table.itemChanged.connect(self.on_checkbox_changed)
        self.save_config()

    def _get_status_text(self, status: str) -> str:
        status_map = {
            "pending": "待安装",
            "installing": "安装中",
            "success": "已完成",
            "failed": "失败",
            "skipped": "已跳过"
        }
        return status_map.get(status, status)

    def _update_status_color(self, item: QTableWidgetItem, status: str):
        color_map = {
            "pending": "#999999",
            "installing": "#2196F3",
            "success": "#4CAF50",
            "failed": "#f44336",
            "skipped": "#FF9800"
        }
        color = color_map.get(status, "#000000")
        item.setForeground(QColor(color))

    def edit_software(self, index: int):
        """编辑软件配置"""
        from src.ui.dialogs.edit_params_dialog import EditParamsDialog

        config = self.software_list[index]
        dialog = EditParamsDialog(config, self)

        if dialog.exec():
            # 保存修改
            config.params = dialog.get_params()
            config.install_path = dialog.get_install_path()

            # 更新表格
            self.update_table()

            # 保存配置
            self.save_config()

    def move_up(self):
        """上移软件"""
        current_row = self.table.currentRow()
        if current_row > 0:
            self.software_list[current_row], self.software_list[current_row - 1] = \
                self.software_list[current_row - 1], self.software_list[current_row]
            self.update_table()
            self.table.setCurrentCell(current_row - 1, 0)
            self.save_config()

    def move_down(self):
        """下移软件"""
        current_row = self.table.currentRow()
        if current_row < len(self.software_list) - 1:
            self.software_list[current_row], self.software_list[current_row + 1] = \
                self.software_list[current_row + 1], self.software_list[current_row]
            self.update_table()
            self.table.setCurrentCell(current_row + 1, 0)
            self.save_config()

    def update_log_table(self):
        """更新日志表格"""
        logs = self.logger.get_logs()
        self.log_table.setRowCount(len(logs))

        for i, log in enumerate(logs):
            self.log_table.setItem(i, 0, QTableWidgetItem(log['time']))
            self.log_table.setItem(i, 1, QTableWidgetItem(log['message']))

            # 根据日志级别设置颜色
            if log['level'] == 'ERROR':
                self.log_table.item(i, 1).setForeground(QColor("#f44336"))
            elif log['level'] == 'SUCCESS':
                self.log_table.item(i, 1).setForeground(QColor("#4CAF50"))
            elif log['level'] == 'WARNING':
                self.log_table.item(i, 1).setForeground(QColor("#FF9800"))

        # 滚动到底部
        self.log_table.scrollToBottom()

    def start_install(self):
        """开始批量安装"""
        if not self.software_list:
            QMessageBox.warning(self, "提示", "请先扫描软件")
            return

        # 检查是否有待安装的软件
        pending_count = sum(1 for s in self.software_list if s.enabled and s.status in ["pending", "failed"])
        if pending_count == 0:
            QMessageBox.warning(self, "提示", "没有待安装的软件")
            return

        # 确认开始安装
        reply = QMessageBox.question(
            self,
            "确认安装",
            f"即将开始安装 {pending_count} 个软件，是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 重置状态
        for config in self.software_list:
            if config.status in ["pending", "failed"]:
                config.status = "pending"

        # 清空日志
        self.logger.clear()
        self.update_table()
        self.update_log_table()

        # 禁用按钮
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.scan_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)

        # 开始安装
        self.install_thread = InstallThread(self.installer, self.software_list)
        self.install_thread.progress_signal.connect(self.on_install_progress)
        self.install_thread.error_signal.connect(self.on_install_error)
        self.install_thread.finished_signal.connect(self.on_install_finished)
        self.install_thread.start()

    def on_install_progress(self, current: int, total: int, name: str, status: str):
        """安装进度回调"""
        # 更新进度条
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

        # 更新表格中的状态
        for config in self.software_list:
            if config.name == name:
                config.status = status
                break

        self.update_table()
        self.update_log_table()

    def on_install_error(self, config: SoftwareConfig, error_message: str):
        """安装错误回调"""
        from src.ui.dialogs.error_dialog import ErrorDialog

        dialog = ErrorDialog(config.name, error_message, self)
        action = dialog.get_action()

        if action == "retry":
            config.status = "pending"
        elif action == "skip":
            config.status = "skipped"
        elif action == "stop":
            self.installer.stop()

    def on_install_finished(self, result: dict):
        """安装完成回调"""
        # 启用按钮
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.scan_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)

        # 更新日志
        self.logger.info("=" * 40)
        self.logger.info(f"安装完成: 成功 {result['success']} 个, 失败 {result['failed']} 个, 跳过 {result['skipped']} 个")
        self.update_log_table()

        # 提示完成
        QMessageBox.information(
            self,
            "安装完成",
            f"安装完成！\n成功: {result['success']}\n失败: {result['failed']}\n跳过: {result['skipped']}"
        )

    def stop_install(self):
        """停止安装"""
        if self.installer:
            self.installer.stop()
        QMessageBox.information(self, "提示", "正在停止安装...")

    def view_log_file(self):
        """查看日志文件 - 自动打开最新日志"""
        import os
        import glob

        # 查找logs目录下的所有日志文件
        log_dir = "logs"
        if not os.path.exists(log_dir):
            QMessageBox.warning(self, "提示", "日志目录不存在")
            return

        # 查找所有install_*.log文件
        log_files = glob.glob(os.path.join(log_dir, "install_*.log"))
        if not log_files:
            QMessageBox.warning(self, "提示", "没有找到日志文件")
            return

        # 获取最新的日志文件
        latest_log = max(log_files, key=os.path.getmtime)

        # 用系统默认程序打开
        try:
            os.startfile(latest_log)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开日志文件:\n{str(e)}")

    def load_config(self):
        """加载配置"""
        self.software_list = self.config_manager.load()

        if self.config_manager.packages_dir:
            self.packages_dir = self.config_manager.packages_dir
            self.dir_label.setText(f"当前目录: {self.packages_dir}")

        if self.software_list:
            self.update_table()

    def save_config(self):
        """保存配置"""
        self.config_manager.save(self.packages_dir, self.software_list)

    def closeEvent(self, event):
        """关闭窗口时保存配置"""
        self.save_config()
        event.accept()

    # ===== 文件备份功能 =====

    def init_backup_ui(self, layout):
        """初始化备份功能UI"""
        # 备份目标目录
        backup_dir_group = QGroupBox("备份目标目录")
        backup_dir_layout = QHBoxLayout()

        self.backup_dir_label = QLabel("未选择")
        self.backup_dir_label.setStyleSheet("color: #666; padding: 5px;")
        self.backup_dir_label.setWordWrap(True)
        backup_dir_layout.addWidget(self.backup_dir_label, 1)

        self.backup_dir_btn = QPushButton("选择...")
        self.backup_dir_btn.clicked.connect(self.select_backup_dir)
        backup_dir_layout.addWidget(self.backup_dir_btn)

        backup_dir_group.setLayout(backup_dir_layout)
        layout.addWidget(backup_dir_group)

        # 文件分类列表
        files_group = QGroupBox("用户文件分类")
        files_layout = QVBoxLayout()

        # 分类选择
        category_layout = QHBoxLayout()

        self.desktop_check = QCheckBox("桌面")
        self.desktop_check.setChecked(True)
        category_layout.addWidget(self.desktop_check)

        self.download_check = QCheckBox("下载")
        self.download_check.setChecked(True)
        category_layout.addWidget(self.download_check)

        self.document_check = QCheckBox("文档")
        self.document_check.setChecked(True)
        category_layout.addWidget(self.document_check)

        self.favorite_check = QCheckBox("收藏夹")
        self.favorite_check.setChecked(True)
        category_layout.addWidget(self.favorite_check)

        category_layout.addStretch()

        self.scan_user_files_btn = QPushButton("扫描文件")
        self.scan_user_files_btn.clicked.connect(self.scan_user_files)
        category_layout.addWidget(self.scan_user_files_btn)

        files_layout.addLayout(category_layout)

        # 文件统计表格
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels(["类别", "目录", "文件数", "大小"])
        self.backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.backup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.backup_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.backup_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.backup_table.setMaximumHeight(200)
        files_layout.addWidget(self.backup_table)

        files_group.setLayout(files_layout)
        layout.addWidget(files_group, 1)

        # 备份进度
        self.backup_progress = QProgressBar()
        self.backup_progress.setTextVisible(True)
        self.backup_progress.setFormat("等待备份...")
        layout.addWidget(self.backup_progress)

        # 备份按钮
        backup_action_layout = QHBoxLayout()

        self.backup_start_btn = QPushButton("开始备份")
        self.backup_start_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #42A5F5);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1E88E5, stop:1 #42A5F5);
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.backup_start_btn.clicked.connect(self.start_backup)
        backup_action_layout.addWidget(self.backup_start_btn)

        self.backup_stop_btn = QPushButton("停止备份")
        self.backup_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f44336, stop:1 #E57373);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E53935, stop:1 #EF5350);
            }
            QPushButton:pressed {
                background-color: #C62828;
            }
        """)
        self.backup_stop_btn.clicked.connect(self.stop_backup)
        backup_action_layout.addWidget(self.backup_stop_btn)

        layout.addLayout(backup_action_layout)

    def select_backup_dir(self):
        """选择备份目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择备份目录",
            "C:/"
        )

        if directory:
            self.backup_dir = directory
            self.backup_dir_label.setText(directory)

    def scan_user_files(self):
        """扫描用户文件"""
        # 获取用户目录
        user_dirs = self.backup.get_user_dirs()

        if not user_dirs:
            QMessageBox.warning(self, "提示", "无法获取用户目录")
            return

        # 扫描各目录
        self.backup.scan_all()

        # 更新表格
        self.backup_table.setRowCount(len(user_dirs))

        category_names = {
            'desktop': '桌面',
            'download': '下载',
            'document': '文档',
            'favorite': '收藏夹'
        }

        row = 0
        for category, directory in user_dirs.items():
            items = self.backup.get_category_items(category)
            total_size = self.backup.get_category_size(category)

            self.backup_table.setItem(row, 0, QTableWidgetItem(category_names.get(category, category)))
            self.backup_table.setItem(row, 1, QTableWidgetItem(directory))
            self.backup_table.setItem(row, 2, QTableWidgetItem(str(len(items))))
            self.backup_table.setItem(row, 3, QTableWidgetItem(FileBackup.format_size(total_size)))

            row += 1

        # 统计总数
        total_files = len(self.backup.backup_items)
        total_size = sum(item.size for item in self.backup.backup_items)

        QMessageBox.information(
            self,
            "扫描完成",
            f"共扫描到 {total_files} 个文件，总大小: {FileBackup.format_size(total_size)}"
        )

    def start_backup(self):
        """开始备份"""
        if not hasattr(self, 'backup_dir') or not self.backup_dir:
            QMessageBox.warning(self, "提示", "请先选择备份目录")
            return

        # 获取选中的类别
        categories = []
        if self.desktop_check.isChecked():
            categories.append('desktop')
        if self.download_check.isChecked():
            categories.append('download')
        if self.document_check.isChecked():
            categories.append('document')
        if self.favorite_check.isChecked():
            categories.append('favorite')

        if not categories:
            QMessageBox.warning(self, "提示", "请至少选择一个文件类别")
            return

        # 统计文件数
        to_backup = [item for item in self.backup.backup_items if item.category in categories]
        if not to_backup:
            QMessageBox.warning(self, "提示", "没有文件需要备份，请先扫描")
            return

        # 确认备份
        total_size = sum(item.size for item in to_backup)
        reply = QMessageBox.question(
            self,
            "确认备份",
            f"即将备份 {len(to_backup)} 个文件，总大小 {FileBackup.format_size(total_size)}。\n是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 禁用按钮
        self.backup_start_btn.setEnabled(False)
        self.backup_stop_btn.setEnabled(True)
        self.backup_dir_btn.setEnabled(False)
        self.scan_user_files_btn.setEnabled(False)

        # 开始备份
        self.backup_progress.setMaximum(len(to_backup))
        self.backup_progress.setValue(0)

        self.backup_thread = BackupThread(self.backup, self.backup_dir, categories)
        self.backup_thread.progress_signal.connect(self.on_backup_progress)
        self.backup_thread.finished_signal.connect(self.on_backup_finished)
        self.backup_thread.start()

    def on_backup_progress(self, current, total, filename):
        """备份进度"""
        self.backup_progress.setValue(current)
        self.backup_progress.setFormat(f"正在备份: {filename}")

    def on_backup_finished(self, result):
        """备份完成"""
        # 启用按钮
        self.backup_start_btn.setEnabled(True)
        self.backup_stop_btn.setEnabled(False)
        self.backup_dir_btn.setEnabled(True)
        self.scan_user_files_btn.setEnabled(True)

        self.backup_progress.setFormat("备份完成")

        # 提示完成
        QMessageBox.information(
            self,
            "备份完成",
            f"备份完成！\n成功: {result['success']}\n失败: {result['failed']}\n跳过: {result['skipped']}"
        )

    def stop_backup(self):
        """停止备份"""
        if hasattr(self, 'backup_thread'):
            self.backup_thread.stop()


class BackupThread(QThread):
    """备份线程"""
    progress_signal = pyqtSignal(int, int, str)
    finished_signal = pyqtSignal(dict)

    def __init__(self, backup: FileBackup, backup_dir: str, categories: list):
        super().__init__()
        self.backup = backup
        self.backup_dir = backup_dir
        self.categories = categories
        self._stopped = False

    def stop(self):
        self._stopped = True

    def run(self):
        if self._stopped:
            self.finished_signal.emit({'success': 0, 'failed': 0, 'skipped': 0})
            return

        result = self.backup.backup(
            self.backup_dir,
            self.categories,
            self._on_progress
        )
        self.finished_signal.emit(result)

    def _on_progress(self, current, total, filename):
        if not self._stopped:
            self.progress_signal.emit(current, total, filename)
