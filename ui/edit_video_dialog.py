"""
Edit Video Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
                             QMessageBox, QSpinBox)
from PyQt6.QtCore import Qt, QDate
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EditVideoDialog(QDialog):
    """Dialog for editing video metadata"""
    
    def __init__(self, parent, db, file_manager, video_id):
        super().__init__(parent)
        self.db = db
        self.file_manager = file_manager
        self.video_id = video_id
        self.video_data = None
        
        self.setWindowTitle("Edit Video Metadata")
        self.setModal(True)
        self.resize(600, 550)
        
        self.init_ui()
        self.load_video_data()
        self.load_activities()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Edit Video Metadata")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        # Activity selection
        activity_layout = QHBoxLayout()
        activity_layout.addWidget(QLabel("Activity:"))
        self.activity_combo = QComboBox()
        activity_layout.addWidget(self.activity_combo)
        layout.addLayout(activity_layout)
        
        # Class and Section (read-only display)
        class_section_layout = QHBoxLayout()
        class_section_layout.addWidget(QLabel("Class:"))
        self.class_label = QLabel("")
        self.class_label.setStyleSheet("color: #666; padding: 5px;")
        class_section_layout.addWidget(self.class_label)
        class_section_layout.addWidget(QLabel("Section:"))
        self.section_label = QLabel("")
        self.section_label.setStyleSheet("color: #666; padding: 5px;")
        class_section_layout.addWidget(self.section_label)
        class_section_layout.addStretch()
        layout.addLayout(class_section_layout)
        
        # Video title
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Video Title:*"))
        self.title_input = QLineEdit()
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)
        
        # Event date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Event Date:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.date_input)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Version number and status
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        self.version_input = QSpinBox()
        self.version_input.setMinimum(1)
        self.version_input.setMaximum(1000)
        version_layout.addWidget(self.version_input)

        version_layout.addWidget(QLabel("Status:"))
        self.version_status_combo = QComboBox()
        self.version_status_combo.addItems(["ACTIVE", "DRAFT", "ARCHIVED"])
        version_layout.addWidget(self.version_status_combo)
        version_layout.addStretch()
        layout.addLayout(version_layout)

        # Version notes
        notes_layout = QHBoxLayout()
        notes_layout.addWidget(QLabel("Version Notes:"))
        self.version_notes_input = QTextEdit()
        self.version_notes_input.setPlaceholderText("Describe changes in this version...")
        self.version_notes_input.setMaximumHeight(60)
        notes_layout.addWidget(self.version_notes_input)
        layout.addLayout(notes_layout)
        
        # YouTube URL
        youtube_layout = QHBoxLayout()
        youtube_layout.addWidget(QLabel("YouTube URL:"))
        self.youtube_input = QLineEdit()
        self.youtube_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        youtube_layout.addWidget(self.youtube_input)
        layout.addLayout(youtube_layout)
        
        # Description
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        layout.addWidget(self.description_input)
        
        # Tags
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("Tags:"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Comma-separated tags")
        tags_layout.addWidget(self.tags_input)
        layout.addLayout(tags_layout)
        
        # File info (read-only)
        info_section = QLabel("File Information (Read-only):")
        info_section.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(info_section)
        
        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        self.file_info_label.setWordWrap(True)
        layout.addWidget(self.file_info_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("💾 Save Changes")
        save_btn.clicked.connect(self.save_changes)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def load_activities(self):
        """Load activities into combo box"""
        self.activity_combo.clear()
        activities = self.db.get_all_activities()
        
        current_index = 0
        for i, activity in enumerate(activities):
            # Display with class/section info
            display_text = activity['name']
            if activity.get('class') and activity.get('section'):
                display_text = f"{activity['class']} - {activity['section']}: {activity['name']}"
            elif activity.get('class'):
                display_text = f"{activity['class']}: {activity['name']}"
            elif activity.get('section'):
                display_text = f"{activity['section']}: {activity['name']}"
            
            self.activity_combo.addItem(display_text, activity['id'])
            if self.video_data and activity['id'] == self.video_data['activity_id']:
                current_index = i
                # Update class and section labels
                self.class_label.setText(activity.get('class', 'N/A'))
                self.section_label.setText(activity.get('section', 'N/A'))
        
        self.activity_combo.setCurrentIndex(current_index)
        
        # Connect signal to update class/section when activity changes
        self.activity_combo.currentIndexChanged.connect(self.on_activity_changed)
    
    def on_activity_changed(self, index):
        """Update class and section labels when activity changes"""
        if index >= 0:
            activity_id = self.activity_combo.itemData(index)
            activity = self.db.get_activity_by_id(activity_id)
            if activity:
                self.class_label.setText(activity.get('class', 'N/A'))
                self.section_label.setText(activity.get('section', 'N/A'))
    
    def load_video_data(self):
        """Load video data into form"""
        self.video_data = self.db.get_video_by_id(self.video_id)
        
        if not self.video_data:
            QMessageBox.warning(self, "Error", "Video not found")
            self.reject()
            return
        
        # Fill form fields
        self.title_input.setText(self.video_data.get('title', ''))
        
        # Event date
        if self.video_data.get('event_date'):
            try:
                date = QDate.fromString(self.video_data['event_date'], "yyyy-MM-dd")
                self.date_input.setDate(date)
            except:
                self.date_input.setDate(QDate.currentDate())
        else:
            self.date_input.setDate(QDate.currentDate())
        
        self.version_input.setValue(self.video_data.get('version_number', 1))
        self.version_status_combo.setCurrentText(self.video_data.get('version_status', 'ACTIVE'))
        self.version_notes_input.setText(self.video_data.get('version_notes', '') or '')
        self.youtube_input.setText(self.video_data.get('youtube_url', '') or '')
        self.description_input.setText(self.video_data.get('description', '') or '')
        self.tags_input.setText(self.video_data.get('tags', '') or '')
        
        # Display file info
        file_info_parts = []
        
        if self.video_data.get('has_local_copy') and self.video_data.get('file_path'):
            file_info_parts.append(f"📁 Local File: {self.video_data['file_name']}")
            file_info_parts.append(f"Size: {self.file_manager.format_file_size(self.video_data.get('file_size', 0))}")
            file_info_parts.append(f"Duration: {self.file_manager.format_duration(self.video_data.get('duration', 0))}")
            file_info_parts.append(f"Resolution: {self.video_data.get('resolution', 'N/A')}")
            file_info_parts.append(f"Format: {self.video_data.get('format', 'N/A')}")
        else:
            file_info_parts.append("No local file attached")
        
        self.file_info_label.setText("\n".join(file_info_parts))
    
    def save_changes(self):
        """Save changes to database"""
        # Validate title
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a video title")
            return
        
        # Get YouTube URL
        youtube_url = self.youtube_input.text().strip()
        has_youtube = bool(youtube_url)
        
        # Validate YouTube URL if provided
        if has_youtube and not self.file_manager.validate_youtube_url(youtube_url):
            reply = QMessageBox.question(
                self,
                "Invalid URL",
                "The YouTube URL doesn't appear to be valid. Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Prepare updated data
        updated_data = {
            'title': self.title_input.text().strip(),
            'file_path': self.video_data.get('file_path'),
            'youtube_url': youtube_url if youtube_url else None,
            'file_name': self.video_data.get('file_name'),
            'file_size': self.video_data.get('file_size'),
            'duration': self.video_data.get('duration'),
            'format': self.video_data.get('format'),
            'resolution': self.video_data.get('resolution'),
            'version_number': self.version_input.value(),
            'version_status': self.version_status_combo.currentText(),
            'version_notes': self.version_notes_input.toPlainText().strip(),
            'event_date': self.date_input.date().toString("yyyy-MM-dd"),
            'description': self.description_input.toPlainText().strip(),
            'tags': self.tags_input.text().strip(),
            'thumbnail_path': self.video_data.get('thumbnail_path'),
            'document_path': self.video_data.get('document_path'),
            'has_local_copy': self.video_data.get('has_local_copy', 0),
            'has_youtube_link': 1 if has_youtube else 0,
            'has_document': self.video_data.get('has_document', 0)
        }
        
        if self.db.update_video(self.video_id, updated_data):
            QMessageBox.information(self, "Success", "Video updated successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update video")
