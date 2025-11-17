"""
Add Video Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
                             QMessageBox, QFileDialog, QProgressBar, QCheckBox)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUPPORTED_VIDEO_FORMATS, SUPPORTED_DOCUMENT_FORMATS


class VideoProcessThread(QThread):
    """Thread for processing video file"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, dict, str)
    
    def __init__(self, file_manager, source_path, activity_name, title):
        super().__init__()
        self.file_manager = file_manager
        self.source_path = source_path
        self.activity_name = activity_name
        self.title = title
    
    def run(self):
        try:
            # Copy file
            self.progress.emit("Copying video file...")
            success, dest_path, error = self.file_manager.copy_video_file(
                self.source_path, self.activity_name, self.title
            )

            if not success:
                self.finished.emit(False, {}, error)
                return

            # Validate video file
            self.progress.emit("Validating video file...")
            is_valid = self.file_manager.validate_video_file(dest_path)

            if not is_valid:
                # File is not a valid video, save with basic metadata
                self.progress.emit("File appears to be invalid - saving basic information only")
                metadata = {
                    'file_path': dest_path,
                    'file_name': os.path.basename(dest_path),
                    'file_size': self.file_manager.get_file_size(dest_path),
                    'duration': 0,
                    'resolution': 'Invalid file',
                    'format': 'Unknown',
                    'fps': 0
                }
                self.finished.emit(True, metadata, "")
                return

            # Extract metadata
            self.progress.emit("Extracting video metadata...")
            metadata = self.file_manager.get_video_metadata(dest_path)
            metadata['file_path'] = dest_path
            metadata['file_name'] = os.path.basename(dest_path)
            metadata['file_size'] = self.file_manager.get_file_size(dest_path)

            self.finished.emit(True, metadata, "")
            
        except Exception as e:
            self.finished.emit(False, {}, str(e))


class AddVideoDialog(QDialog):
    """Dialog for adding new videos"""
    
    def __init__(self, parent, db, file_manager):
        super().__init__(parent)
        self.db = db
        self.file_manager = file_manager
        self.video_file_path = None
        self.document_file_path = None
        self.video_metadata = {}
        self.process_thread = None
        
        self.setWindowTitle("Add New Video")
        self.setModal(True)
        self.resize(700, 650)
        
        self.init_ui()
        self.load_filter_options()
        self.load_activities()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Add New Video")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        # Activity selection
        activity_layout = QHBoxLayout()
        activity_layout.addWidget(QLabel("Activity:*"))
        self.activity_combo = QComboBox()
        activity_layout.addWidget(self.activity_combo, 1)
        add_activity_btn = QPushButton("+")
        add_activity_btn.setMaximumWidth(40)
        add_activity_btn.setToolTip("Add new activity")
        add_activity_btn.clicked.connect(self.quick_add_activity)
        activity_layout.addWidget(add_activity_btn)
        layout.addLayout(activity_layout)
        
        # Class and Section
        class_section_layout = QHBoxLayout()

        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Class:"))
        self.class_combo = QComboBox()
        self.class_combo.setEditable(False)  # Only predefined classes allowed
        self.class_combo.currentTextChanged.connect(self.on_class_changed)
        class_layout.addWidget(self.class_combo)

        add_class_btn = QPushButton("+")
        add_class_btn.setMaximumWidth(30)
        add_class_btn.setToolTip("Add new class")
        add_class_btn.clicked.connect(self.open_class_manager)
        class_layout.addWidget(add_class_btn)
        class_section_layout.addLayout(class_layout)

        section_layout = QHBoxLayout()
        section_layout.addWidget(QLabel("Section:"))
        self.section_combo = QComboBox()
        self.section_combo.setEditable(False)  # Only predefined sections allowed
        section_layout.addWidget(self.section_combo)

        add_section_btn = QPushButton("+")
        add_section_btn.setMaximumWidth(30)
        add_section_btn.setToolTip("Add new section")
        add_section_btn.clicked.connect(self.open_section_manager)
        section_layout.addWidget(add_section_btn)
        class_section_layout.addLayout(section_layout)
        
        layout.addLayout(class_section_layout)
        
        # Video title
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Video Title:*"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter video title...")
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)
        
        # Event date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Event Date:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.date_input)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Video file upload
        file_section = QLabel("Video File (Optional):")
        file_section.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(file_section)
        
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("color: #666; padding: 5px; border: 1px solid #ccc;")
        file_layout.addWidget(self.file_path_label, 1)
        
        browse_btn = QPushButton("📁 Browse...")
        browse_btn.clicked.connect(self.browse_video_file)
        file_layout.addWidget(browse_btn)
        
        clear_file_btn = QPushButton("✖")
        clear_file_btn.setMaximumWidth(40)
        clear_file_btn.setToolTip("Clear selected file")
        clear_file_btn.clicked.connect(self.clear_video_file)
        file_layout.addWidget(clear_file_btn)
        
        layout.addLayout(file_layout)

        # Document file upload
        doc_section = QLabel("Description Document (Optional):")
        doc_section.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(doc_section)

        doc_layout = QHBoxLayout()
        self.doc_path_label = QLabel("No document selected")
        self.doc_path_label.setStyleSheet("color: #666; padding: 5px; border: 1px solid #ccc;")
        doc_layout.addWidget(self.doc_path_label, 1)

        browse_doc_btn = QPushButton("📄 Browse...")
        browse_doc_btn.clicked.connect(self.browse_document_file)
        doc_layout.addWidget(browse_doc_btn)

        clear_doc_btn = QPushButton("✖")
        clear_doc_btn.setMaximumWidth(40)
        clear_doc_btn.setToolTip("Clear selected document")
        clear_doc_btn.clicked.connect(self.clear_document_file)
        doc_layout.addWidget(clear_doc_btn)

        layout.addLayout(doc_layout)

        # YouTube URL
        youtube_section = QLabel("YouTube Link (Optional):")
        youtube_section.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(youtube_section)
        
        youtube_layout = QHBoxLayout()
        youtube_layout.addWidget(QLabel("URL:"))
        self.youtube_input = QLineEdit()
        self.youtube_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        youtube_layout.addWidget(self.youtube_input)
        layout.addLayout(youtube_layout)
        
        # Note
        note = QLabel("Note: You must provide either a video file or YouTube link (or both)")
        note.setStyleSheet("color: #0066cc; font-style: italic; font-size: 11px;")
        layout.addWidget(note)
        
        # Description
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter video description...")
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)
        
        # Tags
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("Tags:"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Comma-separated tags (e.g., sports, annual, 2024)")
        tags_layout.addWidget(self.tags_input)
        layout.addLayout(tags_layout)
        
        # Version number
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("Auto")
        self.version_input.setMaximumWidth(100)
        self.version_input.setToolTip("Leave blank for auto-increment")
        version_layout.addWidget(self.version_input)

        self.auto_version_check = QCheckBox("Auto-increment version")
        self.auto_version_check.setChecked(True)
        self.auto_version_check.toggled.connect(lambda checked: self.version_input.setEnabled(not checked))
        self.version_input.setEnabled(False)
        version_layout.addWidget(self.auto_version_check)
        version_layout.addStretch()
        layout.addLayout(version_layout)

        # Version hint label
        self.version_hint = QLabel("")
        self.version_hint.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        layout.addWidget(self.version_hint)

        # Version status and notes
        version_extra_layout = QHBoxLayout()

        # Status
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.version_status_combo = QComboBox()
        self.version_status_combo.addItems(["ACTIVE", "DRAFT", "ARCHIVED"])
        self.version_status_combo.setCurrentText("ACTIVE")
        status_layout.addWidget(self.version_status_combo)
        version_extra_layout.addLayout(status_layout)

        # Notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Version Notes:"))
        self.version_notes_input = QTextEdit()
        self.version_notes_input.setPlaceholderText("Describe changes in this version...")
        self.version_notes_input.setMaximumHeight(60)
        notes_layout.addWidget(self.version_notes_input)
        version_extra_layout.addLayout(notes_layout)

        layout.addLayout(version_extra_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.progress_label.setStyleSheet("color: #0066cc;")
        layout.addWidget(self.progress_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Save Video")
        self.save_btn.clicked.connect(self.save_video)
        btn_layout.addWidget(self.save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)

        # Connect signals for version hint update
        self.activity_combo.currentTextChanged.connect(self.update_version_hint)
        self.title_input.textChanged.connect(self.update_version_hint)
        self.version_input.textChanged.connect(self.update_version_hint)

    def load_filter_options(self):
        """Load class and section filter options"""
        # Load predefined classes
        classes = self.db.get_class_names()
        self.class_combo.addItem("")  # Empty option
        for class_name in classes:
            self.class_combo.addItem(class_name)

        # Load predefined sections
        sections = self.db.get_section_names()
        self.section_combo.addItem("")  # Empty option
        for section_name in sections:
            self.section_combo.addItem(section_name)
    
    def on_class_changed(self, class_name):
        """Update section options when class changes"""
        if not class_name or class_name.strip() == "":
            # Load all sections
            self.section_combo.clear()
            self.section_combo.addItem("")
            sections = self.db.get_unique_sections()
            for section_name in sections:
                self.section_combo.addItem(section_name)
        else:
            # Load sections for this class
            self.section_combo.clear()
            self.section_combo.addItem("")
            sections = self.db.get_unique_sections_for_class(class_name)
            for section_name in sections:
                self.section_combo.addItem(section_name)
    
    def load_activities(self):
        """Load activities into combo box"""
        self.activity_combo.clear()
        
        # Get current class and section filters
        class_filter = self.class_combo.currentText().strip()
        section_filter = self.section_combo.currentText().strip()
        
        # Load filtered activities
        if class_filter or section_filter:
            activities = self.db.get_activities_filtered(class_filter, section_filter)
        else:
            activities = self.db.get_all_activities()
        
        if not activities:
            QMessageBox.information(
                self, 
                "No Activities", 
                "No activities found for the selected class/section. Please create an activity first."
            )
        
        for activity in activities:
            # Display with class/section info
            display_text = activity['name']
            if activity.get('class') and activity.get('section'):
                display_text = f"{activity['class']} - {activity['section']}: {activity['name']}"
            elif activity.get('class'):
                display_text = f"{activity['class']}: {activity['name']}"
            elif activity.get('section'):
                display_text = f"{activity['section']}: {activity['name']}"
            
            self.activity_combo.addItem(display_text, activity['id'])

        # Update version hint
        self.update_version_hint()
    
    def quick_add_activity(self):
        """Quick add activity with class and section"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Activity")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Activity name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Activity Name:*"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter activity name...")
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)
        
        # Class
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Class:"))
        class_input = QComboBox()
        class_input.setEditable(True)
        class_input.setPlaceholderText("Select or enter class...")
        class_input.addItem("")
        for class_name in self.db.get_unique_classes():
            class_input.addItem(class_name)
        # Pre-fill with current selection
        if self.class_combo.currentText():
            class_input.setCurrentText(self.class_combo.currentText())
        class_layout.addWidget(class_input)
        layout.addLayout(class_layout)
        
        # Section
        section_layout = QHBoxLayout()
        section_layout.addWidget(QLabel("Section:"))
        section_input = QComboBox()
        section_input.setEditable(True)
        section_input.setPlaceholderText("Select or enter section...")
        section_input.addItem("")
        for section_name in self.db.get_unique_sections():
            section_input.addItem(section_name)
        # Pre-fill with current selection
        if self.section_combo.currentText():
            section_input.setCurrentText(self.section_combo.currentText())
        section_layout.addWidget(section_input)
        layout.addLayout(section_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(add_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # Show dialog
        if dialog.exec():
            name = name_input.text().strip()
            class_name = class_input.currentText().strip()
            section_name = section_input.currentText().strip()
            
            if name:
                activity_id = self.db.add_activity(name, "", class_name, section_name)
                if activity_id > 0:
                    # Reload filter options
                    self.load_filter_options()
                    # Set the class and section
                    if class_name:
                        self.class_combo.setCurrentText(class_name)
                    if section_name:
                        self.section_combo.setCurrentText(section_name)
                    # Reload activities
                    self.load_activities()
                    # Select the newly added activity
                    for i in range(self.activity_combo.count()):
                        if self.activity_combo.itemData(i) == activity_id:
                            self.activity_combo.setCurrentIndex(i)
                            break
                else:
                    QMessageBox.warning(self, "Error", f"Activity '{name}' already exists")
            else:
                QMessageBox.warning(self, "Error", "Please enter an activity name")
    
    def browse_video_file(self):
        """Browse for video file"""
        file_filter = "Video Files (" + " ".join([f"*{ext}" for ext in SUPPORTED_VIDEO_FORMATS]) + ")"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            file_filter
        )
        
        if file_path:
            self.video_file_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            self.file_path_label.setStyleSheet("color: #000; padding: 5px; border: 1px solid #4CAF50; background-color: #e8f5e9;")
            
            # Auto-fill title if empty
            if not self.title_input.text():
                filename = os.path.splitext(os.path.basename(file_path))[0]
                self.title_input.setText(filename.replace('_', ' ').title())
    
    def clear_video_file(self):
        """Clear selected video file"""
        self.video_file_path = None
        self.file_path_label.setText("No file selected")
        self.file_path_label.setStyleSheet("color: #666; padding: 5px; border: 1px solid #ccc;")

    def browse_document_file(self):
        """Browse for document file"""
        file_filter = "Document Files (" + " ".join([f"*{ext}" for ext in SUPPORTED_DOCUMENT_FORMATS]) + ")"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document File",
            "",
            file_filter
        )

        if file_path:
            self.document_file_path = file_path
            self.doc_path_label.setText(os.path.basename(file_path))
            self.doc_path_label.setStyleSheet("color: #000; padding: 5px; border: 1px solid #4CAF50; background-color: #e8f5e9;")

    def clear_document_file(self):
        """Clear selected document file"""
        self.document_file_path = None
        self.doc_path_label.setText("No document selected")
        self.doc_path_label.setStyleSheet("color: #666; padding: 5px; border: 1px solid #ccc;")
    
    def update_version_hint(self):
        """Update the version hint based on current selections"""
        activity_id = self.activity_combo.currentData()
        title = self.title_input.text().strip()

        if activity_id and title:
            if self.auto_version_check.isChecked():
                # Get next version number
                next_version = self.db.get_next_version_number(activity_id, title)
                self.version_hint.setText(f"Will create version: {next_version}")
            else:
                # Show manual version
                try:
                    manual_version = int(self.version_input.text()) if self.version_input.text().strip() else 1
                except ValueError:
                    manual_version = 1
                self.version_hint.setText(f"Manual version: {manual_version}")
        else:
            self.version_hint.setText("Select activity and enter title to see version hint")

    def validate_inputs(self):
        """Validate form inputs"""
        if self.activity_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validation Error", "Please select an activity")
            return False
        
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a video title")
            return False
        
        # Must have either video file or YouTube link
        has_video = bool(self.video_file_path)
        has_youtube = bool(self.youtube_input.text().strip())
        
        if not has_video and not has_youtube:
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "Please provide either a video file or YouTube link (or both)"
            )
            return False
        
        # Validate YouTube URL if provided
        if has_youtube:
            youtube_url = self.youtube_input.text().strip()
            if not self.file_manager.validate_youtube_url(youtube_url):
                reply = QMessageBox.question(
                    self,
                    "Invalid URL",
                    "The YouTube URL doesn't appear to be valid. Continue anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return False
        
        return True
    
    def save_video(self):
        """Save video to database"""
        if not self.validate_inputs():
            return
        
        # Disable save button
        self.save_btn.setEnabled(False)
        
        # Get form values
        activity_id = self.activity_combo.currentData()
        activity_name = self.activity_combo.currentText()
        title = self.title_input.text().strip()
        event_date = self.date_input.date().toString("yyyy-MM-dd")
        description = self.description_input.toPlainText().strip()
        tags = self.tags_input.text().strip()
        youtube_url = self.youtube_input.text().strip()
        version_status = self.version_status_combo.currentText()
        version_notes = self.version_notes_input.toPlainText().strip()
        
        # Determine version number
        if self.auto_version_check.isChecked():
            version_number = self.db.get_next_version_number(activity_id, title)
        else:
            try:
                version_number = int(self.version_input.text()) if self.version_input.text() else 1
            except ValueError:
                version_number = 1
        
        # Process video file if provided
        if self.video_file_path:
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.progress_label.setVisible(True)
            
            # Start processing thread
            self.process_thread = VideoProcessThread(
                self.file_manager, 
                self.video_file_path, 
                activity_name,
                title
            )
            self.process_thread.progress.connect(self.update_progress)
            self.process_thread.finished.connect(
                lambda success, metadata, error: self.process_complete(
                    success, metadata, error, activity_id, title, event_date,
                    description, tags, youtube_url, version_number, version_status, version_notes
                )
            )
            self.process_thread.start()
        else:
        # No video file, just save metadata with YouTube link
            self.save_metadata(
                activity_id, title, event_date, description, tags,
                youtube_url, version_number, version_status, version_notes, {}, None
            )
    
    def update_progress(self, message):
        """Update progress label"""
        self.progress_label.setText(message)
    
    def process_complete(self, success, metadata, error, activity_id, title,
                        event_date, description, tags, youtube_url, version_number, version_status, version_notes):
        """Handle video processing completion"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        if not success:
            QMessageBox.critical(self, "Error", f"Failed to process video:\n{error}")
            self.save_btn.setEnabled(True)
            return

        # Generate thumbnail
        self.progress_label.setText("Generating thumbnail...")
        self.progress_label.setVisible(True)

        # Save to database first to get video ID
        video_id = self.save_metadata(
            activity_id, title, event_date, description, tags,
            youtube_url, version_number, version_status, version_notes, metadata, metadata.get('file_path')
        )

        if video_id:
            # Generate thumbnail
            thumbnail_path = self.file_manager.generate_thumbnail(
                metadata.get('file_path'), video_id
            )

            if thumbnail_path:
                # Update video with thumbnail path
                video_data = self.db.get_video_by_id(video_id)
                video_data['thumbnail_path'] = thumbnail_path
                self.db.update_video(video_id, video_data)

        self.progress_label.setVisible(False)

    def open_class_manager(self):
        """Open class manager dialog"""
        from ui.class_manager import ClassManagerDialog
        dialog = ClassManagerDialog(self, self.db)
        if dialog.exec():
            # Reload and refresh
            self.load_filter_options()
            # Refresh activities too as they may be affected
            self.load_activities()

    def open_section_manager(self):
        """Open section manager dialog"""
        from ui.section_manager import SectionManagerDialog
        dialog = SectionManagerDialog(self, self.db)
        if dialog.exec():
            # Reload and refresh
            self.load_filter_options()
            # Refresh activities too as they may be affected
            self.load_activities()

    def save_metadata(self, activity_id, title, event_date, description, tags,
                     youtube_url, version_number, version_status, version_notes, file_metadata, file_path):
        """Save video metadata to database"""
        # Save video to database first to get video ID
        video_data = {
            'activity_id': activity_id,
            'title': title,
            'event_date': event_date,
            'description': description,
            'tags': tags,
            'version_number': version_number,
            'version_status': version_status,
            'version_notes': version_notes,
            'youtube_url': youtube_url if youtube_url else None,
            'file_path': file_path,
            'file_name': file_metadata.get('file_name'),
            'file_size': file_metadata.get('file_size', 0),
            'duration': file_metadata.get('duration', 0),
            'format': file_metadata.get('format'),
            'resolution': file_metadata.get('resolution'),
            'thumbnail_path': None,
            'document_path': None,  # Will be updated below
            'has_local_copy': 1 if file_path else 0,
            'has_youtube_link': 1 if youtube_url else 0,
            'has_document': 0  # Will be updated below
        }

        video_id = self.db.add_video(video_data)

        if video_id > 0:
            # Process document file if provided
            if self.document_file_path:
                self.progress_label.setText("Copying document...")
                self.progress_label.setVisible(True)
                success, doc_dest_path, error = self.file_manager.copy_document_file(
                    self.document_file_path, video_id
                )
                if success:
                    # Update video with document path
                    video_data['document_path'] = doc_dest_path
                    video_data['has_document'] = 1
                    self.db.update_video(video_id, video_data)
                else:
                    QMessageBox.warning(self, "Document Copy Warning", f"Failed to copy document: {error}")
                    # Continue anyway, document is optional

            QMessageBox.information(self, "Success", "Video added successfully!")
            self.accept()
            return video_id
        else:
            QMessageBox.critical(self, "Error", "Failed to save video to database")
            self.save_btn.setEnabled(True)
            return None
