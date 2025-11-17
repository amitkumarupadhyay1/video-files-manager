"""
Version Timeline Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QListWidgetItem, QTextEdit,
                             QSplitter, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os

from utils.file_manager import FileManager


class VersionTimelineDialog(QDialog):
    """Dialog for viewing version timeline of a video"""

    def __init__(self, parent, db, file_manager, activity_id, video_title):
        super().__init__(parent)
        self.db = db
        self.file_manager = file_manager
        self.activity_id = activity_id
        self.video_title = video_title
        self.versions = []

        self.setWindowTitle(f"Version Timeline - {video_title}")
        self.setModal(True)
        self.resize(800, 600)

        self.init_ui()
        self.load_versions()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(f"Version Timeline: {self.video_title}")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Version list
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Version details
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 500])
        layout.addWidget(splitter)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def create_left_panel(self):
        """Create left panel with version list"""
        panel = QGroupBox("Versions")
        layout = QVBoxLayout(panel)

        self.version_list = QListWidget()
        self.version_list.itemClicked.connect(self.version_selected)
        layout.addWidget(self.version_list)

        # Version count label
        self.version_count_label = QLabel("Loading...")
        self.version_count_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.version_count_label)

        return panel

    def create_right_panel(self):
        """Create right panel with version details"""
        panel = QGroupBox("Version Details")
        layout = QVBoxLayout(panel)

        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedHeight(150)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.thumbnail_label.setText("Select a version")
        layout.addWidget(self.thumbnail_label)

        # Details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)

        return panel

    def load_versions(self):
        """Load all versions of the video"""
        self.versions = self.db.get_video_versions(self.activity_id, self.video_title)

        if not self.versions:
            self.version_list.addItem("No versions found")
            self.version_count_label.setText("0 versions")
            return

        # Sort versions by upload date (chronological)
        self.versions.sort(key=lambda v: v['upload_date'])

        for i, version in enumerate(self.versions):
            # Create item text with version info
            status = version.get('version_status', 'ACTIVE')
            if status == 'ACTIVE':
                status_icon = '✅'
            elif status == 'DRAFT':
                status_icon = '📝'
            else:
                status_icon = '🗃️'

            item_text = f"{status_icon} v{version['version_number']} - {version['upload_date'][:10]}"

            # Add notes indicator if notes exist
            if version.get('version_notes', '').strip():
                item_text += " 📝"  # Notes indicator

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store version index
            self.version_list.addItem(item)

        self.version_count_label.setText(f"{len(self.versions)} versions")

        # Select the latest version
        if self.versions:
            self.version_list.setCurrentRow(len(self.versions) - 1)
            self.version_selected(self.version_list.item(len(self.versions) - 1))

    def version_selected(self, item):
        """Handle version selection"""
        if not item:
            return

        version_index = item.data(Qt.ItemDataRole.UserRole)
        if version_index >= len(self.versions):
            return

        version = self.versions[version_index]

        # Get status display
        status = version.get('version_status', 'ACTIVE')
        if status == 'ACTIVE':
            status_display = "✅ ACTIVE"
        elif status == 'DRAFT':
            status_display = "📝 DRAFT"
        else:
            status_display = "🗃️ ARCHIVED"

        # Load thumbnail
        thumbnail_path = version.get('thumbnail_path')
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
            scaled_pixmap = pixmap.scaled(300, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            self.thumbnail_label.setPixmap(scaled_pixmap)
        else:
            self.thumbnail_label.clear()
            self.thumbnail_label.setPixmap(QPixmap())  # Clear pixmap
            self.thumbnail_label.setText("No thumbnail")

        # Display details
        details_html = f"""
        <h3>Version {version['version_number']} ({status_display})</h3>
        <p><strong>Upload Date:</strong> {version['upload_date'][:19]}</p>
        <p><strong>Event Date:</strong> {version.get('event_date', 'N/A')}</p>
        <p><strong>Duration:</strong> {FileManager.format_duration(version.get('duration', 0))}</p>
        <p><strong>Resolution:</strong> {version.get('resolution', 'N/A')}</p>
        <p><strong>Format:</strong> {version.get('format', 'N/A')}</p>
        <p><strong>Size:</strong> {FileManager.format_file_size(version.get('file_size', 0))}</p>
        <p><strong>Description:</strong><br>{version.get('description', 'No description')}</p>
        <p><strong>Tags:</strong> {version.get('tags', 'No tags')}</p>
        <p><strong>YouTube Link:</strong> {'Yes' if version.get('has_youtube_link') else 'No'}</p>
        <p><strong>Local Copy:</strong> {'Yes' if version.get('has_local_copy') else 'No'}</p>
        """

        # Add version notes if they exist
        version_notes = version.get('version_notes', '').strip()
        if version_notes:
            details_html += f"<p><strong>Version Notes:</strong><br>{version_notes}</p>"

        self.details_text.setHtml(details_html)
