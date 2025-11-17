"""
Class Manager Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QListWidget, QMessageBox, QTextEdit,
                             QGridLayout, QColorDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class ClassManagerDialog(QDialog):
    """Dialog for managing classes"""

    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.selected_class_id = None

        self.setWindowTitle("Manage Classes")
        self.setModal(True)
        self.resize(700, 600)

        self.init_ui()
        self.load_classes()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Class Management")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        # Split layout - left for list, right for form
        h_layout = QHBoxLayout()

        # Left panel - Classes list
        left_panel = QVBoxLayout()
        list_label = QLabel("Existing Classes:")
        left_panel.addWidget(list_label)

        self.classes_list = QListWidget()
        self.classes_list.itemClicked.connect(self.class_selected)
        left_panel.addWidget(self.classes_list)

        h_layout.addLayout(left_panel)

        # Right panel - Form
        right_panel = QVBoxLayout()
        form_label = QLabel("Add/Edit Class:")
        form_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        right_panel.addWidget(form_label)

        # Create form grid
        form_grid = QGridLayout()

        # Name
        form_grid.addWidget(QLabel("Name:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter class name e.g., Class 1...")
        form_grid.addWidget(self.name_input, 0, 1)

        # Color picker
        form_grid.addWidget(QLabel("Color:"), 1, 0)
        color_layout = QHBoxLayout()
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("#RRGGBB or color name...")
        color_layout.addWidget(self.color_input)
        self.color_btn = QPushButton("Choose")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(20, 20)
        self.color_preview.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        form_grid.addLayout(color_layout, 1, 1)

        right_panel.addLayout(form_grid)

        # Description
        desc_label = QLabel("Description:")
        right_panel.addWidget(desc_label)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Class description (optional)...")
        self.description_input.setMaximumHeight(60)
        right_panel.addWidget(self.description_input)

        # Buttons
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ Add New")
        self.add_btn.clicked.connect(self.add_class)
        btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("✏️ Update Selected")
        self.update_btn.clicked.connect(self.update_class)
        self.update_btn.setEnabled(False)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.clicked.connect(self.delete_class)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.clear_btn)

        right_panel.addLayout(btn_layout)
        right_panel.addStretch()

        h_layout.addLayout(right_panel)
        layout.addLayout(h_layout)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)

    def load_classes(self):
        """Load classes into list"""
        self.classes_list.clear()
        classes = self.db.get_all_classes()

        for class_info in classes:
            activities_count = class_info.get('activities_count', 0)
            color = class_info.get('color', '')
            color_indicator = f" ■ " if color else ""
            item_text = f"{color_indicator}{class_info['name']} ({activities_count} activities)"
            self.classes_list.addItem(item_text)
            self.classes_list.item(self.classes_list.count() - 1).setData(
                Qt.ItemDataRole.UserRole, class_info['id']
            )

    def class_selected(self, item):
        """Handle class selection"""
        self.selected_class_id = item.data(Qt.ItemDataRole.UserRole)
        class_info = self.db.get_class_by_id(self.selected_class_id)

        if class_info:
            self.name_input.setText(class_info.get('name', ''))
            self.color_input.setText(class_info.get('color', ''))
            self.description_input.setText(class_info.get('description', ''))

            # Update color preview
            self.update_color_preview(class_info.get('color', ''))

            self.update_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)

    def add_class(self):
        """Add new class"""
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a class name")
            return

        class_id = self.db.add_class(
            name=name,
            description=self.description_input.toPlainText().strip(),
            color=self.color_input.text().strip()
        )

        if class_id > 0:
            QMessageBox.information(self, "Success", f"Class '{name}' added successfully")
            self.load_classes()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", f"Class '{name}' already exists")

    def update_class(self):
        """Update selected class"""
        if not self.selected_class_id:
            return

        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a class name")
            return

        if self.db.update_class(
            self.selected_class_id,
            name=name,
            description=self.description_input.toPlainText().strip(),
            color=self.color_input.text().strip()
        ):
            QMessageBox.information(self, "Success", "Class updated successfully")
            self.load_classes()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", "Failed to update class or name already exists")

    def delete_class(self):
        """Delete selected class"""
        if not self.selected_class_id:
            return

        class_info = self.db.get_class_by_id(self.selected_class_id)
        if not class_info:
            return

        activities_count = len(self.db.get_activities_filtered(class_filter=class_info['name']))

        msg = f"Are you sure you want to delete class '{class_info['name']}'?"
        if activities_count > 0:
            msg += f"\n\nThis will affect {activities_count} associated activity(s)!"

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_class(self.selected_class_id):
                QMessageBox.information(self, "Success", "Class deleted successfully")
                self.load_classes()
                self.clear_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete class")

    def choose_color(self):
        """Open color picker dialog"""
        current_color = self.parse_color(self.color_input.text().strip())
        color = QColorDialog.getColor(current_color, self, "Choose Class Color")

        if color.isValid():
            color_hex = color.name()  # Get hex format #RRGGBB
            self.color_input.setText(color_hex)
            self.update_color_preview(color_hex)

    def parse_color(self, color_str):
        """Parse color string to QColor"""
        if not color_str:
            return QColor('white')

        color = QColor(color_str)
        return color if color.isValid() else QColor('white')

    def update_color_preview(self, color_str):
        """Update color preview label"""
        if color_str:
            self.color_preview.setStyleSheet(f"border: 1px solid #ccc; background-color: {color_str};")
        else:
            self.color_preview.setStyleSheet("border: 1px solid #ccc; background-color: white;")

    def clear_form(self):
        """Clear form inputs"""
        self.name_input.clear()
        self.color_input.clear()
        self.description_input.clear()
        self.update_color_preview('')
        self.selected_class_id = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.classes_list.clearSelection()
