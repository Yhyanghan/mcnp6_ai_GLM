from PyQt5.QtWidgets import (QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QLabel, QPushButton, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QSize
from PyQt5.QtGui import (QFont, QTextCharFormat, QColor, QSyntaxHighlighter, 
                         QTextDocument, QTextCursor, QTextBlockFormat, QPainter)
import re

class MCNP6SyntaxHighlighter(QSyntaxHighlighter):
    """MCNP6语法高亮器，支持更精确的卡片类型识别"""
    
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        self._setup_rules()
    
    def _setup_rules(self):
        # 注释格式 (c 开头的行或 $ 后的内容)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'^[cC]\s+.*$', re.MULTILINE), comment_format))
        self.highlighting_rules.append((re.compile(r'\$.*$'), comment_format))
        
        # 材料卡片 (m1, M2, mt1等)
        material_format = QTextCharFormat()
        material_format.setForeground(QColor("#C586C0"))
        material_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'^\s*[mM][tT]?\d+', re.MULTILINE), material_format))
        
        # 计数卡片 (f4:n, F5:p, *f8:p,e等)
        tally_format = QTextCharFormat()
        tally_format.setForeground(QColor("#DCDCAA"))
        tally_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'^\s*\*?[fF][cCmMsStTeE]?\d+:?[npehNPEH,]*', re.MULTILINE), tally_format))
        
        # 表面卡片 (数字开头，表面类型如 so, px, cy, rpp等)
        surface_format = QTextCharFormat()
        surface_format.setForeground(QColor("#4EC9B0"))
        surface_types = r'\b(so|sx|sy|sz|s|px|py|pz|p|cx|cy|cz|c\/x|c\/y|c\/z|kx|ky|kz|k\/x|k\/y|k\/z|sq|gq|tx|ty|tz|box|rpp|sph|rcc|rhp|hex|rec|trc|ell|wed|arb)\b'
        self.highlighting_rules.append((re.compile(surface_types, re.IGNORECASE), surface_format))
        
        # 源定义关键字 (sdef及其参数)
        source_format = QTextCharFormat()
        source_format.setForeground(QColor("#569CD6"))
        source_format.setFontWeight(QFont.Bold)
        source_keywords = r'\b(sdef|pos|erg|dir|vec|par|cel|sur|rad|ext|axs|ara|wgt|eff|tme)\b'
        self.highlighting_rules.append((re.compile(source_keywords, re.IGNORECASE), source_format))
        
        # 重要数据卡关键字
        datacard_format = QTextCharFormat()
        datacard_format.setForeground(QColor("#CE9178"))
        datacard_format.setFontWeight(QFont.Bold)
        data_keywords = r'\b(nps|ctme|prdmp|print|mode|imp|vol|area|tr|fill|like|but|lat|u|trcl|phys|cut|elpt|tmp|act|fmesh|tmesh|wwg|wwe|wwn|wwp|ext|vect|fcl|pd|dxt|dd|df|dm|de|em|sf|sb|sp|si|sc|ds|fq|fm|fs|sd|fu|ft|tf|cf|cm|e|t|c)\b'
        self.highlighting_rules.append((re.compile(data_keywords, re.IGNORECASE), datacard_format))
        
        # 数值格式 (整数、浮点数、科学计数法)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((re.compile(r'[+-]?\d+\.?\d*[eE]?[+-]?\d*'), number_format))
        
        # 粒子类型
        particle_format = QTextCharFormat()
        particle_format.setForeground(QColor("#9CDCFE"))
        self.highlighting_rules.append((re.compile(r'\b(n|p|e|h|\|)\b'), particle_format))
    
    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

class MCNP6Editor(QPlainTextEdit):
    content_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_editor()
        self.error_lines = set()
    
    def setup_editor(self):
        font = QFont("Consolas", 11)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                padding: 5px;
            }
        """)
        
        self.highlighter = MCNP6SyntaxHighlighter(self.document())
        self.textChanged.connect(self.content_changed.emit)
        
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
    
    def mark_error_lines(self, errors):
        self.clear_error_marks()
        
        document = self.document()
        cursor = QTextCursor(document)
        
        for error in errors:
            line_num = error.get('line', 0)
            if line_num > 0:
                block = document.findBlockByNumber(line_num - 1)
                if block.isValid():
                    block_format = QTextBlockFormat()
                    block_format.setBackground(QColor("#5A1D1D"))
                    cursor.setPosition(block.position())
                    cursor.movePosition(QTextCursor.StartOfBlock)
                    cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                    cursor.setBlockFormat(block_format)
                    self.error_lines.add(line_num)
        
        self.viewport().update()
    
    def mark_warning_lines(self, warnings):
        document = self.document()
        cursor = QTextCursor(document)
        
        for warning in warnings:
            line_num = warning.get('line', 0)
            if line_num > 0 and line_num not in self.error_lines:
                block = document.findBlockByNumber(line_num - 1)
                if block.isValid():
                    block_format = QTextBlockFormat()
                    block_format.setBackground(QColor("#4A3D00"))
                    cursor.setPosition(block.position())
                    cursor.movePosition(QTextCursor.StartOfBlock)
                    cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                    cursor.setBlockFormat(block_format)
        
        self.viewport().update()
    
    def clear_error_marks(self):
        document = self.document()
        cursor = QTextCursor(document)
        cursor.select(QTextCursor.Document)
        
        block_format = QTextBlockFormat()
        block_format.setBackground(QColor("#1E1E1E"))
        cursor.setBlockFormat(block_format)
        
        self.error_lines.clear()
        self.viewport().update()
    
    def update_line_number_area_width(self, new_block_count):
        width = 50
        self.setViewportMargins(width, 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), 50, cr.height()))
    
    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#252526"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, int(top), self.line_number_area.width(), 
                                self.fontMetrics().height(), Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(50, 0)
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class EditorPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_file = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #2D2D30; border-bottom: 1px solid #3E3E42;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        self.file_label = QLabel("未打开文件")
        self.file_label.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        toolbar_layout.addWidget(self.file_label)
        
        toolbar_layout.addStretch()
        
        self.save_btn = QPushButton("保存")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
        """)
        toolbar_layout.addWidget(self.save_btn)
        
        layout.addWidget(toolbar)
        
        self.editor = MCNP6Editor()
        layout.addWidget(self.editor)
        
        self.status_bar = QFrame()
        self.status_bar.setStyleSheet("background-color: #007ACC; color: white;")
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        self.line_col_label = QLabel("行: 1, 列: 1")
        status_layout.addWidget(self.line_col_label)
        
        status_layout.addStretch()
        
        self.char_count_label = QLabel("字符: 0")
        status_layout.addWidget(self.char_count_label)
        
        layout.addWidget(self.status_bar)
        
        self.editor.cursorPositionChanged.connect(self.update_status)
        self.editor.textChanged.connect(self.update_char_count)
    
    def update_status(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.line_col_label.setText(f"行: {line}, 列: {col}")
    
    def update_char_count(self):
        count = self.editor.toPlainText().__len__()
        self.char_count_label.setText(f"字符: {count}")
    
    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.setPlainText(content)
            self.current_file = file_path
            self.file_label.setText(file_path)
            return True
        except Exception as e:
            return False
    
    def save_file(self, file_path=None):
        try:
            path = file_path or self.current_file
            if not path:
                return False
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            
            self.current_file = path
            self.file_label.setText(path)
            return True
        except Exception as e:
            return False
    
    def get_content(self):
        return self.editor.toPlainText()
    
    def set_content(self, content):
        self.editor.setPlainText(content)
    
    def mark_errors(self, errors):
        self.editor.mark_error_lines(errors)
    
    def mark_warnings(self, warnings):
        self.editor.mark_warning_lines(warnings)
    
    def clear_marks(self):
        self.editor.clear_error_marks()
    
    def get_editor(self):
        return self.editor
