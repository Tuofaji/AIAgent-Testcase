import sys
import asyncio
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QSpinBox
)
from PyQt5.QtCore import QThread, pyqtSignal
from DocAGTest import run_agent as doc_to_db
from Sql_agent import run_agent as sql_query_agent
from Testcase_agent import run_agent as testcase_gen_agent
from test_engineer_gui import TestEngineerMainWindow

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(str)

    def __init__(self, doc_path, db_path, excel_path, total, batch_size, doc_prompt, sql_prompt, case_prompt, start_id=1):
        super().__init__()
        self.doc_path = doc_path
        self.db_path = db_path
        self.excel_path = excel_path
        self.total = total  # 用作目标生成数量
        self.batch_size = batch_size  # 用作 max_batch_size
        self.doc_prompt = doc_prompt
        self.sql_prompt = sql_prompt
        self.case_prompt = case_prompt
        self.start_id = start_id

    def run(self):
        asyncio.run(self.run_all())

    async def run_all(self):
        try:
            self.log_signal.emit('【1/3】将需求文档内容写入数据库...')
            self.log_signal.emit('智能分批模式：优先尝试一次性生成，如检测到截断将自动分批处理')
            
            # 文档入库，支持智能分批
            all_sqls = await doc_to_db(self.doc_prompt, start_id=self.start_id, max_batch_size=self.batch_size)
            self.log_signal.emit(f'需求写入数据库完成，共{len(all_sqls)}条。')

            self.log_signal.emit('【2/3】自动生成需求查询SQL...')
            # SQL 查询，传递当前 ID 范围
            current_id = self.start_id + len(all_sqls)
            requirements_list = await sql_query_agent(self.sql_prompt, db_path=self.db_path, filter=self.sql_prompt, start_id=current_id)
            self.log_signal.emit(f'查询到的需求数据: 共{len(requirements_list)}条')
            
            # 打印前几条需求内容用于调试
            if requirements_list:
                self.log_signal.emit('需求内容示例:')
                for i, req in enumerate(requirements_list[:3]):  # 显示前3条
                    self.log_signal.emit(f'  {i+1}. {req[:50]}...')

            self.log_signal.emit('【3/3】自动生成测试用例...')
            # 测试用例生成，传递需求列表和当前 ID 范围，支持智能分批
            current_id = current_id + len(requirements_list)
            test_cases = await testcase_gen_agent(
                self.case_prompt,
                db_path=self.db_path,
                excel_path=self.excel_path,
                filter=self.sql_prompt,
                start_id=current_id,
                target_count=self.total,  # 使用用户设置的总数
                requirements_list=requirements_list  # 传递具体需求列表
            )
            self.log_signal.emit(f'生成的测试用例: 共{len(test_cases)}条')

            self.log_signal.emit('所有任务完成！数据已保存到相应文件中。')
            self.done_signal.emit('测试用例生成完成！')
        except Exception as e:
            self.log_signal.emit(f'执行出错: {str(e)}')
            import traceback
            self.log_signal.emit(f'详细错误: {traceback.format_exc()}')
            self.done_signal.emit('执行过程中出错！')

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试用例自动生成系统")
        self.setGeometry(300, 200, 700, 600)
        self.test_engineer_window = None  # 初始化测试工程师窗口引用
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 需求写入数据库指令
        self.doc_prompt_edit = QLineEdit("请将商品管理模块的列表UI、新增需求写入数据库，id从1开始。")
        layout.addWidget(QLabel("需求写入数据库指令:"))
        layout.addWidget(self.doc_prompt_edit)

        # SQL生成指令
        self.sql_prompt_edit = QLineEdit("请创建一个 SELECT 查询来获取商品管理模块的需求。")
        layout.addWidget(QLabel("SQL生成指令:"))
        layout.addWidget(self.sql_prompt_edit)

        # 测试用例生成指令
        self.case_prompt_edit = QLineEdit("将需求列表中的列表UI、新增功能整理成测试用例。")
        layout.addWidget(QLabel("测试用例生成指令:"))
        layout.addWidget(self.case_prompt_edit)

        # 文档路径
        doc_layout = QHBoxLayout()
        self.doc_path_edit = QLineEdit("./doc/ERP（资源协同）管理平台需求说明书（商品管理部分）.doc")
        doc_btn = QPushButton("选择需求文档")
        doc_btn.clicked.connect(self.choose_doc)
        doc_layout.addWidget(QLabel("需求文档路径:"))
        doc_layout.addWidget(self.doc_path_edit)
        doc_layout.addWidget(doc_btn)
        layout.addLayout(doc_layout)

        # 数据库路径
        db_layout = QHBoxLayout()
        self.db_path_edit = QLineEdit(".chat_app_db.sqlite")
        db_btn = QPushButton("选择数据库")
        db_btn.clicked.connect(self.choose_db)
        db_layout.addWidget(QLabel("数据库路径:"))
        db_layout.addWidget(self.db_path_edit)
        db_layout.addWidget(db_btn)
        layout.addLayout(db_layout)

        # Excel路径
        excel_layout = QHBoxLayout()
        self.excel_path_edit = QLineEdit("./Exel/new_cases.xlsx")
        excel_btn = QPushButton("选择Excel输出")
        excel_btn.clicked.connect(self.choose_excel)
        excel_layout.addWidget(QLabel("Excel输出路径:"))
        excel_layout.addWidget(self.excel_path_edit)
        excel_layout.addWidget(excel_btn)
        layout.addLayout(excel_layout)

        # 数量和批量
        param_layout = QHBoxLayout()
        self.total_spin = QSpinBox()
        self.total_spin.setRange(1, 1000)
        self.total_spin.setValue(25)
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(1, 100)
        self.batch_spin.setValue(10)
        param_layout.addWidget(QLabel("用例总数:"))
        param_layout.addWidget(self.total_spin)
        param_layout.addWidget(QLabel("单批生成数:"))
        param_layout.addWidget(self.batch_spin)
        layout.addLayout(param_layout)

        # 日志窗口
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel("运行日志:"))
        layout.addWidget(self.log_text)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 运行按钮
        self.run_btn = QPushButton("一键生成测试用例")
        self.run_btn.clicked.connect(self.run_all)
        button_layout.addWidget(self.run_btn)
        
        # 添加测试工程师智能体按钮
        self.test_engineer_btn = QPushButton("🤖 测试工程师智能体")
        self.test_engineer_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.test_engineer_btn.clicked.connect(self.open_test_engineer)
        button_layout.addWidget(self.test_engineer_btn)
        
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def choose_doc(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择需求文档", "", "Word文档 (*.doc *.docx)")
        if path:
            self.doc_path_edit.setText(path)

    def choose_db(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择数据库文件", "", "SQLite数据库 (*.sqlite *.db)")
        if path:
            self.db_path_edit.setText(path)

    def choose_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择Excel输出", "", "Excel文件 (*.xlsx)")
        if path:
            self.excel_path_edit.setText(path)

    def run_all(self):
        doc_path = self.doc_path_edit.text().strip()
        db_path = self.db_path_edit.text().strip()
        excel_path = self.excel_path_edit.text().strip()
        total = self.total_spin.value()
        batch_size = self.batch_spin.value()
        doc_prompt = self.doc_prompt_edit.text().strip()
        sql_prompt = self.sql_prompt_edit.text().strip()
        case_prompt = self.case_prompt_edit.text().strip()

        if not doc_path or not db_path or not excel_path:
            QMessageBox.warning(self, "参数错误", "请填写所有路径参数！")
            return

        self.run_btn.setEnabled(False)
        self.log_text.clear()
        self.log_text.append("开始执行...")

        self.worker = WorkerThread(doc_path, db_path, excel_path, total, batch_size, doc_prompt, sql_prompt, case_prompt)
        self.worker.log_signal.connect(self.log_text.append)
        self.worker.done_signal.connect(self.on_done)
        self.worker.start()
        
    def open_test_engineer(self):
        """打开测试工程师智能体界面"""
        # 直接创建测试工程师窗口
        app = QApplication.instance() or QApplication(sys.argv)
        self.test_engineer_window = TestEngineerMainWindow()
        self.test_engineer_window.show()

    def on_done(self, msg):
        self.run_btn.setEnabled(True)
        QMessageBox.information(self, "完成", msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 