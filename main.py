import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from main_window import MCNP6AIWindow
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("开始启动应用程序...")
        
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        logger.info("创建QApplication...")
        app = QApplication(sys.argv)
        
        logger.info("创建主窗口...")
        window = MCNP6AIWindow()
        logger.info("显示主窗口...")
        window.show()
        
        logger.info("验证配置...")
        errors = Config.validate()
        if errors:
            logger.warning(f"配置验证失败: {errors}")
            msg = "配置验证失败，请检查 .env 文件：\n\n"
            msg += "\n".join(f"- {error}" for error in errors)
            msg += "\n\n程序将继续运行，但部分功能可能不可用。"
            QMessageBox.warning(window, "配置警告", msg)
        
        logger.info("应用程序启动成功，进入主循环...")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {str(e)}", exc_info=True)
        if 'app' in locals():
            QMessageBox.critical(None, "启动错误", f"应用程序启动失败:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
