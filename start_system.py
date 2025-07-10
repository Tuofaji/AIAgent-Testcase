"""
测试系统统一启动脚本

功能：
1. 启动测试用例自动生成系统主界面
2. 集成软件测试工程师智能体
"""

import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont
import traceback

def show_error_and_exit(message):
    """显示错误信息并退出"""
    app = QApplication.instance() or QApplication(sys.argv)
    QMessageBox.critical(None, "启动失败", f"启动系统时发生错误:\n\n{message}")
    sys.exit(1)

def start_application():
    """启动应用程序"""
    app = QApplication(sys.argv)
    app.setApplicationName("测试系统")
    app.setStyle("Fusion")  # 使用Fusion风格提升跨平台一致性
    
    # 创建启动画面
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(Qt.white)
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    
    # 添加启动画面文字
    splash.showMessage(
        "正在启动测试系统...", 
        alignment=Qt.AlignCenter | Qt.AlignBottom,
        color=Qt.black
    )
    splash.show()
    app.processEvents()
    
    # 检查依赖模块
    try:
        # 延迟导入主窗口类以便在显示启动画面之后再加载
        from gui_main import MainWindow
        
        # 更新启动画面信息
        splash.showMessage("加载测试用例自动生成系统...", alignment=Qt.AlignCenter | Qt.AlignBottom, color=Qt.black)
        app.processEvents()
        
        # 创建并显示主窗口
        window = MainWindow()
        
        # 延迟0.5秒关闭启动画面并显示主窗口
        def finish_splash():
            splash.finish(window)
            window.show()
            # 显示欢迎信息
            window.log_text.append("✅ 系统启动成功")
            window.log_text.append("🎯 提示: 点击右侧的「测试工程师智能体」按钮可以启动专业测试咨询系统")
        
        QTimer.singleShot(500, finish_splash)
        
        sys.exit(app.exec_())
    
    except ImportError as e:
        error_msg = f"导入模块失败: {str(e)}\n\n{traceback.format_exc()}"
        show_error_and_exit(error_msg)
    
    except Exception as e:
        error_msg = f"初始化失败: {str(e)}\n\n{traceback.format_exc()}"
        show_error_and_exit(error_msg)

if __name__ == "__main__":
    start_application() 