"""
Activity Manager Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QListWidget, QMessageBox, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QColor


class ActivityManagerDialog(QDialog):
    """Dialog for managing activities"""
    
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.selected_activity_id = None

        self.setWindowTitle("Manage Activities")
        self.setModal(True)
        self.resize(600, 500)

        self.init_ui()
        self.load_filter_options()
        self.load_activities()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Activity Management")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        # Activities list
        list_label = QLabel("Existing Activities:")
        layout.addWidget(list_label)
        
        self.activities_list = QListWidget()
        self.activities_list.itemClicked.connect(self.activity_selected)
        layout.addWidget(self.activities_list)
        
        # Form section
        form_label = QLabel("Add/Edit Activity:")
        form_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(form_label)
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter activity name...")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Initialize UI components first
        self.class_input = QComboBox()
        self.class_input.setEditable(False)  # Only predefined classes allowed

        self.section_input = QComboBox()
        self.section_input.setEditable(False)  # Only predefined sections allowed

        # Class and Section inputs
        class_section_layout = QHBoxLayout()

        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Class:"))
        class_layout.addWidget(self.class_input)

        add_class_btn = QPushButton("+")
        add_class_btn.setMaximumWidth(30)
        add_class_btn.setToolTip("Add new class")
        add_class_btn.clicked.connect(self.open_class_manager)
        class_layout.addWidget(add_class_btn)
        class_section_layout.addLayout(class_layout)

        section_layout = QHBoxLayout()
        section_layout.addWidget(QLabel("Section:"))
        section_layout.addWidget(self.section_input)

        add_section_btn = QPushButton("+")
        add_section_btn.setMaximumWidth(30)
        add_section_btn.setToolTip("Add new section")
        add_section_btn.clicked.connect(self.open_section_manager)
        section_layout.addWidget(add_section_btn)
        class_section_layout.addLayout(section_layout)

        layout.addLayout(class_section_layout)

        # Description input
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter activity description (optional)...")
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Add New")
        self.add_btn.clicked.connect(self.add_activity)
        btn_layout.addWidget(self.add_btn)
        
        self.update_btn = QPushButton("✏️ Update Selected")
        self.update_btn.clicked.connect(self.update_activity)
        self.update_btn.setEnabled(False)
        btn_layout.addWidget(self.update_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.clicked.connect(self.delete_activity)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)
        
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)

    def load_filter_options(self):
        """Load class and section filter options"""
        # Clear existing items except the first empty one
        while self.class_input.count() > 0:
            self.class_input.removeItem(0)
        while self.section_input.count() > 0:
            self.section_input.removeItem(0)

        # Load predefined classes
        self.class_input.addItem("")  # Empty option
        for class_name in self.db.get_class_names():
            self.class_input.addItem(class_name)

        # Load predefined sections
        self.section_input.addItem("")  # Empty option
        for section_name in self.db.get_section_names():
            self.section_input.addItem(section_name)

    def load_activities(self):
        """Load activities into list"""
        self.activities_list.clear()
        activities = self.db.get_all_activities()
        
        for activity in activities:
            # Use pre-calculated count from DB query if available, otherwise fallback
            videos_count = activity.get('videos_count', 0)
            item_text = f"{activity['name']} ({videos_count} videos)"
            self.activities_list.addItem(item_text)
            
            # Handle class color
            class_color = activity.get('class_color')
            if class_color:
                # Create a colored icon
                pixmap = QPixmap(12, 12)
                pixmap.fill(QColor(class_color))
                icon = QIcon(pixmap)
                self.activities_list.item(self.activities_list.count() - 1).setIcon(icon)

            self.activities_list.item(self.activities_list.count() - 1).setData(
                Qt.ItemDataRole.UserRole, activity['id']
            )
    
    def activity_selected(self, item):
        """Handle activity selection"""
        self.selected_activity_id = item.data(Qt.ItemDataRole.UserRole)
        activity = self.db.get_activity_by_id(self.selected_activity_id)

        if activity:
            self.name_input.setText(activity['name'])
            self.class_input.setCurrentText(activity.get('class', ''))
            self.section_input.setCurrentText(activity.get('section', ''))
            self.description_input.setText(activity.get('description', ''))
            self.update_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
    
    def add_activity(self):
        """Add new activity"""
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter an activity name")
            return

        description = self.description_input.toPlainText().strip()
        class_name = self.class_input.currentText().strip()
        section = self.section_input.currentText().strip()

        activity_id = self.db.add_activity(name, description, class_name, section)

        if activity_id > 0:
            QMessageBox.information(self, "Success", f"Activity '{name}' added successfully")
            self.load_activities()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", f"Activity '{name}' already exists")
    
    def update_activity(self):
        """Update selected activity"""
        if not self.selected_activity_id:
            return

        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter an activity name")
            return

        description = self.description_input.toPlainText().strip()
        class_name = self.class_input.currentText().strip()
        section = self.section_input.currentText().strip()

        if self.db.update_activity(self.selected_activity_id, name, description, class_name, section):
            QMessageBox.information(self, "Success", "Activity updated successfully")
            self.load_activities()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", "Failed to update activity or name already exists")
    
    def delete_activity(self):
        """Delete selected activity"""
        if not self.selected_activity_id:
            return
        
        activity = self.db.get_activity_by_id(self.selected_activity_id)
        if not activity:
            return
        
        videos_count = len(self.db.get_videos_by_activity(self.selected_activity_id))
        
        msg = f"Are you sure you want to delete activity '{activity['name']}'?"
        if videos_count > 0:
            msg += f"\n\nThis will also delete {videos_count} associated video(s)!"
        
        reply = QMessageBox.question(
            self, 
            "Confirm Delete",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_activity(self.selected_activity_id):
                QMessageBox.information(self, "Success", "Activity deleted successfully")
                self.load_activities()
                self.clear_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete activity")
    
    def clear_form(self):
        """Clear form inputs"""
        self.name_input.clear()
        self.class_input.setCurrentIndex(0)
        self.section_input.setCurrentIndex(0)
        self.description_input.clear()
        self.selected_activity_id = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.activities_list.clearSelection()

    def open_class_manager(self):
        """Open class manager dialog"""
        from ui.class_manager import ClassManagerDialog
        dialog = ClassManagerDialog(self, self.db)
        if dialog.exec():
            self.load_filter_options()

    def open_section_manager(self):
        """Open section manager dialog"""
        from ui.section_manager import SectionManagerDialog
        dialog = SectionManagerDialog(self, self.db)
        if dialog.exec():
            self.load_filter_options()
