from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTabWidget, QTextEdit, QPushButton, 
                             QLabel, QFileDialog, QStatusBar, QMenuBar, QAction,
                             QMessageBox, QProgressBar, QGroupBox, QFormLayout,
                             QLineEdit, QSpinBox, QComboBox, QDialog, QToolBar,
                             QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QTextCursor
import sys
import os
from editor import EditorPanel
from ai_analyzer import MCNP6AIAnalyzer
from mcnp6_runner import MCNP6Runner
from config import Config
from settings_dialog import AISettingsDialog, MCNP6SettingsDialog

class AIOutputPanel(QWidget):
    apply_suggestion = pyqtSignal()
    jump_to_line = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = None
        self.current_errors = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #2D2D30; border-bottom: 1px solid #3E3E42;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        self.jump_to_line_btn = QPushButton("跳转到行")
        self.jump_to_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
            QPushButton:disabled {
                background-color: #3E3E42;
                color: #858585;
            }
        """)
        self.jump_to_line_btn.setEnabled(False)
        self.jump_to_line_btn.clicked.connect(self.on_jump_to_line)
        toolbar_layout.addWidget(self.jump_to_line_btn)
        
        self.apply_suggestion_btn = QPushButton("应用建议")
        self.apply_suggestion_btn.setStyleSheet("""
            QPushButton {
                background-color: #107C10;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1E9E1E;
            }
            QPushButton:disabled {
                background-color: #3E3E42;
                color: #858585;
            }
        """)
        self.apply_suggestion_btn.setEnabled(False)
        self.apply_suggestion_btn.clicked.connect(self.on_apply_suggestion)
        toolbar_layout.addWidget(self.apply_suggestion_btn)
        
        toolbar_layout.addStretch()
        
        self.clear_btn = QPushButton("清除")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #C53030;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #D54040;
            }
        """)
        self.clear_btn.clicked.connect(self.on_clear)
        toolbar_layout.addWidget(self.clear_btn)
        
        layout.addWidget(toolbar)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                padding: 10px;
                font-family: Consolas, monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.text_edit)
    
    def set_content(self, content):
        self.text_edit.setPlainText(content)
    
    def clear(self):
        self.text_edit.clear()
    
    def set_mode(self, mode):
        self.current_mode = mode
        if mode == 'diagnose':
            self.apply_suggestion_btn.setEnabled(False)
        elif mode in ['optimize', 'complete']:
            self.apply_suggestion_btn.setEnabled(True)
    
    def set_errors(self, errors):
        self.current_errors = errors
        self.jump_to_line_btn.setEnabled(len(errors) > 0)
    
    def on_jump_to_line(self):
        if self.current_errors:
            line_num = self.current_errors[0].get('line', 0)
            if line_num > 0:
                self.jump_to_line.emit(line_num)
    
    def on_apply_suggestion(self):
        self.apply_suggestion.emit()
    
    def on_clear(self):
        self.clear()
        self.jump_to_line_btn.setEnabled(False)
        self.apply_suggestion_btn.setEnabled(False)
        self.current_errors = []
        self.current_mode = None

class MCNP6Thread(QThread):
    output_received = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, runner, input_file):
        super().__init__()
        self.runner = runner
        self.input_file = input_file
    
    def run(self):
        try:
            def callback(line):
                self.output_received.emit(line)
            
            result = self.runner.run_simulation(self.input_file, callback)
            self.finished.emit(result)
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"MCNP6线程运行错误: {str(e)}", exc_info=True)
            result = {
                "success": False,
                "error": f"MCNP6线程运行错误: {str(e)}",
                "stderr": traceback.format_exc()
            }
            self.finished.emit(result)

class AIThread(QThread):
    finished = pyqtSignal(dict)
    
    def __init__(self, analyzer, method, *args):
        super().__init__()
        self.analyzer = analyzer
        self.method = method
        self.args = args
    
    def run(self):
        method = getattr(self.analyzer, self.method)
        result = method(*self.args)
        self.finished.emit(result)

class MCNP6AIWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
        self.ai_analyzer = MCNP6AIAnalyzer()
        self.mcnp6_runner = MCNP6Runner()
        self.current_file = None
        self.output_file_path = None
        
        self.mcnp6_thread = None
        self.ai_thread = None
    
    def setup_ui(self):
        self.setWindowTitle("MCNP6 AI Assistant")
        self.setGeometry(100, 100, 1400, 900)
        
        self.create_menu_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        self.apply_dark_theme()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建(&N)", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        tools_menu = menubar.addMenu("工具(&T)")
        
        analyze_action = QAction("AI分析输入文件(&A)", self)
        analyze_action.setShortcut("F5")
        analyze_action.triggered.connect(self.analyze_input_file)
        tools_menu.addAction(analyze_action)
        
        complete_action = QAction("AI补全输入文件(&C)", self)
        complete_action.triggered.connect(self.complete_input_file)
        tools_menu.addAction(complete_action)
        
        optimize_action = QAction("AI优化建议(&O)", self)
        optimize_action.triggered.connect(self.optimize_input_file)
        tools_menu.addAction(optimize_action)
        
        tools_menu.addSeparator()
        
        diagnose_action = QAction("AI语法诊断(&D)", self)
        diagnose_action.setShortcut("F8")
        diagnose_action.triggered.connect(self.diagnose_syntax)
        tools_menu.addAction(diagnose_action)
        
        tools_menu.addSeparator()
        
        validate_action = QAction("验证输入文件(&V)", self)
        validate_action.triggered.connect(self.validate_input_file)
        tools_menu.addAction(validate_action)
        
        run_menu = menubar.addMenu("运行(&R)")
        
        run_action = QAction("运行MCNP6(&R)", self)
        run_action.setShortcut("F6")
        run_action.triggered.connect(self.run_mcnp6)
        run_menu.addAction(run_action)
        
        # 添加测试cmd窗口的菜单项
        test_cmd_action = QAction("测试CMD窗口(&T)", self)
        test_cmd_action.triggered.connect(self.test_cmd_window)
        run_menu.addAction(test_cmd_action)
        
        stop_action = QAction("停止运行(&S)", self)
        stop_action.setShortcut("F7")
        stop_action.triggered.connect(self.stop_mcnp6)
        run_menu.addAction(stop_action)
        
        settings_menu = menubar.addMenu("设置(&S)")
        
        ai_settings_action = QAction("AI设置(&A)", self)
        ai_settings_action.triggered.connect(self.show_ai_settings)
        settings_menu.addAction(ai_settings_action)
        
        mcnp6_settings_action = QAction("MCNP6设置(&M)", self)
        mcnp6_settings_action.triggered.connect(self.show_mcnp6_settings)
        settings_menu.addAction(mcnp6_settings_action)
        
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        control_group = QGroupBox("控制面板")
        control_layout = QFormLayout(control_group)
        
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("选择MCNP6输入文件...")
        control_layout.addRow("输入文件:", self.input_file_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_input_file)
        control_layout.addRow("", browse_btn)
        
        left_layout.addWidget(control_group)
        
        ai_group = QGroupBox("AI 分析")
        ai_layout = QVBoxLayout(ai_group)
        
        analyze_btn = QPushButton("分析输入文件")
        analyze_btn.clicked.connect(self.analyze_input_file)
        ai_layout.addWidget(analyze_btn)
        
        complete_btn = QPushButton("补全输入文件")
        complete_btn.clicked.connect(self.complete_input_file)
        ai_layout.addWidget(complete_btn)
        
        optimize_btn = QPushButton("优化建议")
        optimize_btn.clicked.connect(self.optimize_input_file)
        ai_layout.addWidget(optimize_btn)
        
        diagnose_btn = QPushButton("语法诊断")
        diagnose_btn.clicked.connect(self.diagnose_syntax)
        ai_layout.addWidget(diagnose_btn)
        
        left_layout.addWidget(ai_group)
        
        run_group = QGroupBox("MCNP6 运行")
        run_layout = QVBoxLayout(run_group)
        
        self.run_btn = QPushButton("运行")
        self.run_btn.clicked.connect(self.run_mcnp6)
        run_layout.addWidget(self.run_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_mcnp6)
        self.stop_btn.setEnabled(False)
        run_layout.addWidget(self.stop_btn)
        
        left_layout.addWidget(run_group)
        
        left_layout.addStretch()
        
        return left_widget
    
    def create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        
        self.editor_panel = EditorPanel()
        self.tab_widget.addTab(self.editor_panel, "编辑器")
        
        self.ai_output_panel = AIOutputPanel()
        self.ai_output_panel.jump_to_line.connect(self.jump_to_editor_line)
        self.ai_output_panel.apply_suggestion.connect(self.apply_ai_suggestion)
        self.tab_widget.addTab(self.ai_output_panel, "AI 分析结果")
        
        self.mcnp6_output = QTextEdit()
        self.mcnp6_output.setReadOnly(True)
        self.tab_widget.addTab(self.mcnp6_output, "MCNP6 输出")
        
        self.output_viewer = QTextEdit()
        self.output_viewer.setReadOnly(True)
        self.tab_widget.addTab(self.output_viewer, "输出文件")
        
        right_layout.addWidget(self.tab_widget)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)
        
        return right_widget
    
    def setup_connections(self):
        self.editor_panel.save_btn.clicked.connect(self.save_file)
    
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QWidget {
                background-color: #2D2D30;
                color: #D4D4D4;
                font-size: 11px;
            }
            QGroupBox {
                border: 1px solid #3E3E42;
                border-radius: 3px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
            QPushButton:pressed {
                background-color: #0D5A8C;
            }
            QPushButton:disabled {
                background-color: #3E3E42;
                color: #7A7A7A;
            }
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                padding: 4px;
                border-radius: 2px;
            }
            QLineEdit:focus {
                border: 1px solid #007ACC;
            }
            QTextEdit {
                background-color: #1E1E1E;
                border: none;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #3E3E42;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #D4D4D4;
                padding: 6px 12px;
                border: 1px solid #3E3E42;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #3E3E42;
            }
            QProgressBar {
                background-color: #3E3E42;
                border: none;
                border-radius: 2px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
            }
            QStatusBar {
                background-color: #007ACC;
                color: white;
            }
            QMenuBar {
                background-color: #2D2D30;
                color: #D4D4D4;
            }
            QMenuBar::item:selected {
                background-color: #3E3E42;
            }
            QMenu {
                background-color: #2D2D30;
                color: #D4D4D4;
                border: 1px solid #3E3E42;
            }
            QMenu::item:selected {
                background-color: #007ACC;
            }
        """)
    
    def new_file(self):
        self.editor_panel.set_content("")
        self.current_file = None
        self.input_file_edit.clear()
        self.status_bar.showMessage("已创建新文件")
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开MCNP6输入文件", "", "MCNP6 Files (*.inp *.txt);;All Files (*)"
        )
        
        if file_path:
            if self.editor_panel.load_file(file_path):
                self.current_file = file_path
                self.input_file_edit.setText(file_path)
                self.status_bar.showMessage(f"已打开: {file_path}")
            else:
                QMessageBox.critical(self, "错误", "无法打开文件")
    
    def save_file(self):
        if self.current_file:
            if self.editor_panel.save_file():
                self.status_bar.showMessage(f"已保存: {self.current_file}")
            else:
                QMessageBox.critical(self, "错误", "无法保存文件")
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存MCNP6输入文件", "", "MCNP6 Files (*.inp);;All Files (*)"
            )
            
            if file_path:
                if self.editor_panel.save_file(file_path):
                    self.current_file = file_path
                    self.input_file_edit.setText(file_path)
                    self.status_bar.showMessage(f"已保存: {file_path}")
                else:
                    QMessageBox.critical(self, "错误", "无法保存文件")
    
    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择MCNP6输入文件", "", "MCNP6 Files (*.inp *.txt);;All Files (*)"
        )
        
        if file_path:
            self.input_file_edit.setText(file_path)
            self.editor_panel.load_file(file_path)
            self.current_file = file_path
    
    def analyze_input_file(self):
        content = self.editor_panel.get_content()
        
        if not content.strip():
            QMessageBox.warning(self, "警告", "请先输入或加载MCNP6输入文件内容")
            return
        
        self.tab_widget.setCurrentIndex(1)
        self.ai_output_panel.clear()
        self.ai_output_panel.set_content("正在分析输入文件，请稍候...")
        self.ai_output_panel.set_mode('analyze')
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.ai_thread = AIThread(self.ai_analyzer, "analyze_input_file", content)
        self.ai_thread.finished.connect(self.on_analyze_finished)
        self.ai_thread.start()
    
    def on_analyze_finished(self, result):
        self.progress_bar.setVisible(False)
        
        if result["success"]:
            self.ai_output_panel.clear()
            self.ai_output_panel.set_content(result["result"])
            self.status_bar.showMessage("AI分析完成")
        else:
            self.ai_output_panel.clear()
            self.ai_output_panel.set_content(f"分析失败: {result.get('error', '未知错误')}")
            QMessageBox.critical(self, "错误", f"AI分析失败: {result.get('error', '未知错误')}")
    
    def complete_input_file(self):
        content = self.editor_panel.get_content()
        
        if not content.strip():
            QMessageBox.warning(self, "警告", "请先输入部分MCNP6输入文件内容")
            return
        
        self.tab_widget.setCurrentIndex(1)
        self.ai_output_panel.clear()
        self.ai_output_panel.set_content("正在补全输入文件，请稍候...")
        self.ai_output_panel.set_mode('complete')
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.ai_thread = AIThread(self.ai_analyzer, "complete_input_file", content)
        self.ai_thread.finished.connect(self.on_complete_finished)
        self.ai_thread.start()
    
    def on_complete_finished(self, result):
        self.progress_bar.setVisible(False)
        
        if result["success"]:
            self.editor_panel.set_content(result["content"])
            self.tab_widget.setCurrentIndex(0)
            self.status_bar.showMessage("输入文件补全完成")
        else:
            self.ai_output_panel.clear()
            self.ai_output_panel.set_content(f"补全失败: {result.get('error', '未知错误')}")
            QMessageBox.critical(self, "错误", f"AI补全失败: {result.get('error', '未知错误')}")
    
    def optimize_input_file(self):
        content = self.editor_panel.get_content()
        
        if not content.strip():
            QMessageBox.warning(self, "警告", "请先输入或加载MCNP6输入文件内容")
            return
        
        self.tab_widget.setCurrentIndex(1)
        self.ai_output_panel.clear()
        self.ai_output_panel.set_content("正在生成优化建议，请稍候...")
        self.ai_output_panel.set_mode('optimize')
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.ai_thread = AIThread(self.ai_analyzer, "optimize_input_file", content)
        self.ai_thread.finished.connect(self.on_optimize_finished)
        self.ai_thread.start()
    
    def on_optimize_finished(self, result):
        self.progress_bar.setVisible(False)
        
        if result["success"]:
            self.ai_output_panel.clear()
            self.ai_output_panel.set_content(result["suggestions"])
            self.status_bar.showMessage("优化建议生成完成")
        else:
            self.ai_output_panel.clear()
            self.ai_output_panel.set_content(f"生成优化建议失败: {result.get('error', '未知错误')}")
            QMessageBox.critical(self, "错误", f"生成优化建议失败: {result.get('error', '未知错误')}")
    
    def diagnose_syntax(self):
        content = self.editor_panel.get_content()
        
        if not content.strip():
            QMessageBox.warning(self, "警告", "请先输入或加载MCNP6输入文件内容")
            return
        
        self.editor_panel.clear_marks()
        
        self.tab_widget.setCurrentIndex(1)
        self.ai_output_panel.clear()
        self.ai_output_panel.set_content("正在进行AI语法诊断，请稍候...")
        self.ai_output_panel.set_mode('diagnose')
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.ai_thread = AIThread(self.ai_analyzer, "diagnose_syntax", content)
        self.ai_thread.finished.connect(self.on_diagnose_finished)
        self.ai_thread.start()
    
    def on_diagnose_finished(self, result):
        self.progress_bar.setVisible(False)
        
        if result["success"]:
            diagnosis = result.get("diagnosis", {})
            
            self.ai_output_panel.clear()
            
            summary = diagnosis.get("summary", "诊断完成")
            output_text = f"=== 诊断总结 ===\n{summary}\n"
            
            errors = diagnosis.get("errors", [])
            warnings = diagnosis.get("warnings", [])
            
            if errors:
                output_text += f"\n=== 发现 {len(errors)} 个错误 ===\n"
                for i, error in enumerate(errors, 1):
                    output_text += f"\n错误 {i}:\n"
                    output_text += f"  行号: {error.get('line', '未知')}\n"
                    output_text += f"  类型: {error.get('type', '未知')}\n"
                    output_text += f"  描述: {error.get('message', '无')}\n"
                    output_text += f"  建议: {error.get('suggestion', '无')}\n"
                
                self.editor_panel.mark_errors(errors)
                self.ai_output_panel.set_errors(errors)
            else:
                output_text += "\n✓ 未发现语法错误"
            
            if warnings:
                output_text += f"\n=== 发现 {len(warnings)} 个警告 ===\n"
                for i, warning in enumerate(warnings, 1):
                    output_text += f"\n警告 {i}:\n"
                    output_text += f"  行号: {warning.get('line', '未知')}\n"
                    output_text += f"  类型: {warning.get('type', '未知')}\n"
                    output_text += f"  描述: {warning.get('message', '无')}\n"
                
                self.editor_panel.mark_warnings(warnings)
            
            self.ai_output_panel.set_content(output_text)
            self.status_bar.showMessage(f"AI诊断完成: {len(errors)} 个错误, {len(warnings)} 个警告")
            
            if errors:
                QMessageBox.warning(
                    self, 
                    "诊断结果", 
                    f"发现 {len(errors)} 个语法错误和 {len(warnings)} 个警告。\n\n错误已在编辑器中高亮显示（红色背景）。\n警告已在编辑器中标记（黄色背景）。\n\n请查看AI分析结果标签页获取详细信息。"
                )
            elif warnings:
                QMessageBox.information(
                    self, 
                    "诊断结果", 
                    f"未发现语法错误，但有 {len(warnings)} 个警告。\n\n警告已在编辑器中标记（黄色背景）。\n\n请查看AI分析结果标签页获取详细信息。"
                )
            else:
                QMessageBox.information(
                    self, 
                    "诊断结果", 
                    "未发现语法错误或警告。\n\n输入文件语法正确！"
                )
        else:
            self.ai_output_panel.clear()
            self.ai_output_panel.set_content(f"诊断失败: {result.get('error', '未知错误')}")
            QMessageBox.critical(self, "错误", f"AI诊断失败: {result.get('error', '未知错误')}")
    
    def jump_to_editor_line(self, line_num):
        self.tab_widget.setCurrentIndex(0)
        editor = self.editor_panel.get_editor()
        document = editor.document()
        block = document.findBlockByNumber(line_num - 1)
        
        if block.isValid():
            cursor = QTextCursor(block)
            editor.setTextCursor(cursor)
            editor.setFocus()
            self.status_bar.showMessage(f"已跳转到第 {line_num} 行")
    
    def apply_ai_suggestion(self):
        if self.ai_output_panel.current_mode == 'complete':
            content = self.ai_output_panel.text_edit.toPlainText()
            if content.strip():
                self.editor_panel.set_content(content)
                self.tab_widget.setCurrentIndex(0)
                self.status_bar.showMessage("已应用AI补全建议")
                QMessageBox.information(self, "成功", "已应用AI补全建议到编辑器！")
        elif self.ai_output_panel.current_mode == 'optimize':
            content = self.ai_output_panel.text_edit.toPlainText()
            if content.strip():
                reply = QMessageBox.question(
                    self,
                    "应用优化建议",
                    "优化建议包含详细的分析和改进建议。\n\n是否要将优化建议追加到编辑器？\n\n点击'是'追加到编辑器末尾\n点击'否'仅在AI分析结果中查看",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    current_content = self.editor_panel.get_content()
                    new_content = current_content + "\n\n" + "="*50 + "\nAI优化建议\n" + "="*50 + "\n\n" + content
                    self.editor_panel.set_content(new_content)
                    self.tab_widget.setCurrentIndex(0)
                    self.status_bar.showMessage("已应用AI优化建议")
                    QMessageBox.information(self, "成功", "已将AI优化建议追加到编辑器！")
    
    def validate_input_file(self):
        if not self.current_file:
            QMessageBox.warning(self, "警告", "请先打开或保存输入文件")
            return
        
        result = self.mcnp6_runner.validate_input_file(self.current_file)
        
        message = []
        if result["valid"]:
            message.append("输入文件验证通过！")
        else:
            message.append("输入文件验证失败：")
            for error in result["errors"]:
                message.append(f"  错误: {error}")
        
        if result["warnings"]:
            message.append("\n警告：")
            for warning in result["warnings"]:
                message.append(f"  {warning}")
        
        QMessageBox.information(self, "验证结果", "\n".join(message))
    
    def run_mcnp6(self):
        input_file = self.input_file_edit.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "警告", "请先选择有效的MCNP6输入文件")
            return
        
        if not self.current_file:
            self.save_file()
        
        self.tab_widget.setCurrentIndex(2)
        self.mcnp6_output.clear()
        self.mcnp6_output.append("正在启动MCNP6...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.mcnp6_thread = MCNP6Thread(self.mcnp6_runner, input_file)
        self.mcnp6_thread.output_received.connect(self.on_mcnp6_output)
        self.mcnp6_thread.finished.connect(self.on_mcnp6_finished)
        self.mcnp6_thread.start()
        
        self.status_bar.showMessage("MCNP6正在运行...")
    
    def on_mcnp6_output(self, line):
        self.mcnp6_output.append(line.rstrip())
    
    def on_mcnp6_finished(self, result):
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if result["success"]:
            self.mcnp6_output.append("\n运行完成！")
            self.status_bar.showMessage("MCNP6运行完成")
            
            if result.get("output_file"):
                self.output_file_path = result["output_file"]
                self.mcnp6_output.append(f"\n输出文件已生成: {self.output_file_path}")
                
                # 询问用户是否查看输出文件
                reply = QMessageBox.question(
                    self, 
                    "查看输出文件", 
                    "是否要在界面上显示输出文件内容？",
                    QMessageBox.Yes | QMessageBox.No, 
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.load_output_file(self.output_file_path)
        else:
            self.mcnp6_output.append(f"\n运行失败: {result.get('error', '未知错误')}")
            if result.get("stderr"):
                self.mcnp6_output.append(f"\n错误输出:\n{result['stderr']}")
            self.status_bar.showMessage("MCNP6运行失败")
            QMessageBox.critical(self, "错误", f"MCNP6运行失败: {result.get('error', '未知错误')}")
    
    def stop_mcnp6(self):
        if self.mcnp6_runner.is_running():
            result = self.mcnp6_runner.stop_simulation()
            if result["success"]:
                self.mcnp6_output.append("\n模拟已停止")
                self.status_bar.showMessage("模拟已停止")
            else:
                QMessageBox.critical(self, "错误", result.get("error", "停止失败"))
    
    def test_cmd_window(self):
        """测试仅打开cmd窗口"""
        try:
            import subprocess
            import os
            
            # 修复路径格式：使用双反斜杠或原始字符串
            cmd_path = r"C:\Windows\System32\cmd.exe"
            working_dir = r"E:\MCNP"
            
            # 使用shell=True直接执行cmd命令
            subprocess.Popen(
                cmd_path, 
                cwd=working_dir, 
                shell=True
            )
            
            self.status_bar.showMessage("已打开测试CMD窗口")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开CMD窗口: {str(e)}")
    
    def load_output_file(self, output_file):
        try:
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self.output_viewer.setPlainText(content)
            self.tab_widget.setCurrentIndex(3)
            self.status_bar.showMessage(f"已加载输出文件: {output_file}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载输出文件: {str(e)}")
    
    def show_ai_settings(self):
        dialog = AISettingsDialog(self)
        dialog.exec_()
        
        if dialog.result() == QDialog.Accepted:
            self.ai_analyzer = MCNP6AIAnalyzer()
            self.status_bar.showMessage("AI设置已更新")
    
    def show_mcnp6_settings(self):
        dialog = MCNP6SettingsDialog(self)
        dialog.exec_()
        
        if dialog.result() == QDialog.Accepted:
            self.mcnp6_runner = MCNP6Runner()
            self.status_bar.showMessage("MCNP6设置已更新")
    
    def show_about(self):
        QMessageBox.about(
            self, 
            "关于 MCNP6 AI Assistant",
            "MCNP6 AI Assistant\n\n"
            "一个整合AI和MCNP6的Windows桌面应用\n"
            "用于分析、诊断和补全MCNP6输入文件\n\n"
            "版本: 1.0.0\n"
            "开发者: 核工程与核技术专业-杨寒(邮箱yhyanghan22@163.com)"
        )