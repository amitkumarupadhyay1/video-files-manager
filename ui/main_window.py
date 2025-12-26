"""
Main window for Video Management Application
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QListWidget, QTableWidget,
                             QTableWidgetItem, QSplitter, QMessageBox, QHeaderView,
                             QMenu, QStatusBar, QToolBar, QGroupBox, QTextEdit, QComboBox,
                             QCompleter)
from PyQt6.QtCore import QStringListModel
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPixmap, QColor
import sys
import os
import math

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, ORGANIZATION, DEVELOPER
from database.db_manager import DatabaseManager
from utils.file_manager import FileManager
from utils.backup_manager import BackupManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.file_manager = FileManager()
        self.current_activity_id = None
        self.selected_video_id = None
        self.current_search_criteria = None  # Store advanced search criteria

        # Pagination state
        self.current_page = 1
        self.page_size = 50
        self.total_pages = 1
        self.total_videos = 0

        self.init_ui()
        self.load_filter_options()
        self.load_activities()
        self.load_videos()
        self.update_statistics()
        self.showMaximized()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"{APP_NAME} - v{APP_VERSION}")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create search bar and filters
        filter_layout = QHBoxLayout()

        # Search input
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search videos by title, description, tags, or activity...")
        self.search_input.textChanged.connect(self.search_videos)
        # Setup auto-complete
        self.setup_search_completer()
        filter_layout.addWidget(self.search_input)

        # Advanced search button
        self.advanced_search_btn = QPushButton("🔍 Advanced")
        self.advanced_search_btn.setToolTip("Open advanced search dialog")
        self.advanced_search_btn.clicked.connect(self.show_advanced_search)
        filter_layout.addWidget(self.advanced_search_btn)

        # Class filter
        filter_layout.addWidget(QLabel("Class:"))
        self.class_filter = QComboBox()
        self.class_filter.addItem("All", "")
        self.class_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.class_filter)

        # Section filter
        filter_layout.addWidget(QLabel("Section:"))
        self.section_filter = QComboBox()
        self.section_filter.addItem("All", "")
        self.section_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.section_filter)

        main_layout.addLayout(filter_layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Activities list
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Center panel - Videos table
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)
        
        # Right panel - Video details
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes
        splitter.setSizes([250, 600, 350])
        
        main_layout.addWidget(splitter)
        
        # Pagination Controls
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()
        
        self.first_page_btn = QPushButton("<< First")
        self.first_page_btn.clicked.connect(self.go_to_first_page)
        self.first_page_btn.setFixedWidth(80)
        pagination_layout.addWidget(self.first_page_btn)
        
        self.prev_page_btn = QPushButton("< Prev")
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.prev_page_btn.setFixedWidth(80)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setFixedWidth(120)
        pagination_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton("Next >")
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setFixedWidth(80)
        pagination_layout.addWidget(self.next_page_btn)
        
        self.last_page_btn = QPushButton("Last >>")
        self.last_page_btn.clicked.connect(self.go_to_last_page)
        self.last_page_btn.setFixedWidth(80)
        pagination_layout.addWidget(self.last_page_btn)
        
        pagination_layout.addStretch()
        main_layout.addLayout(pagination_layout)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.stats_label = QLabel("")
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.stats_label)
    
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add Video action
        add_video_action = QAction("➕ Add Video", self)
        add_video_action.triggered.connect(self.add_video)
        toolbar.addAction(add_video_action)
        
        toolbar.addSeparator()
        
        # Manage Activities action
        manage_activities_action = QAction("📁 Manage Activities", self)
        manage_activities_action.triggered.connect(self.manage_activities)
        toolbar.addAction(manage_activities_action)

        toolbar.addSeparator()

        # Manage Classes action
        manage_classes_action = QAction("🏫 Manage Classes", self)
        manage_classes_action.triggered.connect(self.manage_classes)
        toolbar.addAction(manage_classes_action)

        # Manage Sections action
        manage_sections_action = QAction("🏷️ Manage Sections", self)
        manage_sections_action.triggered.connect(self.manage_sections)
        toolbar.addAction(manage_sections_action)

        toolbar.addSeparator()
        
        # Refresh action
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self.refresh_all)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()

        # Collections action
        collections_action = QAction("� Collections", self)
        collections_action.triggered.connect(self.show_collections)
        toolbar.addAction(collections_action)

        toolbar.addSeparator()

        # Statistics action
        stats_action = QAction("📊 Statistics", self)
        stats_action.triggered.connect(self.show_statistics)
        toolbar.addAction(stats_action)
        
        toolbar.addSeparator()

        # Export action
        export_action = QAction("📤 Export", self)
        export_action.triggered.connect(self.export_activities)
        toolbar.addAction(export_action)

        toolbar.addSeparator()

        # Backup action
        backup_action = QAction("💾 Backup", self)
        backup_action.triggered.connect(self.create_backup)
        toolbar.addAction(backup_action)
        
        toolbar.addSeparator()

        # About action
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)

    def create_backup(self):
        """Create a manual backup of the database"""
        backup_manager = BackupManager()
        success, message = backup_manager.create_backup(manual=True)
        
        if success:
            QMessageBox.information(self, "Backup Successful", message)
        else:
            QMessageBox.warning(self, "Backup Failed", f"Could not create backup:\n{message}")
    
    def create_left_panel(self):
        """Create left panel with activities list"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Activities")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # All Videos button
        self.all_videos_btn = QPushButton("📹 All Videos")
        self.all_videos_btn.clicked.connect(self.show_all_videos)
        layout.addWidget(self.all_videos_btn)
        
        # Activities list
        self.activities_list = QListWidget()
        self.activities_list.itemClicked.connect(self.activity_selected)
        layout.addWidget(self.activities_list)
        
        # Add/Edit buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("+ Add")
        add_btn.clicked.connect(self.manage_activities)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)
        
        return panel
    
    def create_center_panel(self):
        """Create center panel with videos table"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        self.videos_title = QLabel("All Videos")
        self.videos_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.videos_title)
        
        # Videos table
        self.videos_table = QTableWidget()
        self.videos_table.setColumnCount(7)
        self.videos_table.setHorizontalHeaderLabels([
            "ID", "Title", "Activity", "Duration", "Size", "Version", "Availability"
        ])
        self.videos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.videos_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.videos_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.videos_table.setColumnHidden(0, True)  # Hide ID column
        self.videos_table.itemSelectionChanged.connect(self.video_selected)
        self.videos_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.videos_table.customContextMenuRequested.connect(self.show_video_context_menu)
        
        layout.addWidget(self.videos_table)
        
        return panel
    
    def create_right_panel(self):
        """Create right panel with video details"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Video Details")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedHeight(180)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.thumbnail_label.setText("No video selected")
        layout.addWidget(self.thumbnail_label)
        
        # Details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)
        
        # Playback buttons
        btn_group = QGroupBox("Playback Options")
        btn_layout = QVBoxLayout()
        
        self.play_local_btn = QPushButton("🎬 Play Local Copy")
        self.play_local_btn.clicked.connect(self.play_local_video)
        self.play_local_btn.setEnabled(False)
        btn_layout.addWidget(self.play_local_btn)
        
        self.play_youtube_btn = QPushButton("▶️ Play YouTube Link")
        self.play_youtube_btn.clicked.connect(self.play_youtube_video)
        self.play_youtube_btn.setEnabled(False)
        btn_layout.addWidget(self.play_youtube_btn)
        
        btn_group.setLayout(btn_layout)
        layout.addWidget(btn_group)
        
        # Action buttons
        action_layout = QVBoxLayout()

        self.edit_btn = QPushButton("✏️ Edit Metadata")
        self.edit_btn.clicked.connect(self.edit_video)
        self.edit_btn.setEnabled(False)
        action_layout.addWidget(self.edit_btn)

        self.view_doc_btn = QPushButton("📄 View Document")
        self.view_doc_btn.clicked.connect(self.view_document)
        self.view_doc_btn.setEnabled(False)
        self.view_doc_btn.setVisible(False)
        action_layout.addWidget(self.view_doc_btn)

        self.delete_btn = QPushButton("🗑️ Delete Video")
        self.delete_btn.clicked.connect(self.delete_video)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.delete_btn)

        layout.addLayout(action_layout)
        layout.addStretch()
        
        return panel
    
    def load_activities(self):
        """Load activities into the list"""
        self.activities_list.clear()
        activities = self.db.get_all_activities()

        for activity in activities:
            videos_count = activity.get('videos_count', 0)
            item_text = f"{activity['name']} ({videos_count})"
            self.activities_list.addItem(item_text)
            
            # Handle class color
            class_color = activity.get('class_color')
            if class_color:
                # Create a colored icon
                pixmap = QPixmap(12, 12)
                pixmap.fill(QColor(class_color))
                icon = QIcon(pixmap)
                self.activities_list.item(self.activities_list.count() - 1).setIcon(icon)

            # Store activity ID in item data
            self.activities_list.item(self.activities_list.count() - 1).setData(Qt.ItemDataRole.UserRole, activity['id'])
    
    def load_videos(self):
        """Fetch videos from DB based on current state with pagination"""
        offset = (self.current_page - 1) * self.page_size
        
        # Determine mode
        if self.current_activity_id:
             videos = self.db.get_videos_by_activity(self.current_activity_id, limit=self.page_size, offset=offset)
             self.total_videos = self.db.get_total_video_count(self.current_activity_id)
        elif self.current_search_criteria:
             # Advanced search
             c = self.current_search_criteria
             videos = self.db.search_videos(
                c.get('search_term', ''), c.get('class_filter', ''), c.get('section_filter', ''),
                c.get('date_from', ''), c.get('date_to', ''), c.get('format_filter', ''),
                c.get('tags', ''), c.get('size_min', 0), c.get('size_max', 0),
                c.get('duration_min', 0), c.get('duration_max', 0), c.get('version_min', 0),
                c.get('status_filter', ''), c.get('has_local'), c.get('has_youtube'),
                limit=self.page_size, offset=offset
             )
             self.total_videos = self.db.get_search_count(
                c.get('search_term', ''), c.get('class_filter', ''), c.get('section_filter', ''),
                c.get('date_from', ''), c.get('date_to', ''), c.get('format_filter', ''),
                c.get('tags', ''), c.get('size_min', 0), c.get('size_max', 0),
                c.get('duration_min', 0), c.get('duration_max', 0), c.get('version_min', 0),
                c.get('status_filter', ''), c.get('has_local'), c.get('has_youtube')
             )
        else:
             # Check simple search/filters
             search_term = self.search_input.text().strip()
             class_filter = self.class_filter.currentText()
             # Map "All" to "" (assuming "All" is empty string data, need to verify)
             # In load_filter_options, addItem("All", "") so currentData() is ""
             class_data = self.class_filter.currentData() or ""
             section_data = self.section_filter.currentData() or ""
             
             if search_term or class_data or section_data:
                 videos = self.db.search_videos(
                    search_term=search_term,
                    class_filter=class_data,
                    section_filter=section_data,
                    limit=self.page_size,
                    offset=offset
                 )
                 self.total_videos = self.db.get_search_count(
                    search_term=search_term,
                    class_filter=class_data,
                    section_filter=section_data
                 )
             else:
                 videos = self.db.get_all_videos(limit=self.page_size, offset=offset)
                 self.total_videos = self.db.get_total_video_count()

        self.update_video_table(videos)
        self.update_pagination_controls()
        self.status_label.setText(f"Showing {len(videos)} videos (Total: {self.total_videos})")

    def update_video_table(self, videos):
        """Render videos into the table"""
        self.videos_table.setRowCount(0)
        
        for video in videos:
            row = self.videos_table.rowCount()
            self.videos_table.insertRow(row)
            
            # ID (hidden)
            self.videos_table.setItem(row, 0, QTableWidgetItem(str(video['id'])))
            
            # Title
            self.videos_table.setItem(row, 1, QTableWidgetItem(video['title']))
            
            # Activity
            self.videos_table.setItem(row, 2, QTableWidgetItem(video.get('activity_name', 'N/A')))
            
            # Duration
            duration = FileManager.format_duration(video.get('duration', 0))
            self.videos_table.setItem(row, 3, QTableWidgetItem(duration))
            
            # Size
            size = FileManager.format_file_size(video.get('file_size', 0))
            self.videos_table.setItem(row, 4, QTableWidgetItem(size))
            
            # Version with status indicator
            version_num = video.get('version_number', 1)
            status = video.get('version_status', 'ACTIVE')
            if status == 'ACTIVE':
                status_icon = '✅'
            elif status == 'DRAFT':
                status_icon = '📝'
            else:  # ARCHIVED
                status_icon = '🗃️'
            self.videos_table.setItem(row, 5, QTableWidgetItem(f"{status_icon} v{version_num}"))
            
            # Availability
            availability = []
            if video.get('has_local_copy'):
                availability.append("💾 Local")
            if video.get('has_youtube_link'):
                availability.append("🌐 YouTube")
            self.videos_table.setItem(row, 6, QTableWidgetItem(" | ".join(availability) if availability else "None"))

    def update_pagination_controls(self):
        """Update state of pagination buttons"""
        if self.total_videos > 0:
            self.total_pages = math.ceil(self.total_videos / self.page_size)
        else:
            self.total_pages = 1
            
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
        
        self.first_page_btn.setEnabled(self.current_page > 1)
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)
        self.last_page_btn.setEnabled(self.current_page < self.total_pages)

    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_videos()

    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_videos()
            
    def go_to_first_page(self):
        """Go to first page"""
        self.current_page = 1
        self.load_videos()
        
    def go_to_last_page(self):
        """Go to last page"""
        self.current_page = self.total_pages
        self.load_videos()
    
    def activity_selected(self, item):
        """Handle activity selection"""
        self.current_activity_id = item.data(Qt.ItemDataRole.UserRole)
        activity = self.db.get_activity_by_id(self.current_activity_id)
        
        if activity:
            self.videos_title.setText(f"Videos - {activity['name']}")
            self.current_page = 1
            self.load_videos()
    
    def show_all_videos(self):
        """Show all videos"""
        self.current_activity_id = None
        self.videos_title.setText("All Videos")
        self.current_page = 1
        self.load_videos()
        self.activities_list.clearSelection()
    
    def video_selected(self):
        """Handle video selection"""
        selected_items = self.videos_table.selectedItems()
        if not selected_items:
            self.selected_video_id = None
            self.clear_video_details()
            return
        
        row = selected_items[0].row()
        video_id = int(self.videos_table.item(row, 0).text())
        self.selected_video_id = video_id
        
        # Load video details
        self.load_video_details(video_id)
    
    def load_video_details(self, video_id):
        """Load and display video details"""
        video = self.db.get_video_by_id(video_id)
        if not video:
            return
        
        # Enable/disable buttons based on availability
        self.play_local_btn.setEnabled(bool(video.get('has_local_copy')))
        self.play_youtube_btn.setEnabled(bool(video.get('has_youtube_link')))
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

        # Show/hide document button
        has_document = bool(video.get('has_document'))
        self.view_doc_btn.setVisible(has_document)
        self.view_doc_btn.setEnabled(has_document)
        
        # Load thumbnail
        thumbnail_path = video.get('thumbnail_path')
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
            # Ensure minimum size for visibility
            scaled_pixmap = pixmap.scaled(320, 180, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            self.thumbnail_label.setPixmap(scaled_pixmap)
            # Ensure alignment is center
            self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.thumbnail_label.clear()
            self.thumbnail_label.setText("No thumbnail available")
            self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Get proper tags from relationship
        video_tags = self.db.get_video_tags(video_id)
        tags_display = ', '.join([tag['name'] for tag in video_tags]) if video_tags else 'No tags'

        # Get status display
        status = video.get('version_status', 'ACTIVE')
        if status == 'ACTIVE':
            status_display = "✅ ACTIVE"
        elif status == 'DRAFT':
            status_display = "📝 DRAFT"
        else:
            status_display = "🗃️ ARCHIVED"

        # Display details
        details_html = f"""
        <h3>{video['title']}</h3>
        <p><strong>Activity:</strong> {video.get('activity_name', 'N/A')}</p>
        <p><strong>Version:</strong> {video.get('version_number', 1)} ({status_display})</p>
        <p><strong>Event Date:</strong> {video.get('event_date', 'N/A')}</p>
        <p><strong>Duration:</strong> {FileManager.format_duration(video.get('duration', 0))}</p>
        <p><strong>Resolution:</strong> {video.get('resolution', 'N/A')}</p>
        <p><strong>Format:</strong> {video.get('format', 'N/A')}</p>
        <p><strong>Size:</strong> {FileManager.format_file_size(video.get('file_size', 0))}</p>
        <p><strong>Description:</strong><br>{video.get('description', 'No description')}</p>
        <p><strong>Tags:</strong> {tags_display}</p>
        <p><strong>Upload Date:</strong> {video.get('upload_date', 'N/A')[:10]}</p>
        """

        # Add version notes if they exist
        version_notes = video.get('version_notes', '').strip()
        if version_notes:
            details_html += f"<p><strong>Version Notes:</strong><br>{version_notes}</p>"
        
        self.details_text.setHtml(details_html)
    
    def clear_video_details(self):
        """Clear video details panel"""
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("No video selected")
        self.details_text.clear()
        self.play_local_btn.setEnabled(False)
        self.play_youtube_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
    
    def search_videos_original(self, text):
        """Search videos"""
        if not text.strip():
            self.show_all_videos()
            return

        videos = self.db.search_videos(text)
        self.videos_title.setText(f"Search Results - '{text}'")
        self.load_videos(videos)
    
    def update_statistics(self):
        """Update statistics in status bar"""
        stats = self.db.get_statistics()
        stats_text = (f"Videos: {stats['total_videos']} | "
                     f"Activities: {stats['total_activities']} | "
                     f"Storage: {stats['total_storage_mb']} MB")
        self.stats_label.setText(stats_text)
    
    def refresh_all(self):
        """Refresh all data"""
        self.load_activities()
        if self.current_activity_id:
            videos = self.db.get_videos_by_activity(self.current_activity_id)
            self.load_videos(videos)
        else:
            self.load_videos()
        self.update_statistics()
        self.status_label.setText("Refreshed")
    
    def add_video(self):
        """Open add video dialog"""
        from ui.add_video_dialog import AddVideoDialog
        dialog = AddVideoDialog(self, self.db, self.file_manager)
        if dialog.exec():
            self.refresh_all()
    
    def edit_video(self):
        """Open edit video dialog"""
        if not self.selected_video_id:
            return
        
        from ui.edit_video_dialog import EditVideoDialog
        dialog = EditVideoDialog(self, self.db, self.file_manager, self.selected_video_id)
        if dialog.exec():
            self.refresh_all()
            self.load_video_details(self.selected_video_id)
    
    def delete_video(self):
        """Delete selected video"""
        if not self.selected_video_id:
            return
        
        video = self.db.get_video_by_id(self.selected_video_id)
        if not video:
            return
        
        reply = QMessageBox.question(
            self, 
            "Confirm Delete",
            f"Are you sure you want to delete '{video['title']}'?\n\nThis will also delete the local video file if it exists.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete local file if exists
            if video.get('has_local_copy') and video.get('file_path'):
                self.file_manager.delete_video_file(video['file_path'])
            
            # Delete thumbnail
            if video.get('thumbnail_path'):
                self.file_manager.delete_thumbnail(video['thumbnail_path'])

            # Delete document
            if video.get('has_document') and video.get('document_path'):
                self.file_manager.delete_document_file(video['document_path'])

            # Delete from database
            if self.db.delete_video(self.selected_video_id):
                QMessageBox.information(self, "Success", "Video deleted successfully")
                self.selected_video_id = None
                self.refresh_all()
                self.clear_video_details()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete video")
    
    def manage_activities(self):
        """Open activity management dialog"""
        from ui.activity_manager import ActivityManagerDialog
        dialog = ActivityManagerDialog(self, self.db)
        if dialog.exec():
            self.refresh_all()

    def manage_classes(self):
        """Open class management dialog"""
        from ui.class_manager import ClassManagerDialog
        dialog = ClassManagerDialog(self, self.db)
        if dialog.exec():
            self.refresh_all()

    def manage_sections(self):
        """Open section management dialog"""
        from ui.section_manager import SectionManagerDialog
        dialog = SectionManagerDialog(self, self.db)
        if dialog.exec():
            self.refresh_all()

    def show_collections(self):
        """Open collection manager dialog"""
        from ui.collection_manager import CollectionManagerDialog
        dialog = CollectionManagerDialog(self, self.db)
        if dialog.exec():
            self.refresh_all()

    def add_video_to_collection(self, collection_id):
        """Add the currently selected video to a collection"""
        if not self.selected_video_id:
            QMessageBox.warning(self, "No Video Selected", "Please select a video first")
            return

        video = self.db.get_video_by_id(self.selected_video_id)
        collection = self.db.get_collection_by_id(collection_id)

        if not video or not collection:
            return

        if self.db.add_video_to_collection(collection_id, self.selected_video_id):
            QMessageBox.information(self, "Success",
                                  f"'{video['title']}' added to '{collection['name']}'")
        else:
            QMessageBox.warning(self, "Info",
                              f"'{video['title']}' is already in '{collection['name']}'")

    def remove_video_from_collection(self, collection_id):
        """Remove the currently selected video from a collection"""
        if not self.selected_video_id:
            QMessageBox.warning(self, "No Video Selected", "Please select a video first")
            return

        video = self.db.get_video_by_id(self.selected_video_id)
        collection = self.db.get_collection_by_id(collection_id)

        if not video or not collection:
            return

        if self.db.remove_video_from_collection(collection_id, self.selected_video_id):
            QMessageBox.information(self, "Success",
                                  f"'{video['title']}' removed from '{collection['name']}'")
        else:
            QMessageBox.warning(self, "Error", "Failed to remove video from collection")
    
    def play_local_video(self):
        """Play local video file"""
        if not self.selected_video_id:
            return

        video = self.db.get_video_by_id(self.selected_video_id)
        if video and video.get('file_path') and os.path.exists(video['file_path']):
            from ui.video_player import VideoPlayerDialog
            thumbnail_path = video.get('thumbnail_path')
            player = VideoPlayerDialog(self, video['file_path'], video['title'], thumbnail_path)
            player.exec()
        else:
            QMessageBox.warning(self, "Error", "Video file not found")
    
    def play_youtube_video(self):
        """Play YouTube video"""
        if not self.selected_video_id:
            return
        
        video = self.db.get_video_by_id(self.selected_video_id)
        if video and video.get('youtube_url'):
            from ui.youtube_player import YouTubePlayerDialog
            player = YouTubePlayerDialog(self, video['youtube_url'], video['title'])
            player.exec()
        else:
            QMessageBox.warning(self, "Error", "YouTube URL not available")

    def view_document(self):
        """Open document file"""
        if not self.selected_video_id:
            return

        video = self.db.get_video_by_id(self.selected_video_id)
        if video and video.get('document_path') and os.path.exists(video['document_path']):
            success = self.file_manager.open_document_file(video['document_path'])
            if not success:
                QMessageBox.warning(self, "Error", "Failed to open document")
        else:
            QMessageBox.warning(self, "Error", "Document file not found")

    def show_video_context_menu(self, position):
        """Show context menu for video table"""
        if not self.videos_table.selectedItems():
            return
        
        menu = QMenu()
        
        if self.selected_video_id:
            video = self.db.get_video_by_id(self.selected_video_id)
            
            if video and video.get('has_local_copy'):
                play_local_action = menu.addAction("🎬 Play Local Copy")
                play_local_action.triggered.connect(self.play_local_video)
                
                open_location_action = menu.addAction("📁 Open File Location")
                open_location_action.triggered.connect(lambda: self.file_manager.open_file_location(video['file_path']))
            
            if video and video.get('has_youtube_link'):
                play_youtube_action = menu.addAction("▶️ Play YouTube Link")
                play_youtube_action.triggered.connect(self.play_youtube_video)
            
            menu.addSeparator()

            # Collections submenu
            collections_menu = menu.addMenu("📚 Collections")

            # Add to collection submenu
            add_to_collection_menu = collections_menu.addMenu("➕ Add to Collection")

            # Get all collections
            collections = self.db.get_all_collections()
            if collections:
                for collection in collections:
                    action = add_to_collection_menu.addAction(collection['name'])
                    action.triggered.connect(
                        lambda checked, c_id=collection['id']: self.add_video_to_collection(c_id)
                    )
            else:
                add_to_collection_menu.addAction("No collections available").setEnabled(False)

            # Remove from collections submenu
            video_collections = self.db.get_video_collections(video['id'])
            if video_collections:
                remove_from_collection_menu = collections_menu.addMenu("❌ Remove from Collection")
                for collection in video_collections:
                    action = remove_from_collection_menu.addAction(collection['name'])
                    action.triggered.connect(
                        lambda checked, c_id=collection['id']: self.remove_video_from_collection(c_id)
                    )

            menu.addSeparator()

            edit_action = menu.addAction("✏️ Edit")
            edit_action.triggered.connect(self.edit_video)

            delete_action = menu.addAction("🗑️ Delete")
            delete_action.triggered.connect(self.delete_video)
        
        menu.exec(self.videos_table.viewport().mapToGlobal(position))

    def center_window(self):
        """Center the window on the screen"""
        # Use QApplication to get the primary screen
        from PyQt6.QtWidgets import QApplication
        if QApplication.instance():
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()

                # Calculate center position
                center_x = (screen_geometry.width() - self.frameSize().width()) // 2
                center_y = (screen_geometry.height() - self.frameSize().height()) // 2

                # Ensure window doesn't go off-screen
                center_x = max(0, center_x)
                center_y = max(0, center_y)

                # Move window to center
                self.move(center_x, center_y)

    def show_statistics(self):
        """Show statistics dialog"""
        stats = self.db.get_statistics()

        msg = f"""
        <h2>Video Management Statistics</h2>
        <p><strong>Total Videos:</strong> {stats['total_videos']}</p>
        <p><strong>Total Activities:</strong> {stats['total_activities']}</p>
        <p><strong>Videos with Local Copy:</strong> {stats['local_videos']}</p>
        <p><strong>Videos with YouTube Link:</strong> {stats['youtube_videos']}</p>
        <p><strong>Total Storage Used:</strong> {stats['total_storage_mb']} MB ({stats['total_storage_bytes']:,} bytes)</p>
        <p><strong>Available Disk Space:</strong> {stats.get('available_space_gb', 0.0)} GB</p>
        """

        QMessageBox.information(self, "Statistics", msg)

    def setup_search_completer(self):
        """Setup auto-complete for search input"""
        # Create completer model
        self.completer_model = QStringListModel()

        # Get initial suggestions
        suggestions = self.db.get_search_suggestions("")
        self.completer_model.setStringList(suggestions)

        # Create completer
        completer = QCompleter(self.completer_model, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        # Set completer to search input
        self.search_input.setCompleter(completer)

        # Update suggestions as user types
        self.search_input.textChanged.connect(self.update_search_suggestions)

    def update_search_suggestions(self, text):
        """Update search suggestions based on current input"""
        suggestions = self.db.get_search_suggestions(text)
        self.completer_model.setStringList(suggestions)

    def show_advanced_search(self):
        """Show advanced search dialog"""
        from ui.advanced_search_dialog import AdvancedSearchDialog

        # Get current filters
        current_class = self.class_filter.currentData() or ""
        current_section = self.section_filter.currentData() or ""

        dialog = AdvancedSearchDialog(self, self.db, current_class, current_section)

        if dialog.exec():
            # Store the search criteria
            self.current_search_criteria = dialog.get_search_criteria()

            # Apply the advanced search
            self.apply_advanced_search()

    def apply_advanced_search(self):
        """Apply advanced search criteria"""
        if not self.current_search_criteria:
            return

        # Call the advanced search method with tags support - UPDATE: Just fetch using load_videos which uses criteria
        self.current_page = 1
        self.load_videos()

        # Create descriptive title
        title_parts = []

        if self.current_search_criteria.get('search_term'):
            title_parts.append(f"Search: '{self.current_search_criteria['search_term']}'")

        if self.current_search_criteria.get('class_filter'):
            title_parts.append(f"Class: {self.current_search_criteria['class_filter']}")

        if self.current_search_criteria.get('section_filter'):
            title_parts.append(f"Section: {self.current_search_criteria['section_filter']}")

        if self.current_search_criteria.get('date_from') and self.current_search_criteria.get('date_to'):
            title_parts.append(f"Date: {self.current_search_criteria['date_from']} to {self.current_search_criteria['date_to']}")

        if title_parts:
            self.videos_title.setText("Advanced Search - " + " | ".join(title_parts))
        else:
            self.videos_title.setText("Advanced Search Results")

        # Clear activity selection and current search criteria
        self.current_activity_id = None
        self.activities_list.clearSelection()

    def search_videos(self, text):
        """Search videos - updated to handle both simple and advanced search"""
        if not text.strip():
            # Clear current search criteria if simple search is cleared
            if self.current_search_criteria:
                self.current_search_criteria = None
            self.show_all_videos()
            return

        # If advanced search criteria exists, update the search term
        if self.current_search_criteria:
            self.current_search_criteria['search_term'] = text.strip()
            self.apply_advanced_search()
        else:
            # Simple search
            self.current_page = 1
            self.videos_title.setText(f"Search Results - '{text.strip()}'")
            self.load_videos()

    def load_filter_options(self):
        """Load class and section filter options"""
        # Clear existing items except "All"
        while self.class_filter.count() > 1:
            self.class_filter.removeItem(1)
        while self.section_filter.count() > 1:
            self.section_filter.removeItem(1)

        # Load predefined classes from dedicated table
        classes = self.db.get_class_names()
        for class_name in classes:
            self.class_filter.addItem(class_name, class_name)

        # Load predefined sections from dedicated table
        sections = self.db.get_section_names()
        for section_name in sections:
            self.section_filter.addItem(section_name, section_name)

    def apply_filters(self):
        """Apply class/section filters to videos and activities"""
        class_filter = self.class_filter.currentData() or ""
        section_filter = self.section_filter.currentData() or ""

        # Load filtered videos
        self.current_page = 1
        self.load_videos()

        # Load filtered activities
        activities = self.db.get_activities_filtered(class_filter, section_filter)
        self.load_filtered_activities(activities)

        # Update title
        filter_text = []
        if class_filter:
            filter_text.append(f"Class: {class_filter}")
        if section_filter:
            filter_text.append(f"Section: {section_filter}")

        if filter_text:
            self.videos_title.setText(f"Videos - {' | '.join(filter_text)}")
        else:
            self.videos_title.setText("All Videos")

        # Clear activity selection
        self.current_activity_id = None
        self.activities_list.clearSelection()

    def load_filtered_activities(self, activities):
        """Load filtered activities into the list"""
        self.activities_list.clear()

        for activity in activities:
            videos_count = activity.get('videos_count', 0)
            class_name = activity.get('class', '')
            section_name = activity.get('section', '')

            # Format: Class - Section: Activity Name (videos)
            if class_name and section_name:
                display_text = f"{class_name} - {section_name}: {activity['name']} ({videos_count})"
            elif class_name:
                display_text = f"{class_name}: {activity['name']} ({videos_count})"
            elif section_name:
                display_text = f"{section_name}: {activity['name']} ({videos_count})"
            else:
                display_text = f"{activity['name']} ({videos_count})"

            self.activities_list.addItem(display_text)
            self.activities_list.item(self.activities_list.count() - 1).setData(Qt.ItemDataRole.UserRole, activity['id'])

    def refresh_all(self):
        """Refresh all data"""
        self.load_filter_options()
        self.load_activities()
        # Just reload videos, current state (activity/search) is preserved or we can reset
        # Let's reset page to 1 but keep context if possible? 
        # Actually refresh usually means "reload data", but existing logic tried to keep context.
        # But load_videos() reads current context! So just calling it is enough.
        # But we should probably stay on current page? Or reset?
        # User expectation on "Refresh": see new data. 
        # If I stay on page 5 and new data is on page 1, might be confusing.
        # But commonly refresh keeps view. Let's keep page.
        self.load_videos()
        self.update_statistics()
        self.status_label.setText("Refreshed")

    def export_activities(self):
        """Open export activities dialog"""
        from ui.export_activities_dialog import ExportActivitiesDialog
        dialog = ExportActivitiesDialog(self, self.db, self.file_manager)
        dialog.exec()

    def show_about(self):
        """Show about dialog"""
        about_msg = f"""
        <div style='text-align: center;'>
            <h1>{APP_NAME}</h1>
            <p style='font-size: 14px;'><strong>Version {APP_VERSION}</strong></p>
            <hr>
            <p style='font-size: 13px;'><strong>{ORGANIZATION}</strong></p>
            <p style='font-size: 12px;'>A comprehensive video management system for organizing<br>
            school activity videos with local and YouTube integration.</p>
            <hr>
            <p style='font-size: 12px;'><strong>Developed by:</strong> {DEVELOPER}</p>
            <p style='font-size: 11px; color: #666;'>© 2025 All Rights Reserved</p>
            <hr>
            <p style='font-size: 11px;'><strong>Features:</strong></p>
            <ul style='text-align: left; font-size: 11px;'>
                <li>Upload and manage video files locally</li>
                <li>Store YouTube links alongside local videos</li>
                <li>Dual playback support (local & YouTube)</li>
                <li>Activity-based organization</li>
                <li>Version control for videos</li>
                <li>Advanced search and filtering</li>
                <li>Auto-generated thumbnails</li>
                <li>Class and section filtering</li>
                <li>Storage statistics and monitoring</li>
                <li>HTML export reports</li>
            </ul>
        </div>
        """

        QMessageBox.about(self, f"About {APP_NAME}", about_msg)
