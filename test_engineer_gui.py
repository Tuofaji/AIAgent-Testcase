"""
软件测试工程师智能体GUI界面

功能特点：
1. 专业的测试咨询对话界面
2. 测试用例评审功能
3. 测试策略设计工具
4. 知识库查询功能
5. 历史记录管理
6. 支持从主界面嵌入调用
"""

import sys
import asyncio
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QTabWidget, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QSplitter, QGroupBox, QListWidget, QTextBrowser, QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QTextCursor, QPixmap, QIcon

# 导入测试工程师智能体模块
import test_engineer_agent
from test_engineer_agent import (
    software_test_engineer,
    chat_with_test_engineer,
    ask_test_expert,
    review_my_testcases,
    TEST_KNOWLEDGE_BASE
)

import pandas as pd

class ChatWorkerThread(QThread):
    """聊天工作线程"""
    response_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, message, chat_type="chat"):
        super().__init__()
        self.message = message
        self.chat_type = chat_type

    def run(self):
        try:
            asyncio.run(self._async_chat())
        except Exception as e:
            self.error_signal.emit(f"对话出错: {str(e)}")

    async def _async_chat(self):
        try:
            if self.chat_type == "chat":
                response = await chat_with_test_engineer(self.message)
            elif self.chat_type == "consultation":
                response = await ask_test_expert(self.message)
            else:
                response = await chat_with_test_engineer(self.message)
            
            self.response_signal.emit(response)
        except Exception as e:
            self.error_signal.emit(f"AI响应出错: {str(e)}")

class TestCaseReviewWorkerThread(QThread):
    """测试用例评审工作线程"""
    result_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, test_cases):
        super().__init__()
        self.test_cases = test_cases

    def run(self):
        try:
            asyncio.run(self._async_review())
        except Exception as e:
            self.error_signal.emit(f"评审出错: {str(e)}")

    async def _async_review(self):
        try:
            print("开始评审测试用例...")
            result = await review_my_testcases(self.test_cases)
            print(f"评审结果类型: {type(result)}")
            print(f"评审结果内容: {result[:200]}...")  # 只打印前200个字符
            self.result_signal.emit(result)
        except Exception as e:
            print(f"评审出错详细信息: {str(e)}")
            import traceback
            print(traceback.format_exc())
            self.error_signal.emit(f"评审出错: {str(e)}")

class TestEngineerMainWindow(QMainWindow):
    """软件测试工程师智能体主界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🤖 软件测试工程师智能体 - 专业测试咨询系统")
        self.setGeometry(100, 100, 1200, 800)
        self.chat_history = []
        self.init_ui()
        self.apply_professional_style()
        
        # 添加状态栏消息
        self.statusBar().showMessage("已成功加载软件测试工程师智能体")

    def init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 添加标题和介绍
        self.add_header(main_layout)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 智能对话标签页
        self.create_chat_tab()
        
        # 测试用例评审标签页
        self.create_review_tab()
        
        # 知识库标签页
        self.create_knowledge_tab()
        
        # 系统管理标签页
        self.create_management_tab()
        
        # 添加返回主程序按钮（如果是从主程序打开的）
        if self.parent():
            back_btn = QPushButton("← 返回主程序")
            back_btn.clicked.connect(self.hide)
            main_layout.addWidget(back_btn)

    def add_header(self, layout):
        """添加头部信息"""
        header_group = QGroupBox("🎯 专业身份")
        header_layout = QVBoxLayout(header_group)
        
        title_label = QLabel("高级软件测试工程师 / 测试架构师")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        desc_label = QLabel(
            "专业领域：测试用例生成系统管理 | 测试流程优化 | 质量保证咨询 | 测试团队指导"
        )
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header_group)

    def create_chat_tab(self):
        """创建智能对话标签页"""
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)
        
        # 聊天模式选择
        mode_layout = QHBoxLayout()
        mode_label = QLabel("对话模式:")
        self.chat_mode_combo = QComboBox()
        self.chat_mode_combo.addItems([
            "💬 智能对话", 
            "🎯 专业咨询", 
            "📋 快速问答",
            "🔧 系统管理"
        ])
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.chat_mode_combo)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # 聊天显示区域
        self.chat_display = QTextBrowser()
        self.chat_display.setMinimumHeight(400)
        self.add_welcome_message()
        layout.addWidget(self.chat_display)
        
        # 输入区域
        input_layout = QVBoxLayout()
        
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(100)
        self.chat_input.setPlaceholderText("请输入您的测试相关问题...")
        input_layout.addWidget(self.chat_input)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("🚀 发送")
        self.send_button.clicked.connect(self.send_message)
        
        clear_button = QPushButton("🧹 清空")
        clear_button.clicked.connect(self.clear_chat)
        
        export_button = QPushButton("💾 导出对话")
        export_button.clicked.connect(self.export_chat)
        
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(export_button)
        button_layout.addStretch()
        
        input_layout.addLayout(button_layout)
        layout.addLayout(input_layout)
        
        self.tab_widget.addTab(chat_widget, "💬 智能对话")

    def create_review_tab(self):
        """创建测试用例评审标签页"""
        review_widget = QWidget()
        layout = QVBoxLayout(review_widget)
        
        # 说明
        info_label = QLabel("📋 测试用例评审功能 - 上传Excel文件或直接输入测试用例进行专业评审")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 文件上传区域
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("选择包含测试用例的Excel文件...")
        
        browse_button = QPushButton("📁 浏览文件")
        browse_button.clicked.connect(self.browse_test_file)
        
        load_button = QPushButton("📥 加载用例")
        load_button.clicked.connect(self.load_test_cases)
        
        file_layout.addWidget(QLabel("Excel文件:"))
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_button)
        file_layout.addWidget(load_button)
        
        layout.addLayout(file_layout)
        
        # 测试用例显示和编辑区域
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：测试用例列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("📝 测试用例列表:"))
        
        self.test_case_table = QTableWidget()
        self.test_case_table.setColumnCount(8)
        self.test_case_table.setHorizontalHeaderLabels([
            "模块名称", "功能项", "用例说明", "前置条件", 
            "输入", "执行步骤", "预期结果", "重要程度"
        ])
        left_layout.addWidget(self.test_case_table)
        
        review_button = QPushButton("🔍 开始评审")
        review_button.clicked.connect(self.start_review)
        left_layout.addWidget(review_button)
        
        splitter.addWidget(left_widget)
        
        # 右侧：评审结果
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("📊 评审结果:"))
        
        self.review_result = QTextBrowser()
        # 设置字体和样式，使其更易于阅读
        font = QFont("Consolas", 10)
        self.review_result.setFont(font)
        self.review_result.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.review_result)
        
        splitter.addWidget(right_widget)
        
        # 设置分割比例
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(review_widget, "📋 测试用例评审")

    def create_knowledge_tab(self):
        """创建知识库标签页"""
        knowledge_widget = QWidget()
        layout = QVBoxLayout(knowledge_widget)
        
        layout.addWidget(QLabel("📚 软件测试专业知识库"))
        
        # 知识分类
        knowledge_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：知识分类
        category_widget = QWidget()
        category_layout = QVBoxLayout(category_widget)
        category_layout.addWidget(QLabel("知识分类:"))
        
        self.knowledge_list = QListWidget()
        for category in TEST_KNOWLEDGE_BASE.keys():
            self.knowledge_list.addItem(f"📖 {category}")
        
        self.knowledge_list.itemClicked.connect(self.show_knowledge_detail)
        category_layout.addWidget(self.knowledge_list)
        
        knowledge_splitter.addWidget(category_widget)
        
        # 右侧：知识详情
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.addWidget(QLabel("知识详情:"))
        
        self.knowledge_detail = QTextBrowser()
        detail_layout.addWidget(self.knowledge_detail)
        
        knowledge_splitter.addWidget(detail_widget)
        knowledge_splitter.setSizes([300, 700])
        
        layout.addWidget(knowledge_splitter)
        
        self.tab_widget.addTab(knowledge_widget, "📚 知识库")

    def create_management_tab(self):
        """创建系统管理标签页"""
        management_widget = QWidget()
        layout = QVBoxLayout(management_widget)
        
        layout.addWidget(QLabel("🔧 测试用例生成系统管理"))
        
        # 系统状态
        status_group = QGroupBox("📊 系统状态")
        status_layout = QVBoxLayout(status_group)
        
        self.system_status = QTextBrowser()
        self.system_status.setMaximumHeight(150)
        self.update_system_status()
        status_layout.addWidget(self.system_status)
        
        layout.addWidget(status_group)
        
        # 管理功能
        manage_group = QGroupBox("🛠️ 管理功能")
        manage_layout = QVBoxLayout(manage_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("🔄 刷新状态")
        refresh_button.clicked.connect(self.update_system_status)
        
        config_button = QPushButton("⚙️ 系统配置")
        config_button.clicked.connect(self.show_system_config)
        
        log_button = QPushButton("📋 查看日志")
        log_button.clicked.connect(self.show_system_logs)
        
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(config_button)
        button_layout.addWidget(log_button)
        button_layout.addStretch()
        
        manage_layout.addLayout(button_layout)
        layout.addWidget(manage_group)
        
        # 系统日志
        log_group = QGroupBox("📜 系统日志")
        log_layout = QVBoxLayout(log_group)
        
        self.system_log = QTextBrowser()
        log_layout.addWidget(self.system_log)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(management_widget, "🔧 系统管理")

    def apply_professional_style(self):
        """应用专业样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

    def add_welcome_message(self):
        """添加欢迎消息"""
        welcome_msg = """欢迎使用软件测试工程师智能体！

🎯 专业身份：高级软件测试工程师 / 测试架构师

💼 核心职责：
• 管理和优化测试用例生成系统
• 提供专业的软件测试咨询和指导
• 设计测试策略和测试方案
• 监控和改进测试流程

🛠️ 服务内容：
• 支持测试用例评审和优化建议
• 提供测试策略设计服务
• 分享行业最佳实践和经验

请随时向我咨询测试相关问题！"""
        self.chat_display.setPlainText(welcome_msg)
        
        # 也尝试添加一条系统消息
        self.add_message_to_chat("🤖 测试专家", "您好，我是测试用例生成系统的管理专家。请问有什么可以帮助您的？")

    def send_message(self):
        """发送消息"""
        message = self.chat_input.toPlainText().strip()
        if not message:
            return
        
        # 显示用户消息
        self.add_message_to_chat("👤 您", message)
        self.chat_input.clear()
        
        # 禁用发送按钮
        self.send_button.setEnabled(False)
        self.send_button.setText("🤔 思考中...")
        
        # 获取对话模式
        chat_type = "consultation" if "咨询" in self.chat_mode_combo.currentText() else "chat"
        
        # 启动聊天线程
        self.chat_worker = ChatWorkerThread(message, chat_type)
        self.chat_worker.response_signal.connect(self.handle_chat_response)
        self.chat_worker.error_signal.connect(self.handle_chat_error)
        self.chat_worker.start()

    def handle_chat_response(self, response):
        """处理聊天响应"""
        self.add_message_to_chat("🤖 测试专家", response)
        self.send_button.setEnabled(True)
        self.send_button.setText("🚀 发送")

    def handle_chat_error(self, error):
        """处理聊天错误"""
        self.add_message_to_chat("❌ 系统", f"抱歉，发生错误：{error}")
        self.send_button.setEnabled(True)
        self.send_button.setText("🚀 发送")

    def add_message_to_chat(self, sender, message):
        """添加消息到聊天显示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 使用纯文本格式而不是HTML，确保显示正确
        formatted_message = f"\n{sender} ({timestamp}):\n{message}\n{'='*80}\n"
        
        # 添加到聊天窗口
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(formatted_message)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()
        
        # 添加到历史记录
        self.chat_history.append({"sender": sender, "message": message, "time": timestamp})

    def clear_chat(self):
        """清空聊天"""
        self.chat_display.clear()
        self.add_welcome_message()
        self.chat_history.clear()

    def export_chat(self):
        """导出对话记录"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出对话记录", f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 
            "文本文件 (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 导出为纯文本
                    f.write("软件测试工程师智能体 - 对话记录\n\n")
                    for chat in self.chat_history:
                        f.write(f"{chat['sender']} ({chat['time']}):\n")
                        f.write(f"{chat['message']}\n\n")
                QMessageBox.information(self, "成功", f"对话记录已导出到：{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败：{str(e)}")

    def browse_test_file(self):
        """浏览测试文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择测试用例文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)

    def load_test_cases(self):
        """加载测试用例"""
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "警告", "请先选择文件！")
            return
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 设置表格行数和数据
            self.test_case_table.setRowCount(len(df))
            
            for i, row in df.iterrows():
                for j, value in enumerate(row):
                    if j < self.test_case_table.columnCount():
                        item = QTableWidgetItem(str(value))
                        self.test_case_table.setItem(i, j, item)
            
            QMessageBox.information(self, "成功", f"已加载 {len(df)} 条测试用例")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载文件失败：{str(e)}")

    def start_review(self):
        """开始评审测试用例"""
        if self.test_case_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "请先加载测试用例！")
            return
        
        # 提取测试用例数据
        test_cases = []
        headers = []
        for i in range(self.test_case_table.columnCount()):
            headers.append(self.test_case_table.horizontalHeaderItem(i).text())
        
        for i in range(self.test_case_table.rowCount()):
            case = {}
            for j in range(self.test_case_table.columnCount()):
                item = self.test_case_table.item(i, j)
                case[headers[j]] = item.text() if item else ""
            test_cases.append(case)
        
        # 启动评审线程
        self.review_worker = TestCaseReviewWorkerThread(test_cases)
        self.review_worker.result_signal.connect(self.show_review_result)
        self.review_worker.error_signal.connect(self.show_review_error)
        self.review_worker.start()
        
        self.review_result.setText("🔍 正在进行专业评审，请稍候...")

    def show_review_result(self, result):
        """显示评审结果"""
        try:
            # 检查结果是否包含详细评审结果（Markdown格式）
            if "### 评审结果" in result or "#### JSON格式摘要" in result or "### 详细评审结果" in result:
                # 直接显示格式化好的详细评审结果
                self.review_result.setPlainText(result)
                return
                
            # 检查结果是否为JSON字符串
            if result.strip().startswith('{'):
                try:
                    import json
                    data = json.loads(result)
                    
                    # 构建格式化的评审结果
                    formatted_result = f"""
📊 评审结果：

🔍 总体评分：{data.get('overall_score', 'N/A')}/10

✅ 优点：
{chr(10).join([f"• {strength}" for strength in data.get('strengths', [])])}

⚠️ 不足：
{chr(10).join([f"• {weakness}" for weakness in data.get('weaknesses', [])])}

🔧 改进建议：
{chr(10).join([f"• {improvement}" for improvement in data.get('improvements', [])])}

📈 质量评估：
{chr(10).join([f"• {dim}：{score}/10" for dim, score in data.get('quality_assessment', {}).items()])}
"""
                    self.review_result.setPlainText(formatted_result)
                    return
                except Exception as e:
                    print(f"JSON解析错误: {str(e)}")
                    pass  # 如果解析失败，继续使用原始文本
            
            # 如果既不是JSON也不是详细评审，直接显示原始文本
            self.review_result.setPlainText(result)
        except Exception as e:
            self.review_result.setPlainText(f"显示评审结果出错: {str(e)}\n\n原始结果:\n{result}")

    def show_review_error(self, error):
        """显示评审错误"""
        self.review_result.setPlainText(f"❌ 评审出错：{error}")

    def show_knowledge_detail(self, item):
        """显示知识详情"""
        category_name = item.text().replace("📖 ", "")
        if category_name in TEST_KNOWLEDGE_BASE:
            knowledge = TEST_KNOWLEDGE_BASE[category_name]
            
            # 使用纯文本显示
            detail_text = f"{category_name}\n{'='*50}\n\n"
            for subcategory, items in knowledge.items():
                detail_text += f"▶ {subcategory}:\n"
                for item in items:
                    detail_text += f"  • {item}\n"
                detail_text += "\n"
            
            self.knowledge_detail.setPlainText(detail_text)

    def update_system_status(self):
        """更新系统状态"""
        # 使用纯文本显示
        status_text = f"""
🟢 系统运行正常
更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
智能体版本: v1.0.0
支持功能: 智能对话、用例评审、知识库查询
当前会话: {len(self.chat_history)} 条消息
"""
        self.system_status.setPlainText(status_text)

    def show_system_config(self):
        """显示系统配置"""
        QMessageBox.information(self, "系统配置", "系统配置功能开发中...")

    def show_system_logs(self):
        """显示系统日志"""
        log_content = f"""
[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 系统启动
[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 智能体初始化完成
[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] GUI界面加载完成
[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 等待用户交互...
"""
        self.system_log.setPlainText(log_content)

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("软件测试工程师智能体")
    
    # 设置应用图标（如果有的话）
    # app.setWindowIcon(QIcon("icon.png"))
    
    window = TestEngineerMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 