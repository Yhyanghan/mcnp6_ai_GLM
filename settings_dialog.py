from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, 
                             QPushButton, QGroupBox, QRadioButton, QButtonGroup,
                             QLabel, QFileDialog, QMessageBox, QTabWidget, QWidget)
from PyQt5.QtCore import Qt
import os
import sys
import logging
from pathlib import Path
from config import Config

def get_app_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent

def get_env_file_path():
    return get_app_path() / '.env'

logger = logging.getLogger(__name__)

class AISettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI设置")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        mode_group = QGroupBox("AI模式")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_group = QButtonGroup(self)
        
        self.online_radio = QRadioButton("在线API (Online API)")
        self.local_radio = QRadioButton("本地AI (Local AI)")
        
        self.mode_group.addButton(self.online_radio, 0)
        self.mode_group.addButton(self.local_radio, 1)
        
        self.online_radio.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.online_radio)
        mode_layout.addWidget(self.local_radio)
        
        layout.addWidget(mode_group)
        
        self.tab_widget = QTabWidget()
        
        self.online_tab = QWidget()
        self.setup_online_tab()
        self.tab_widget.addTab(self.online_tab, "在线API")
        
        self.local_tab = QWidget()
        self.setup_local_tab()
        self.tab_widget.addTab(self.local_tab, "本地AI")
        
        layout.addWidget(self.tab_widget)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_btn)
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def setup_online_tab(self):
        layout = QFormLayout(self.online_tab)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("输入API密钥")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("API密钥:", self.api_key_edit)
        
        self.api_base_edit = QLineEdit()
        self.api_base_edit.setPlaceholderText("https://api.openai.com/v1")
        layout.addRow("API地址:", self.api_base_edit)
        
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("gpt-4")
        layout.addRow("模型:", self.model_edit)
        
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)
        layout.addRow("温度:", self.temperature_spin)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 10000)
        self.max_tokens_spin.setValue(2000)
        layout.addRow("最大令牌数:", self.max_tokens_spin)
    
    def setup_local_tab(self):
        layout = QFormLayout(self.local_tab)
        
        self.local_endpoint_edit = QLineEdit()
        self.local_endpoint_edit.setPlaceholderText("http://localhost:11434/api/generate")
        layout.addRow("本地端点:", self.local_endpoint_edit)
        
        self.local_model_edit = QLineEdit()
        self.local_model_edit.setPlaceholderText("llama2")
        layout.addRow("本地模型:", self.local_model_edit)
        
        self.local_temperature_spin = QDoubleSpinBox()
        self.local_temperature_spin.setRange(0.0, 2.0)
        self.local_temperature_spin.setSingleStep(0.1)
        self.local_temperature_spin.setValue(0.7)
        layout.addRow("温度:", self.local_temperature_spin)
        
        self.local_max_tokens_spin = QSpinBox()
        self.local_max_tokens_spin.setRange(100, 10000)
        self.local_max_tokens_spin.setValue(2000)
        layout.addRow("最大令牌数:", self.local_max_tokens_spin)
        
        hint_label = QLabel("提示: 本地AI需要先启动本地AI服务（如Ollama）")
        hint_label.setStyleSheet("color: #888888; font-style: italic;")
        layout.addRow(hint_label)
    
    def load_settings(self):
        mode = Config.AI_MODE
        if mode == 'online':
            self.online_radio.setChecked(True)
        else:
            self.local_radio.setChecked(True)
        
        self.api_key_edit.setText(Config.AI_API_KEY)
        self.api_base_edit.setText(Config.AI_API_BASE)
        self.model_edit.setText(Config.AI_MODEL)
        self.temperature_spin.setValue(Config.AI_TEMPERATURE)
        self.max_tokens_spin.setValue(Config.AI_MAX_TOKENS)
        
        self.local_endpoint_edit.setText(Config.AI_LOCAL_ENDPOINT)
        self.local_model_edit.setText(Config.AI_LOCAL_MODEL)
        self.local_temperature_spin.setValue(Config.AI_TEMPERATURE)
        self.local_max_tokens_spin.setValue(Config.AI_MAX_TOKENS)
    
    def on_mode_changed(self):
        if self.online_radio.isChecked():
            self.tab_widget.setCurrentIndex(0)
        else:
            self.tab_widget.setCurrentIndex(1)
    
    def test_connection(self):
        from ai_analyzer import MCNP6AIAnalyzer
        
        try:
            mode = 'online' if self.online_radio.isChecked() else 'local'
            
            if mode == 'online':
                api_key = self.api_key_edit.text().strip()
                if not api_key:
                    QMessageBox.warning(self, "警告", "请输入API密钥")
                    return
                
                Config.AI_API_KEY = api_key
                Config.AI_API_BASE = self.api_base_edit.text().strip()
                Config.AI_MODEL = self.model_edit.text().strip()
            else:
                Config.AI_LOCAL_ENDPOINT = self.local_endpoint_edit.text().strip()
                Config.AI_LOCAL_MODEL = self.local_model_edit.text().strip()
            
            Config.AI_MODE = mode
            Config.AI_TEMPERATURE = self.temperature_spin.value()
            Config.AI_MAX_TOKENS = self.max_tokens_spin.value()
            
            analyzer = MCNP6AIAnalyzer()
            result = analyzer.analyze_input_file("c test\n1 1 -1.0 -1 imp:p=1\n2 0 1 imp:p=0\n1 so 10\nm1 1001 1.0\nsdef pos=0 erg=1")
            
            if result.get("success"):
                QMessageBox.information(self, "成功", "AI连接测试成功！")
            else:
                QMessageBox.warning(self, "失败", f"AI连接测试失败：{result.get('error', '未知错误')}")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"测试连接时发生错误：{str(e)}")
    
    def save_settings(self):
        try:
            mode = 'online' if self.online_radio.isChecked() else 'local'
            
            env_content = ""
            
            with open(str(get_env_file_path()), 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            skip_next = False
            
            for i, line in enumerate(lines):
                if skip_next:
                    skip_next = False
                    continue
                
                stripped = line.strip()
                
                if stripped.startswith('AI_MODE='):
                    new_lines.append(f'AI_MODE={mode}\n')
                elif stripped.startswith('AI_API_KEY='):
                    new_lines.append(f'AI_API_KEY={self.api_key_edit.text().strip()}\n')
                elif stripped.startswith('AI_API_BASE='):
                    new_lines.append(f'AI_API_BASE={self.api_base_edit.text().strip()}\n')
                elif stripped.startswith('AI_MODEL='):
                    new_lines.append(f'AI_MODEL={self.model_edit.text().strip()}\n')
                elif stripped.startswith('AI_TEMPERATURE='):
                    new_lines.append(f'AI_TEMPERATURE={self.temperature_spin.value()}\n')
                elif stripped.startswith('AI_MAX_TOKENS='):
                    new_lines.append(f'AI_MAX_TOKENS={self.max_tokens_spin.value()}\n')
                elif stripped.startswith('AI_LOCAL_ENDPOINT='):
                    new_lines.append(f'AI_LOCAL_ENDPOINT={self.local_endpoint_edit.text().strip()}\n')
                elif stripped.startswith('AI_LOCAL_MODEL='):
                    new_lines.append(f'AI_LOCAL_MODEL={self.local_model_edit.text().strip()}\n')
                else:
                    new_lines.append(line)
            
            with open(str(get_env_file_path()), 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            from dotenv import load_dotenv
            from config import Config
            load_dotenv(override=True)
            
            Config.reload()
            
            QMessageBox.information(self, "成功", "AI设置已保存！")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置时发生错误：{str(e)}")

class MCNP6SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MCNP6设置")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        execution_group = QGroupBox("MCNP6执行方式")
        execution_layout = QFormLayout(execution_group)
        
        self.mcnp6_path_edit = QLineEdit()
        self.mcnp6_path_edit.setPlaceholderText("C:/Windows/System32/cmd.exe 或 C:/MCNP6/mcnp6.exe")
        execution_layout.addRow("MCNP6执行路径:", self.mcnp6_path_edit)
        
        browse_path_btn = QPushButton("浏览...")
        browse_path_btn.clicked.connect(self.browse_mcnp6_path)
        execution_layout.addRow("", browse_path_btn)
        
        self.mcnp6_cmd_edit = QLineEdit()
        self.mcnp6_cmd_edit.setPlaceholderText("C:/MCNP6/mcnp6.exe (仅当使用cmd.exe时需要)")
        execution_layout.addRow("MCNP6可执行文件", self.mcnp6_cmd_edit)
        
        browse_cmd_btn = QPushButton("浏览...")
        browse_cmd_btn.clicked.connect(self.browse_mcnp6_cmd)
        execution_layout.addRow("", browse_cmd_btn)
        
        self.mcnp6_env_bat_edit = QLineEdit()
        self.mcnp6_env_bat_edit.setPlaceholderText("C:/Users/Username/mcnp_env.bat")
        execution_layout.addRow("环境批处理文件", self.mcnp6_env_bat_edit)
        
        browse_env_btn = QPushButton("浏览...")
        browse_env_btn.clicked.connect(self.browse_mcnp6_env_bat)
        execution_layout.addRow("", browse_env_btn)
        
        layout.addWidget(execution_group)
        
        workspace_group = QGroupBox("工作目录")
        workspace_layout = QFormLayout(workspace_group)
        
        self.workspace_edit = QLineEdit()
        self.workspace_edit.setPlaceholderText("C:/MCNP6/workspace")
        workspace_layout.addRow("工作目录:", self.workspace_edit)
        
        browse_workspace_btn = QPushButton("浏览...")
        browse_workspace_btn.clicked.connect(self.browse_workspace)
        workspace_layout.addRow("", browse_workspace_btn)
        
        layout.addWidget(workspace_group)
        
        hint_label = QLabel("提示:\n- 如果MCNP6直接执行: MCNP6执行路径设置为mcnp6.exe，MCNP6可执行文件留空\n- 如果MCNP6通过cmd.exe执行: MCNP6执行路径设置为cmd.exe，MCNP6可执行文件设置为mcnp6.exe\n- 工作目录用于存放输出文件和临时文件")
        hint_label.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(hint_label)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.test_btn = QPushButton("测试MCNP6")
        self.test_btn.clicked.connect(self.test_mcnp6)
        button_layout.addWidget(self.test_btn)
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        self.mcnp6_path_edit.setText(Config.MCNP6_PATH)
        mcnp6_cmd = Config.MCNP6_CMD if hasattr(Config, 'MCNP6_CMD') else ''
        self.mcnp6_cmd_edit.setText(mcnp6_cmd)
        mcnp6_env_bat = Config.MCNP6_ENV_BAT if hasattr(Config, 'MCNP6_ENV_BAT') else ''
        self.mcnp6_env_bat_edit.setText(mcnp6_env_bat)
        self.workspace_edit.setText(Config.MCNP6_WORKSPACE)
    
    def browse_mcnp6_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择MCNP6执行路径", "", "可执行文件(*.exe);;所有文件(*)"
        )
        
        if file_path:
            self.mcnp6_path_edit.setText(file_path)
    
    def browse_mcnp6_cmd(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择MCNP6可执行文件", "", "可执行文件(*.exe);;所有文件(*)"
        )
        
        if file_path:
            self.mcnp6_cmd_edit.setText(file_path)
    
    def browse_workspace(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择工作目录"
        )
        
        if dir_path:
            self.workspace_edit.setText(dir_path)
    
    def browse_mcnp6_env_bat(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择环境批处理文件", "", "批处理文件(*.bat);;所有文件(*)"
        )
        
        if file_path:
            self.mcnp6_env_bat_edit.setText(file_path)
    
    def test_mcnp6(self):
        import os
        import subprocess
        import tempfile
        from pathlib import Path
        
        mcnp6_path = self.mcnp6_path_edit.text().strip()
        mcnp6_cmd = self.mcnp6_cmd_edit.text().strip()
        
        if not mcnp6_path:
            QMessageBox.warning(self, "警告", "请输入MCNP6执行路径")
            return
        
        if not os.path.exists(mcnp6_path):
            QMessageBox.warning(self, "警告", f"文件不存在: {mcnp6_path}")
            return
        
        if 'cmd.exe' in mcnp6_path.lower() and not mcnp6_cmd:
            QMessageBox.warning(self, "警告", "使用cmd.exe执行方式时，必须设置MCNP6可执行文件")
            return
        
        if mcnp6_cmd and not os.path.exists(mcnp6_cmd):
            QMessageBox.warning(self, "警告", f"MCNP6可执行文件不存在: {mcnp6_cmd}")
            return
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                test_input = os.path.join(temp_dir, "test.inp")
                test_output = os.path.join(temp_dir, "test.out")
                test_runtpe = os.path.join(temp_dir, "test.r")
                
                with open(test_input, 'w', encoding='utf-8') as f:
                    f.write("c Test input file\n")
                    f.write("1 1 -1.0 -1 imp:p=1\n")
                    f.write("2 0 1 imp:p=0\n")
                    f.write("1 so 10\n")
                    f.write("m1 1001 1.0\n")
                    f.write("sdef pos=0 erg=1\n")
                    f.write("nps 10\n")
                
                test_cmd = []
                env = os.environ.copy()
                
                if 'cmd.exe' in mcnp6_path.lower():
                    mcnp6_dir = str(Path(mcnp6_cmd).parent)
                    env['MCNPPATH'] = mcnp6_dir
                    env['PATH'] = mcnp6_dir + os.pathsep + env['PATH']
                    
                    datapath = str(Path(mcnp6_dir).parent.parent.joinpath("MCNP_DATA"))
                    if os.path.exists(datapath):
                        env['DATAPATH'] = datapath
                    
                    env['DISPLAY'] = ':0.0'
                    
                    command_line = f'{mcnp6_cmd} i="{test_input}" o="{test_output}" r="{test_runtpe}"'
                    test_cmd = [mcnp6_path, '/c', command_line]
                    logger.info(f"测试命令: {mcnp6_path} /c {command_line}")
                else:
                    test_cmd = [mcnp6_path, f"i={test_input}", f"o={test_output}", f"r={test_runtpe}"]
                    logger.info(f"测试命令: {' '.join(test_cmd)}")
                
                logger.info(f"工作目录: {temp_dir}")
                logger.info(f"MCNPPATH: {env.get('MCNPPATH')}")
                logger.info(f"DATAPATH: {env.get('DATAPATH')}")
                
                try:
                    result = subprocess.run(
                        test_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=temp_dir,
                        env=env,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    
                    logger.info(f"返回码: {result.returncode}")
                    logger.info(f"标准输出长度: {len(result.stdout)}")
                    logger.info(f"标准输出前500字符: {result.stdout[:500]}")
                    if result.stderr:
                        logger.info(f"标准错误长度: {len(result.stderr)}")
                        logger.info(f"标准错误前500字符: {result.stderr[:500]}")
                    
                    if result.returncode == 0:
                        QMessageBox.information(self, "成功", "MCNP6测试成功！\n\nMCNP6能够正常运行！")
                    else:
                        error_msg = result.stderr if result.stderr else result.stdout
                        if "bad trouble" in error_msg.lower() or "fatal" in error_msg.lower():
                            QMessageBox.warning(self, "警告", f"MCNP6运行时发生错误：\n{error_msg[:500]}")
                        else:
                            QMessageBox.information(self, "成功", "MCNP6测试成功！\n\nMCNP6能够正常运行！")
                
                except subprocess.TimeoutExpired:
                    logger.error("MCNP6测试超时")
                    QMessageBox.warning(self, "警告", "MCNP6测试超时（60秒）")
                
        except Exception as e:
            import traceback
            logger.error(f"测试MCNP6时发生错误: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "错误", f"测试MCNP6时发生错误：{str(e)}")
    
    def save_settings(self):
        try:
            mcnp6_path = self.mcnp6_path_edit.text().strip()
            mcnp6_cmd = self.mcnp6_cmd_edit.text().strip()
            mcnp6_env_bat = self.mcnp6_env_bat_edit.text().strip()
            workspace = self.workspace_edit.text().strip()
            
            if not mcnp6_path:
                QMessageBox.warning(self, "警告", "请输入MCNP6执行路径")
                return
            
            with open(str(get_env_file_path()), 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            env_bat_line_exists = False
            
            for line in lines:
                stripped = line.strip()
                
                if stripped.startswith('MCNP6_PATH='):
                    new_lines.append(f'MCNP6_PATH={mcnp6_path}\n')
                elif stripped.startswith('MCNP6_CMD='):
                    new_lines.append(f'MCNP6_CMD={mcnp6_cmd}\n')
                elif stripped.startswith('MCNP6_ENV_BAT='):
                    new_lines.append(f'MCNP6_ENV_BAT={mcnp6_env_bat}\n')
                    env_bat_line_exists = True
                elif stripped.startswith('MCNP6_WORKSPACE='):
                    new_lines.append(f'MCNP6_WORKSPACE={workspace}\n')
                else:
                    new_lines.append(line)
            
            # 如果.env文件中没有MCNP6_ENV_BAT行，则添加它
            if not env_bat_line_exists:
                new_lines.append(f'MCNP6_ENV_BAT={mcnp6_env_bat}\n')
            
            with open(str(get_env_file_path()), 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            from dotenv import load_dotenv
            from config import Config
            load_dotenv(override=True)
            
            Config.reload()
            
            os.makedirs(workspace, exist_ok=True)
            
            QMessageBox.information(self, "成功", "MCNP6设置已保存！")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置时发生错误：{str(e)}")
