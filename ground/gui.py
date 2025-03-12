import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                            QLabel, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt

class ProjectBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Folder Browser")
        self.setMinimumSize(600, 400)
        
        # Store project paths
        self.project_paths = []
        
        # Create the main layout
        main_layout = QVBoxLayout()
        
        # Create header section
        header_layout = QHBoxLayout()
        header_label = QLabel("Project Folders:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search projects...")
        self.search_input.textChanged.connect(self.filter_projects)
        
        header_layout.addWidget(header_label)
        header_layout.addWidget(self.search_input)
        main_layout.addLayout(header_layout)
        
        # Create list widget to display projects
        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.open_project_folder)
        main_layout.addWidget(self.project_list)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Project")
        add_button.clicked.connect(self.add_project)
        
        remove_button = QPushButton("Remove Project")
        remove_button.clicked.connect(self.remove_project)
        
        open_button = QPushButton("Open Project")
        open_button.clicked.connect(self.open_selected_project)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(open_button)
        
        main_layout.addLayout(button_layout)
        
        # Create and set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
    def add_project(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            # Check if folder already exists in the list
            if folder not in self.project_paths:
                self.project_paths.append(folder)
                self.project_list.addItem(folder)
            else:
                QMessageBox.warning(self, "Warning", "This project folder is already in the list.")
    
    def remove_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a project to remove.")
            return
            
        for item in selected_items:
            row = self.project_list.row(item)
            self.project_list.takeItem(row)
            self.project_paths.remove(item.text())
    
    def open_selected_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a project to open.")
            return
            
        self.open_project_folder(selected_items[0])
    
    def open_project_folder(self, item):
        path = item.text()
        # Open the folder using the default file explorer
        # This approach works on different operating systems
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{path}"')
            else:  # Linux
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open folder: {str(e)}")
    
    def filter_projects(self):
        search_text = self.search_input.text().lower()
        for i in range(self.project_list.count()):
            item = self.project_list.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

def main():
    app = QApplication(sys.argv)
    window = ProjectBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()