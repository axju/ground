from typing import Optional
import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QFileDialog, QDialog, QLabel, QFormLayout
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLineEdit, QFileDialog, QLabel, QFormLayout, QSpinBox, 
    QDoubleSpinBox, QCheckBox, QDialog
)
from PySide6.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem, 
                              QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                              QPushButton, QLabel)
from PySide6.QtCore import QSettings
from pydantic import BaseModel, Field, ValidationError
from pathlib import Path

from ground.config import Config
from ground.core import Ground


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fields = {}  # Store field references
        self.setWindowTitle("Settings")
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # 🔹 Generate Fields Based on Pydantic Model
        for field_name, field_info in Config.model_fields.items():
            label = QLabel(field_info.description or field_name)
            field_type = field_info.annotation
            widget = None

            # Create Input Widgets Based on Type
            if field_type in (Path, str, Optional[Path]): 
                widget = QLineEdit()
                if field_type in (Path, Optional[Path]):
                    browse_button = QPushButton("Browse...")
                    browse_button.clicked.connect(lambda _, fn=field_name: self.browse_path(fn))
                    row_layout = QVBoxLayout()
                    row_layout.addWidget(widget)
                    row_layout.addWidget(browse_button)
                    form_layout.addRow(label, row_layout)
                    self.fields[field_name] = widget
                    continue
            elif field_type == int:  # Integer Input
                widget = QSpinBox()
                widget.setMinimum(-999999)
                widget.setMaximum(999999)
            elif field_type == float:  # Float Input
                widget = QDoubleSpinBox()
                widget.setDecimals(2)
                widget.setMinimum(-999999.99)
                widget.setMaximum(999999.99)
            elif field_type == bool:  # Checkbox for Boolean
                widget = QCheckBox()

            # Store Widget Reference
            if widget:
                self.fields[field_name] = widget
                form_layout.addRow(label, widget)

        # 🔹 Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)

        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def browse_path(self, field_name):
        """Open file dialog for selecting a path."""
        path = QFileDialog.getExistingDirectory(self, f"Select {field_name}")
        if path:
            self.fields[field_name].setText(path)

    def save_settings(self):
        """Save all settings dynamically"""
        settings_data = {}

        for name, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                settings_data[name] = widget.text()
            elif isinstance(widget, QSpinBox):
                settings_data[name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                settings_data[name] = widget.value()
            elif isinstance(widget, QCheckBox):
                settings_data[name] = widget.isChecked()

        Config(**settings_data).save()
        self.accept()  # Close the dialog

    def load_settings(self):
        """Load settings and populate form fields"""
        config = Config.load()
        for field_name, value in config.model_dump().items():
            widget = self.fields.get(field_name)
            if widget:
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                    widget.setValue(value)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value)


class ProjectTableWidget(QTableWidget):

    def __init__(self, ground: Ground, parent=None):
        super().__init__(parent)
        self.ground = ground
        
        self.init_ui()

    def init_ui(self):
        fields = ["ID", "Name", "Images"]
        self.setColumnCount(len(fields))
        self.setHorizontalHeaderLabels(fields)
        
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)

    def load_projects(self):
        self.setRowCount(len(self.ground.projects))
        for row, project in enumerate(self.ground.projects):
            self.setItem(row, 0, QTableWidgetItem(str(project.data.desc.identifier)))
            self.setItem(row, 1, QTableWidgetItem(project.data.desc.name.strip()))
            self.setItem(row, 2, QTableWidgetItem(str(len(project.images))))
            
        self.resizeColumnsToContents()


class ButtonNaviWidget(QHBoxLayout):

    def add_button(self, name: str, callback):
        button = QPushButton(name)
        button.clicked.connect(callback)
        self.addWidget(button)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ground = Ground()
        
        self.init_ui()
        self.load_projects()

    def init_ui(self):
        self.setWindowTitle("Project Manager")
        self.setGeometry(100, 100, 600, 400)

        button_layout = ButtonNaviWidget()
        button_layout.add_button("Refresh", self.load_projects)
        button_layout.add_button("Settings", self.open_settings)
        button_layout.add_button("html", self.build_html)

        self.project_list = ProjectTableWidget(self.ground)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.project_list)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
    def load_projects(self):
        self.ground.update()
        self.project_list.load_projects()

    def build_html(self):
        self.ground.build_html()

    def open_settings(self):
        if ConfigDialog(self).exec():
            self.ground.config = Config.load()
            self.load_projects()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
