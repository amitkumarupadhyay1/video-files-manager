"""
Export Activities Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QComboBox, QCheckBox, QFileDialog, QProgressBar, QGroupBox,
                             QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os
import sys
import datetime
from typing import Dict, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from utils.file_manager import FileManager


class ExportActivitiesDialog(QDialog):
    """Dialog for exporting activities to HTML/PDF"""

    def __init__(self, parent, db, file_manager):
        super().__init__(parent)
        self.db = db
        self.file_manager = file_manager

        self.setWindowTitle("Export Activities")
        self.setModal(True)
        self.resize(600, 500)

        self.init_ui()
        self.load_activities()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Export Activities to HTML Report")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(title)

        # Activity selection
        activity_group = QGroupBox("Activity Selection")
        activity_layout = QVBoxLayout(activity_group)

        activity_layout.addWidget(QLabel("Select Activity to Export:"))
        self.activity_combo = QComboBox()
        self.activity_combo.addItem("All Activities", 0)
        activity_layout.addWidget(self.activity_combo)

        layout.addWidget(activity_group)

        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)

        self.include_thumbnails = QCheckBox("Include video thumbnails (increases file size)")
        self.include_thumbnails.setChecked(True)
        options_layout.addWidget(self.include_thumbnails)

        self.include_video_links = QCheckBox("Include video file links and YouTube URLs")
        self.include_video_links.setChecked(True)
        options_layout.addWidget(self.include_video_links)

        self.include_statistics = QCheckBox("Include activity statistics")
        self.include_statistics.setChecked(True)
        options_layout.addWidget(self.include_statistics)

        self.include_versions = QCheckBox("Include version history for each video")
        self.include_versions.setChecked(False)
        options_layout.addWidget(self.include_versions)

        layout.addWidget(options_group)

        # Output location
        output_group = QGroupBox("Output Location")
        output_layout = QHBoxLayout(output_group)

        self.output_path_edit = QTextEdit()
        self.output_path_edit.setMaximumHeight(60)
        self.output_path_edit.setPlaceholderText("Select output folder...")
        output_layout.addWidget(self.output_path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output_location)
        output_layout.addWidget(browse_btn)

        layout.addWidget(output_group)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.export_btn = QPushButton("📤 Export to HTML")
        self.export_btn.clicked.connect(self.start_export)
        self.export_btn.setDefault(True)
        btn_layout.addWidget(self.export_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # Set default output location
        self.set_default_output_location()

    def load_activities(self):
        """Load activities into combo box"""
        activities = self.db.get_all_activities()
        for activity in activities:
            display_text = f"{activity['name']}"
            if activity.get('class') or activity.get('section'):
                class_section = []
                if activity.get('class'):
                    class_section.append(activity['class'])
                if activity.get('section'):
                    class_section.append(activity['section'])
                display_text += f" ({' - '.join(class_section)})"
            display_text += f" - {activity['videos_count']} videos"

            self.activity_combo.addItem(display_text, activity['id'])

    def set_default_output_location(self):
        """Set default output location to user's Documents folder"""
        try:
            # Get user's Documents folder
            home_dir = os.path.expanduser("~")
            docs_dir = os.path.join(home_dir, "Documents")
            if os.path.exists(docs_dir):
                export_dir = os.path.join(docs_dir, "VideoManagement_Exports")
                os.makedirs(export_dir, exist_ok=True)
                self.output_path_edit.setPlainText(export_dir)
            else:
                # Fallback to Desktop
                desktop_dir = os.path.join(home_dir, "Desktop")
                if os.path.exists(desktop_dir):
                    export_dir = os.path.join(desktop_dir, "VideoManagement_Exports")
                    os.makedirs(export_dir, exist_ok=True)
                    self.output_path_edit.setPlainText(export_dir)
        except:
            # If all else fails, use current directory
            current_dir = os.getcwd()
            export_dir = os.path.join(current_dir, "exports")
            self.output_path_edit.setPlainText(export_dir)

    def browse_output_location(self):
        """Browse for output location"""
        current_path = self.output_path_edit.toPlainText().strip()

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            current_path if current_path and os.path.exists(current_path) else ""
        )

        if folder:
            # Create subfolder for exports
            export_dir = os.path.join(folder, "VideoManagement_Exports")
            try:
                os.makedirs(export_dir, exist_ok=True)
            except:
                export_dir = folder
            self.output_path_edit.setPlainText(export_dir)

    def start_export(self):
        """Start the export process"""
        output_path = self.output_path_edit.toPlainText().strip()
        if not output_path:
            QMessageBox.warning(self, "Error", "Please select an output location")
            return

        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot create output directory: {str(e)}")
                return

        # Disable controls during export
        self.export_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Get selected activity
        activity_id = self.activity_combo.currentData()
        selected_activity_name = self.activity_combo.currentText().split(" - ")[0] if activity_id else "All_Activities"

        # Start export thread
        self.export_thread = ExportThread(
            db=self.db,
            file_manager=self.file_manager,
            activity_id=activity_id if activity_id else None,
            output_path=output_path,
            activity_name=selected_activity_name,
            include_thumbnails=self.include_thumbnails.isChecked(),
            include_video_links=self.include_video_links.isChecked(),
            include_statistics=self.include_statistics.isChecked(),
            include_versions=self.include_versions.isChecked()
        )

        self.export_thread.progress.connect(self.update_progress)
        self.export_thread.finished.connect(self.export_completed)
        self.export_thread.error.connect(self.export_error)

        self.export_thread.start()

    def update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(message)

    def export_completed(self, output_file):
        """Handle successful export"""
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("Export completed")

        reply = QMessageBox.question(
            self,
            "Export Complete",
            f"Export completed successfully!\n\nOutput: {output_file}\n\nOpen the exported file now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.file_manager.open_document_file(output_file)

        self.accept()

    def export_error(self, error_message):
        """Handle export error"""
        QMessageBox.critical(self, "Export Error", f"An error occurred during export:\n\n{error_message}")
        self.export_btn.setEnabled(True)
        self.progress_bar.setVisible(False)


class ExportThread(QThread):
    """Thread for running export operations"""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, db, file_manager, activity_id, output_path, activity_name,
                 include_thumbnails, include_video_links, include_statistics, include_versions):
        super().__init__()
        self.db = db
        self.file_manager = file_manager
        self.activity_id = activity_id
        self.output_path = output_path
        self.activity_name = activity_name
        self.include_thumbnails = include_thumbnails
        self.include_video_links = include_video_links
        self.include_statistics = include_statistics
        self.include_versions = include_versions

    def run(self):
        """Run the export operation"""
        try:
            # Generate timestamp for filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Activity_Export_{self.activity_name}_{timestamp}.html"
            output_file = os.path.join(self.output_path, filename)

            self.progress.emit(10, "Gathering activity data...")

            # Get activities to export
            if self.activity_id:
                activities = [self.db.get_activity_by_id(self.activity_id)]
                activities = [a for a in activities if a]  # Filter out None
            else:
                activities = self.db.get_all_activities()

            self.progress.emit(30, "Generating HTML report...")

            # Generate HTML content
            html_content = self.generate_html(activities)

            self.progress.emit(80, "Writing export file...")

            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.progress.emit(100, "Export completed")
            self.finished.emit(output_file)

        except Exception as e:
            self.error.emit(str(e))

    def generate_html(self, activities):
        """Generate HTML report for activities"""

        # Generate timestamp
        now = datetime.datetime.now()
        export_datetime = now.strftime("%B %d, %Y at %I:%M %p")

        # Build activities data
        activities_data = []
        total_videos = 0
        total_size = 0

        for i, activity in enumerate(activities):
            self.progress.emit(40 + (i * 10), f"Processing {activity['name']}...")

            # Get videos for this activity
            videos = self.db.get_videos_by_activity(activity['id'])
            activity_data = {
                'activity': activity,
                'videos': videos,
                'video_count': len(videos),
                'total_size': sum(v.get('file_size', 0) for v in videos if v.get('has_local_copy'))
            }

            activities_data.append(activity_data)
            total_videos += len(videos)
            total_size += activity_data['total_size']

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Management Activity Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}

        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .summary {{
            background-color: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #dee2e6;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}

        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        .summary-card h3 {{
            font-size: 2em;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .summary-card p {{
            color: #6c757d;
            font-size: 0.9em;
        }}

        .activity {{
            padding: 30px;
            border-bottom: 1px solid #dee2e6;
        }}

        .activity:last-child {{
            border-bottom: none;
        }}

        .activity-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }}

        .activity-title {{
            font-size: 1.8em;
            color: #333;
            font-weight: 600;
        }}

        .activity-meta {{
            background-color: #e9ecef;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            color: #495057;
        }}

        .activity-description {{
            margin-bottom: 20px;
            font-style: italic;
            color: #6c757d;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }}

        .videos-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}

        .video-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .video-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }}

        .video-thumbnail {{
            width: 100%;
            height: 180px;
            background-color: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6c757d;
            font-size: 0.9em;
            position: relative;
        }}

        .video-thumbnail img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .video-status {{
            position: absolute;
            top: 8px;
            right: 8px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.75em;
        }}

        .video-content {{
            padding: 15px;
        }}

        .video-title {{
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .video-meta {{
            font-size: 0.85em;
            color: #6c757d;
            margin-bottom: 8px;
        }}

        .video-meta span {{
            display: inline-block;
            margin-right: 10px;
        }}

        .video-description {{
            font-size: 0.9em;
            color: #495057;
            margin-bottom: 10px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .video-links {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .video-link {{
            background-color: #007bff;
            color: white;
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.8em;
            display: inline-block;
            transition: background-color 0.2s;
        }}

        .video-link:hover {{
            background-color: #0056b3;
        }}

        .video-link.youtube {{
            background-color: #dc3545;
        }}

        .video-link.youtube:hover {{
            background-color: #c82333;
        }}

        .footer {{
            background-color: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}

        .no-videos {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-style: italic;
        }}

        @media (max-width: 768px) {{
            .videos-grid {{
                grid-template-columns: 1fr;
            }}

            .activity-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
        }}

        .version-info {{
            background-color: #fff3cd;
            padding: 8px 12px;
            border-radius: 4px;
            margin-top: 8px;
            font-size: 0.8em;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📹 Video Management Report</h1>
            <div class="subtitle">Activity and Video Documentation</div>
        </div>

        <div class="summary">
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>{len(activities)}</h3>
                    <p>Total Activities</p>
                </div>
                <div class="summary-card">
                    <h3>{total_videos}</h3>
                    <p>Total Videos</p>
                </div>
                <div class="summary-card">
                    <h3>{self.format_file_size(total_size)}</h3>
                    <p>Storage Used</p>
                </div>
                <div class="summary-card">
                    <h3>{export_datetime}</h3>
                    <p>Export Time</p>
                </div>
            </div>
        </div>"""

        # Add each activity
        for activity_data in activities_data:
            activity = activity_data['activity']
            videos = activity_data['videos']

            html += f"""
        <div class="activity">
            <div class="activity-header">
                <h2 class="activity-title">{activity['name']}</h2>
                <div class="activity-meta">
                    Videos: {activity_data['video_count']} |
                    Size: {self.format_file_size(activity_data['total_size'])}
                    {' | Class: ' + activity.get('class', '') if activity.get('class') else ''}
                    {' | Section: ' + activity.get('section', '') if activity.get('section') else ''}
                </div>
            </div>"""

            if activity.get('description'):
                html += f"""
            <div class="activity-description">
                {activity['description']}
            </div>"""

            if videos:
                html += """
            <div class="videos-grid">"""

                for video in videos:
                    # Get thumbnail
                    thumbnail_html = ""
                    if self.include_thumbnails and video.get('thumbnail_path') and os.path.exists(video['thumbnail_path']):
                        try:
                            import base64
                            with open(video['thumbnail_path'], 'rb') as img_file:
                                img_data = base64.b64encode(img_file.read()).decode()
                            thumbnail_html = f'<img src="data:image/jpeg;base64,{img_data}" alt="Thumbnail">'
                        except:
                            thumbnail_html = '<div style="display: flex; align-items: center; justify-content: center; height: 100%;">📷 No Preview</div>'
                    else:
                        thumbnail_html = '<div style="display: flex; align-items: center; justify-content: center; height: 100%;">📷 No Preview</div>'

                    # Version status
                    status_text = ""
                    if video.get('version_number', 1) > 1:
                        status = video.get('version_status', 'ACTIVE')
                        if status == 'ACTIVE':
                            status_text = "✅ ACTIVE"
                        elif status == 'DRAFT':
                            status_text = "📝 DRAFT"
                        else:
                            status_text = "🗃️ ARCHIVED"

                    html += f"""
                <div class="video-card">
                    <div class="video-thumbnail">
                        {thumbnail_html}
                        {'<div class="video-status">' + status_text + '</div>' if status_text else ''}
                    </div>
                    <div class="video-content">
                        <div class="video-title">{video['title']}</div>
                        <div class="video-meta">
                            <span>🎬 {FileManager.format_duration(video.get('duration', 0))}</span>
                            <span>📐 {video.get('resolution', 'N/A')}</span>
                            <span>📁 {self.format_file_size(video.get('file_size', 0))}</span>
                            <span>📅 {video.get('upload_date', 'N/A')[:10]}</span>
                        </div>
                        {'<div class="video-meta"><span>🎵 ' + video.get('format', 'N/A') + '</span><span>v' + str(video.get('version_number', 1)) + '</span></div>' if video.get('format') else ''}
                        {f'<div class="video-description">{video.get("description", "No description")}</div>' if video.get('description') else ''}
                        <div class="video-links">"""

                    if self.include_video_links:
                        if video.get('has_local_copy') and video.get('file_path'):
                            html += f'<a href="{video["file_path"]}" class="video-link">📁 Local File</a>'

                        if video.get('has_youtube_link') and video.get('youtube_url'):
                            html += f'<a href="{video["youtube_url"]}" class="video-link youtube" target="_blank">📺 YouTube</a>'

                    html += """
                        </div>"""

                    # Version notes if enabled
                    if self.include_versions and video.get('version_number', 1) > 1:
                        version_note = video.get('version_notes', '').strip()
                        if version_note:
                            html += f"""
                        <div class="version-info">
                            📝 Version Notes: {version_note}
                        </div>"""

                    html += """
                    </div>
                </div>"""

                html += """
            </div>"""
            else:
                html += """
            <div class="no-videos">
                🚫 No videos found for this activity
            </div>"""

            html += """
        </div>"""

        # Footer
        html += """
        <div class="footer">
            <p>
                📊 Generated by Video Management System<br>
                <small>This report was exported on {export_datetime}</small>
            </p>
        </div>
    </div>
</body>
</html>"""

        return html

    def format_file_size(self, bytes_size):
        """Format file size for display"""
        if not bytes_size:
            return "0 B"
        return FileManager.format_file_size(bytes_size)
