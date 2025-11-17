"""
Advanced Search Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QComboBox, QDateEdit, QCheckBox,
                             QMessageBox, QFrame, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QDate


class AdvancedSearchDialog(QDialog):
    """Dialog for advanced video search with multiple filters"""

    def __init__(self, parent, db, current_class="", current_section=""):
        super().__init__(parent)
        self.db = db
        self.current_class = current_class
        self.current_section = current_section

        self.setWindowTitle("Advanced Search")
        self.setModal(True)
        self.resize(650, 500)

        self.init_ui()
        self.load_filter_options()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Advanced Video Search")
        title.setStyleSheet("font-weight: bold; font-size: 18px; margin-bottom: 10px;")
        layout.addWidget(title)

        # Search term
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Term:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Title, description, tags, or activity name...")
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Create filter groups
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.Shape.Box)
        filter_layout = QVBoxLayout(filter_frame)

        filter_title = QLabel("Filters:")
        filter_title.setStyleSheet("font-weight: bold; margin-top: 5px;")
        filter_layout.addWidget(filter_title)

        # Basic filters
        basic_group = QGroupBox("Basic Filters")
        basic_layout = QGridLayout(basic_group)

        # Class and Section
        basic_layout.addWidget(QLabel("Class:"), 0, 0)
        self.class_combo = QComboBox()
        basic_layout.addWidget(self.class_combo, 0, 1)

        basic_layout.addWidget(QLabel("Section:"), 0, 2)
        self.section_combo = QComboBox()
        basic_layout.addWidget(self.section_combo, 0, 3)

        # Format
        basic_layout.addWidget(QLabel("Format:"), 1, 0)
        self.format_combo = QComboBox()
        basic_layout.addWidget(self.format_combo, 1, 1)

        # Version and Status
        basic_layout.addWidget(QLabel("Min Version:"), 1, 2)
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("1")
        self.version_input.setMaximumWidth(80)
        basic_layout.addWidget(self.version_input, 1, 3)

        # Status filter
        basic_layout.addWidget(QLabel("Status:"), 2, 2)
        self.status_combo = QComboBox()
        self.status_combo.addItem("All", "")
        self.status_combo.addItem("ACTIVE", "ACTIVE")
        self.status_combo.addItem("DRAFT", "DRAFT")
        self.status_combo.addItem("ARCHIVED", "ARCHIVED")
        basic_layout.addWidget(self.status_combo, 2, 3)

        # Tags
        basic_layout.addWidget(QLabel("Tags:"), 2, 0)
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Comma-separated (sports, annual, 2024)")
        basic_layout.addWidget(self.tags_input, 2, 1, 1, 3)

        filter_layout.addWidget(basic_group)

        # Date filters
        date_group = QGroupBox("Date Range (Upload Date)")
        date_layout = QHBoxLayout(date_group)

        date_layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        # Set to 30 days ago
        from_date = QDate.currentDate().addDays(-30)
        self.date_from.setDate(from_date)
        date_layout.addWidget(self.date_from)

        date_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_to)

        self.date_enabled = QCheckBox("Enable date filter")
        self.date_enabled.setChecked(True)
        self.date_enabled.toggled.connect(lambda checked: self.toggle_date_controls(checked))
        date_layout.addWidget(self.date_enabled)

        date_layout.addStretch()
        filter_layout.addWidget(date_group)

        # Size filters
        size_group = QGroupBox("File Size (MB)")
        size_layout = QHBoxLayout(size_group)

        size_layout.addWidget(QLabel("Min:"))
        self.size_min = QLineEdit()
        self.size_min.setPlaceholderText("0")
        self.size_min.setMaximumWidth(80)
        size_layout.addWidget(self.size_min)

        size_layout.addWidget(QLabel("Max:"))
        self.size_max = QLineEdit()
        self.size_max.setPlaceholderText("1000")
        self.size_max.setMaximumWidth(80)
        size_layout.addWidget(self.size_max)

        self.size_enabled = QCheckBox("Enable size filter")
        self.size_enabled.setChecked(False)
        self.size_enabled.toggled.connect(lambda checked: self.toggle_size_controls(checked))
        size_layout.addWidget(self.size_enabled)

        size_layout.addStretch()
        filter_layout.addWidget(size_group)

        # Duration filters
        duration_group = QGroupBox("Duration (minutes)")
        duration_layout = QHBoxLayout(duration_group)

        duration_layout.addWidget(QLabel("Min:"))
        self.duration_min = QLineEdit()
        self.duration_min.setPlaceholderText("0")
        self.duration_min.setMaximumWidth(80)
        duration_layout.addWidget(self.duration_min)

        duration_layout.addWidget(QLabel("Max:"))
        self.duration_max = QLineEdit()
        self.duration_max.setPlaceholderText("120")
        self.duration_max.setMaximumWidth(80)
        duration_layout.addWidget(self.duration_max)

        self.duration_enabled = QCheckBox("Enable duration filter")
        self.duration_enabled.setChecked(False)
        self.duration_enabled.toggled.connect(lambda checked: self.toggle_duration_controls(checked))
        duration_layout.addWidget(self.duration_enabled)

        duration_layout.addStretch()
        filter_layout.addWidget(duration_group)

        # Availability filters
        avail_group = QGroupBox("Availability")
        avail_layout = QHBoxLayout(avail_group)

        self.has_local_check = QCheckBox("Must have local copy")
        avail_layout.addWidget(self.has_local_check)

        self.has_youtube_check = QCheckBox("Must have YouTube link")
        avail_layout.addWidget(self.has_youtube_check)

        self.either_check = QCheckBox("Either available")
        self.either_check.setChecked(True)
        avail_layout.addWidget(self.either_check)

        avail_layout.addStretch()
        filter_layout.addWidget(avail_group)

        layout.addWidget(filter_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.search_btn)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_filters)
        btn_layout.addWidget(self.clear_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # Initialize controls
        self.toggle_date_controls(True)
        self.toggle_size_controls(False)
        self.toggle_duration_controls(False)

    def load_filter_options(self):
        """Load filter options from database"""
        # Classes - use predefined classes from dedicated table
        classes = self.db.get_class_names()
        self.class_combo.addItem("All", "")
        for class_name in classes:
            self.class_combo.addItem(class_name, class_name)

        # Set current class if provided
        if self.current_class and self.current_class != "All":
            index = self.class_combo.findText(self.current_class)
            if index >= 0:
                self.class_combo.setCurrentIndex(index)

        # Sections - use predefined sections from dedicated table
        sections = self.db.get_section_names()
        self.section_combo.addItem("All", "")
        for section_name in sections:
            self.section_combo.addItem(section_name, section_name)

        # Set current section if provided
        if self.current_section and self.current_section != "All":
            index = self.section_combo.findText(self.current_section)
            if index >= 0:
                self.section_combo.setCurrentIndex(index)

        # Formats
        formats = self.db.get_unique_formats()
        self.format_combo.addItem("All", "")
        for fmt in formats:
            self.format_combo.addItem(fmt, fmt)

    def toggle_date_controls(self, enabled):
        """Toggle date input controls"""
        self.date_from.setEnabled(enabled)
        self.date_to.setEnabled(enabled)

    def toggle_size_controls(self, enabled):
        """Toggle size input controls"""
        self.size_min.setEnabled(enabled)
        self.size_max.setEnabled(enabled)

    def toggle_duration_controls(self, enabled):
        """Toggle duration input controls"""
        self.duration_min.setEnabled(enabled)
        self.duration_max.setEnabled(enabled)

    def clear_filters(self):
        """Clear all filter inputs"""
        self.search_input.clear()
        self.class_combo.setCurrentIndex(0)
        self.section_combo.setCurrentIndex(0)
        self.format_combo.setCurrentIndex(0)
        self.version_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.tags_input.clear()
        self.size_min.clear()
        self.size_max.clear()
        self.duration_min.clear()
        self.duration_max.clear()
        self.has_local_check.setChecked(False)
        self.has_youtube_check.setChecked(False)
        self.either_check.setChecked(True)
        self.date_enabled.setChecked(True)
        self.size_enabled.setChecked(False)
        self.duration_enabled.setChecked(False)

    def get_search_criteria(self):
        """Get search criteria from dialog inputs"""
        criteria = {
            'search_term': self.search_input.text().strip(),
            'class_filter': self.class_combo.currentData() or "",
            'section_filter': self.section_combo.currentData() or "",
            'date_from': self.date_from.date().toString("yyyy-MM-dd") if self.date_enabled.isChecked() else "",
            'date_to': self.date_to.date().toString("yyyy-MM-dd") if self.date_enabled.isChecked() else "",
            'format_filter': self.format_combo.currentData() or "",
            'tags': self.tags_input.text().strip(),
            'version_min': 0,
            'status_filter': self.status_combo.currentData() or "",
            'size_min': 0,
            'size_max': 0,
            'duration_min': 0,
            'duration_max': 0,
            'has_local': None,
            'has_youtube': None
        }

        # Version
        try:
            criteria['version_min'] = int(self.version_input.text()) if self.version_input.text() else 0
        except ValueError:
            criteria['version_min'] = 0

        # Size filters (convert MB to bytes)
        if self.size_enabled.isChecked():
            try:
                criteria['size_min'] = int(float(self.size_min.text()) * 1024 * 1024) if self.size_min.text() else 0
                criteria['size_max'] = int(float(self.size_max.text()) * 1024 * 1024) if self.size_max.text() else 0
            except ValueError:
                criteria['size_min'] = 0
                criteria['size_max'] = 0

        # Duration filters (convert minutes to seconds)
        if self.duration_enabled.isChecked():
            try:
                criteria['duration_min'] = int(float(self.duration_min.text()) * 60) if self.duration_min.text() else 0
                criteria['duration_max'] = int(float(self.duration_max.text()) * 60) if self.duration_max.text() else 0
            except ValueError:
                criteria['duration_min'] = 0
                criteria['duration_max'] = 0

        # Availability filters
        if self.has_local_check.isChecked():
            criteria['has_local'] = True
        elif self.has_youtube_check.isChecked():
            criteria['has_youtube'] = True
        # If either_check is True and neither specific check is checked, show all

        return criteria
