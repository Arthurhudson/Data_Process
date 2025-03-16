import sys
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                           QListWidget, QMessageBox, QCheckBox, QLineEdit,
                           QComboBox, QGroupBox, QGridLayout, QScrollArea,
                           QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from settings_manager import SettingsManager

class CustomMessageBox(QMessageBox):
    def __init__(self, icon, title, text, buttons, parent=None):
        super().__init__(icon, title, text, buttons, parent)
        
        # 创建背景面板
        self.bg_widget = QWidget(self)
        self.bg_widget.setObjectName("background")
        self.bg_widget.setStyleSheet("""
            QWidget#background {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                border-radius: 8px;
            }
        """)
        
        # 设置窗口标题栏样式
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置窗口大小
        self.setMinimumWidth(300)
        self.setMinimumHeight(150)
        
        # 设置样式表
        self.setStyleSheet("""
            QMessageBox {
                background-color: transparent;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
                padding: 10px;
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: #0d47a1;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d8f;
            }
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        # 设置文本颜色和格式
        self.setText(f'<span style="color: #ffffff;">{text}</span>')
        
        # 设置按钮样式
        for button in self.buttons():
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #0d47a1;
                    color: #ffffff;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 14px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:pressed {
                    background-color: #0a3d8f;
                }
            """)
        
        # 设置图标
        if icon is not None:
            self.setIconPixmap(self.iconPixmap().scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    
    def showEvent(self, event):
        super().showEvent(event)
        # 调整背景面板大小以适应整个消息框
        self.bg_widget.setGeometry(self.rect())
        # 确保背景面板在最底层
        self.bg_widget.lower()

class FilterCondition(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 过滤列选择
        self.filter_column = QComboBox()
        self.filter_column.setMinimumWidth(150)
        layout.addWidget(self.filter_column)
        
        # 过滤类型选择
        self.filter_type = QComboBox()
        self.filter_type.setMinimumWidth(100)
        self.filter_type.addItems(["等于", "不等于", "包含", "不包含", "大于", "小于", "大于等于", "小于等于"])
        layout.addWidget(self.filter_type)
        
        # 过滤值输入
        self.filter_value = QLineEdit()
        self.filter_value.setMinimumWidth(150)
        layout.addWidget(self.filter_value)
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        delete_btn.clicked.connect(self.deleteLater)
        layout.addWidget(delete_btn)
        
        # 设置布局
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox, QLineEdit {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
            }
        """)

    def get_settings(self):
        return {
            "column": self.filter_column.currentText(),
            "type": self.filter_type.currentText(),
            "value": self.filter_value.text()
        }

    def load_settings(self, settings):
        if settings:
            self.filter_column.setCurrentText(settings.get("column", ""))
            self.filter_type.setCurrentText(settings.get("type", "等于"))
            self.filter_value.setText(settings.get("value", ""))

class ExcelProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel 文档处理器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置深色主题样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                font-size: 14px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #0d47a1;
                color: white;
            }
            QGroupBox {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #ffffff;
            }
            QComboBox, QLineEdit {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
            }
            QScrollArea {
                border: none;
                background-color: #2b2b2b;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2b2b2b;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        
        # 初始化设置管理器
        self.settings_manager = SettingsManager()
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: #cccccc;")
        select_file_btn = QPushButton("选择Excel文件")
        select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_file_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 列选择区域
        columns_group = QGroupBox("选择要保留的列")
        columns_layout = QVBoxLayout()
        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        columns_layout.addWidget(self.columns_list)
        columns_group.setLayout(columns_layout)
        layout.addWidget(columns_group)
        
        # 过滤条件区域
        filter_group = QGroupBox("过滤条件")
        filter_layout = QVBoxLayout()
        
        # 添加过滤条件按钮
        add_filter_btn = QPushButton("添加过滤条件")
        add_filter_btn.clicked.connect(self.add_filter_condition)
        filter_layout.addWidget(add_filter_btn)
        
        # 过滤条件容器
        self.filter_container = QWidget()
        self.filter_container_layout = QVBoxLayout(self.filter_container)
        self.filter_container_layout.setSpacing(10)
        self.filter_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidget(self.filter_container)
        scroll.setWidgetResizable(True)
        filter_layout.addWidget(scroll)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        process_btn = QPushButton("处理文件")
        process_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        process_btn.clicked.connect(self.process_file)
        save_settings_btn = QPushButton("保存设置")
        save_settings_btn.clicked.connect(self.save_current_settings)
        load_settings_btn = QPushButton("加载设置")
        load_settings_btn.clicked.connect(self.load_saved_settings)
        
        button_layout.addWidget(process_btn)
        button_layout.addWidget(save_settings_btn)
        button_layout.addWidget(load_settings_btn)
        layout.addLayout(button_layout)
        
        # 状态显示
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.status_label)
        
        self.df = None
        self.file_path = None
        
        # 加载保存的设置
        self.load_saved_settings()

    def add_filter_condition(self):
        filter_condition = FilterCondition()
        if self.df is not None:
            filter_condition.filter_column.addItems(self.df.columns)
        self.filter_container_layout.addWidget(filter_condition)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Excel文件",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.file_path = file_path
            self.file_label.setText(file_path.split('/')[-1])
            self.load_excel()

    def load_excel(self):
        try:
            self.df = pd.read_excel(self.file_path)
            self.columns_list.clear()
            self.columns_list.addItems(self.df.columns)
            
            # 更新所有过滤条件的列选择
            for i in range(self.filter_container_layout.count()):
                widget = self.filter_container_layout.itemAt(i).widget()
                if isinstance(widget, FilterCondition):
                    widget.filter_column.clear()
                    widget.filter_column.addItems(self.df.columns)
            
            self.status_label.setText(f"成功加载文件，共 {len(self.df.columns)} 列")
        except Exception as e:
            msg = CustomMessageBox(QMessageBox.Icon.Critical, "错误", f"加载文件时出错：{str(e)}", QMessageBox.StandardButton.Ok, self)
            msg.exec()

    def save_current_settings(self):
        if self.df is None:
            msg = CustomMessageBox(QMessageBox.Icon.Warning, "警告", "请先选择Excel文件", QMessageBox.StandardButton.Ok, self)
            msg.exec()
            return
            
        settings = {
            "selected_columns": [item.text() for item in self.columns_list.selectedItems()],
            "filter_conditions": []
        }
        
        # 保存过滤条件
        for i in range(self.filter_container_layout.count()):
            widget = self.filter_container_layout.itemAt(i).widget()
            if isinstance(widget, FilterCondition):
                settings["filter_conditions"].append(widget.get_settings())
        
        if self.settings_manager.save_settings(settings):
            msg = CustomMessageBox(QMessageBox.Icon.Information, "成功", "设置已保存", QMessageBox.StandardButton.Ok, self)
            msg.exec()
        else:
            msg = CustomMessageBox(QMessageBox.Icon.Warning, "警告", "保存设置失败", QMessageBox.StandardButton.Ok, self)
            msg.exec()

    def load_saved_settings(self):
        settings = self.settings_manager.get_settings()
        if not settings:
            return
            
        # 加载选中的列
        if self.df is not None and "selected_columns" in settings:
            for column in settings["selected_columns"]:
                items = self.columns_list.findItems(column, Qt.MatchFlag.MatchExactly)
                if items:
                    items[0].setSelected(True)
        
        # 加载过滤条件
        if "filter_conditions" in settings:
            # 清除现有的过滤条件
            while self.filter_container_layout.count():
                item = self.filter_container_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 添加保存的过滤条件
            for condition_settings in settings["filter_conditions"]:
                filter_condition = FilterCondition()
                if self.df is not None:
                    filter_condition.filter_column.addItems(self.df.columns)
                filter_condition.load_settings(condition_settings)
                self.filter_container_layout.addWidget(filter_condition)

    def apply_filter(self, df):
        # 获取所有过滤条件
        filter_conditions = []
        for i in range(self.filter_container_layout.count()):
            widget = self.filter_container_layout.itemAt(i).widget()
            if isinstance(widget, FilterCondition):
                if widget.filter_value.text():  # 只处理有值的过滤条件
                    filter_conditions.append(widget)
        
        if not filter_conditions:
            return df
            
        # 应用所有过滤条件
        filtered_df = df.copy()
        for condition in filter_conditions:
            column = condition.filter_column.currentText()
            value = condition.filter_value.text()
            filter_type = condition.filter_type.currentText()
            
            try:
                # 尝试将列转换为数值类型
                try:
                    filtered_df[column] = pd.to_numeric(filtered_df[column], errors='ignore')
                except:
                    pass
                    
                if filter_type == "等于":
                    filtered_df = filtered_df[filtered_df[column].astype(str) == value]
                elif filter_type == "不等于":
                    filtered_df = filtered_df[filtered_df[column].astype(str) != value]
                elif filter_type == "包含":
                    filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False, na=False)]
                elif filter_type == "不包含":
                    filtered_df = filtered_df[~filtered_df[column].astype(str).str.contains(value, case=False, na=False)]
                elif filter_type in ["大于", "小于", "大于等于", "小于等于"]:
                    # 检查列是否为数值类型
                    if pd.api.types.is_numeric_dtype(filtered_df[column]):
                        value = float(value)
                        if filter_type == "大于":
                            filtered_df = filtered_df[filtered_df[column] > value]
                        elif filter_type == "小于":
                            filtered_df = filtered_df[filtered_df[column] < value]
                        elif filter_type == "大于等于":
                            filtered_df = filtered_df[filtered_df[column] >= value]
                        elif filter_type == "小于等于":
                            filtered_df = filtered_df[filtered_df[column] <= value]
                    else:
                        msg = CustomMessageBox(QMessageBox.Icon.Warning, "警告", f"列 '{column}' 不是数值类型，无法进行数值比较", QMessageBox.StandardButton.Ok, self)
                        msg.exec()
                        continue
            except Exception as e:
                msg = CustomMessageBox(QMessageBox.Icon.Warning, "警告", f"应用过滤条件时出错：{str(e)}\n请确保过滤值与列的数据类型匹配", QMessageBox.StandardButton.Ok, self)
                msg.exec()
                continue
                
        return filtered_df

    def process_file(self):
        if self.df is None:
            msg = CustomMessageBox(QMessageBox.Icon.Warning, "警告", "请先选择Excel文件", QMessageBox.StandardButton.Ok, self)
            msg.exec()
            return
            
        selected_columns = [item.text() for item in self.columns_list.selectedItems()]
        if not selected_columns:
            msg = CustomMessageBox(QMessageBox.Icon.Warning, "警告", "请选择至少一列", QMessageBox.StandardButton.Ok, self)
            msg.exec()
            return
            
        try:
            # 只保留选中的列
            processed_df = self.df[selected_columns]
            
            # 应用过滤条件
            processed_df = self.apply_filter(processed_df)
            
            # 生成新文件名
            output_path = self.file_path.rsplit('.', 1)[0] + '_processed.xlsx'
            
            # 保存处理后的文件
            processed_df.to_excel(output_path, index=False)
            
            # 生成提示信息
            tips = self.generate_tips(processed_df)
            
            self.status_label.setText(f"处理完成！\n保存至：{output_path}\n\n提示：\n{tips}")
            msg = CustomMessageBox(QMessageBox.Icon.Information, "成功", "文件处理完成！", QMessageBox.StandardButton.Ok, self)
            msg.exec()
            
        except Exception as e:
            msg = CustomMessageBox(QMessageBox.Icon.Critical, "错误", f"处理文件时出错：{str(e)}", QMessageBox.StandardButton.Ok, self)
            msg.exec()

    def generate_tips(self, df):
        tips = []
        
        # 检查空值
        null_counts = df.isnull().sum()
        if null_counts.any():
            tips.append("数据质量提示：")
            for col, count in null_counts[null_counts > 0].items():
                tips.append(f"- {col} 列包含 {count} 个空值")
        
        # 检查重复值
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            tips.append(f"\n发现 {duplicates} 行重复数据")
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            tips.append("\n数值列统计：")
            for col in numeric_cols:
                tips.append(f"- {col}:")
                tips.append(f"  最小值: {df[col].min()}")
                tips.append(f"  最大值: {df[col].max()}")
                tips.append(f"  平均值: {df[col].mean():.2f}")
        
        return "\n".join(tips)

def main():
    app = QApplication(sys.argv)
    window = ExcelProcessor()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 