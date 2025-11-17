"""
Collection Manager Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QListWidget, QMessageBox, QTextEdit,
                             QColorDialog, QListWidgetItem, QTableWidget, QTableWidgetItem,
                             QWidget, QGroupBox, QHeaderView, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class CollectionManagerDialog(QDialog):
    """Dialog for managing collections and their videos"""

    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.selected_collection_id = None

        self.setWindowTitle("Collection Manager")
        self.setModal(True)
        self.resize(900, 600)

        self.init_ui()
        self.load_collections()

    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout(self)

        # Left panel - Collections list and form
        left_panel = self.create_left_panel()
        layout.addWidget(left_panel)

        # Right panel - Videos in selected collection
        right_panel = self.create_right_panel()
        layout.addWidget(right_panel)

    def create_left_panel(self):
        """Create left panel with collections list and form"""
        panel = QWidget()
        panel.setMaximumWidth(400)
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("Collections")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        # Collections list
        list_label = QLabel("Existing Collections:")
        layout.addWidget(list_label)

        self.collections_list = QListWidget()
        self.collections_list.itemClicked.connect(self.collection_selected)
        layout.addWidget(self.collections_list)

        # Form section
        form_label = QLabel("Add/Edit Collection:")
        form_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(form_label)

        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter collection name...")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Color picker
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(20, 20)
        self.color_preview.setStyleSheet("border: 1px solid #ccc; background-color: #ffffff;")
        self.current_color = "#ffffff"
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        # Description input
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter collection description (optional)...")
        self.description_input.setMaximumHeight(60)
        layout.addWidget(self.description_input)

        # Buttons
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ Add New")
        self.add_btn.clicked.connect(self.add_collection)
        btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("✏️ Update")
        self.update_btn.clicked.connect(self.update_collection)
        self.update_btn.setEnabled(False)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_collection)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        return panel

    def create_right_panel(self):
        """Create right panel with videos in selected collection"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        self.videos_title = QLabel("Select a collection to view its videos")
        self.videos_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.videos_title)

        # Add video button
        self.add_video_btn = QPushButton("➕ Add Videos to Collection")
        self.add_video_btn.clicked.connect(self.add_videos_to_collection)
        self.add_video_btn.setEnabled(False)
        layout.addWidget(self.add_video_btn)

        # Videos table
        self.videos_table = QTableWidget()
        self.videos_table.setColumnCount(4)
        self.videos_table.setHorizontalHeaderLabels([
            "ID", "Title", "Activity", "Added Date"
        ])
        self.videos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.videos_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.videos_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.videos_table.setColumnHidden(0, True)  # Hide ID column
        self.videos_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.videos_table.customContextMenuRequested.connect(self.show_video_context_menu)

        layout.addWidget(self.videos_table)

        return panel

    def load_collections(self):
        """Load collections into list"""
        self.collections_list.clear()
        collections = self.db.get_all_collections()

        for collection in collections:
            videos_count = collection.get('videos_count', 0)
            color = collection.get('color', '#ffffff')

            # Create custom item with color indicator
            item = QListWidgetItem()
            item.setText(f"{collection['name']} ({videos_count} videos)")
            item.setData(Qt.ItemDataRole.UserRole, collection['id'])

            # Add color indicator
            if color and color != '#ffffff':
                item.setBackground(QColor(color).lighter(150))

            self.collections_list.addItem(item)

    def collection_selected(self, item):
        """Handle collection selection"""
        self.selected_collection_id = item.data(Qt.ItemDataRole.UserRole)
        collection = self.db.get_collection_by_id(self.selected_collection_id)

        if collection:
            self.name_input.setText(collection['name'])
            self.description_input.setText(collection.get('description', ''))
            self.current_color = collection.get('color', '#ffffff')
            self.color_preview.setStyleSheet(f"border: 1px solid #ccc; background-color: {self.current_color};")

            self.update_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.add_video_btn.setEnabled(True)

            # Load videos in collection
            self.load_collection_videos()

    def add_collection(self):
        """Add new collection"""
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a collection name")
            return

        description = self.description_input.toPlainText().strip()

        collection_id = self.db.add_collection(name, description, self.current_color)

        if collection_id > 0:
            QMessageBox.information(self, "Success", f"Collection '{name}' added successfully")
            self.load_collections()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", f"Collection '{name}' already exists")

    def update_collection(self):
        """Update selected collection"""
        if not self.selected_collection_id:
            return

        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a collection name")
            return

        description = self.description_input.toPlainText().strip()

        if self.db.update_collection(self.selected_collection_id, name, description, self.current_color):
            QMessageBox.information(self, "Success", "Collection updated successfully")
            self.load_collections()
            self.load_collection_videos()
        else:
            QMessageBox.warning(self, "Error", "Failed to update collection")

    def delete_collection(self):
        """Delete selected collection"""
        if not self.selected_collection_id:
            return

        collection = self.db.get_collection_by_id(self.selected_collection_id)
        if not collection:
            return

        videos_count = len(self.db.get_collection_videos(self.selected_collection_id))

        msg = f"Are you sure you want to delete collection '{collection['name']}'?"
        if videos_count > 0:
            msg += f"\n\nThis will remove {videos_count} videos from this collection (videos won't be deleted)."

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_collection(self.selected_collection_id):
                QMessageBox.information(self, "Success", "Collection deleted successfully")
                self.load_collections()
                self.clear_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete collection")

    def choose_color(self):
        """Choose color for collection"""
        color = QColorDialog.getColor(QColor(self.current_color), self)
        if color.isValid():
            self.current_color = color.name()
            self.color_preview.setStyleSheet(f"border: 1px solid #ccc; background-color: {self.current_color};")

    def clear_form(self):
        """Clear form inputs"""
        self.name_input.clear()
        self.description_input.clear()
        self.current_color = "#ffffff"
        self.color_preview.setStyleSheet("border: 1px solid #ccc; background-color: #ffffff;")
        self.selected_collection_id = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.add_video_btn.setEnabled(False)
        self.videos_title.setText("Select a collection to view its videos")
        self.videos_table.setRowCount(0)

    def load_collection_videos(self):
        """Load videos in selected collection"""
        if not self.selected_collection_id:
            return

        collection = self.db.get_collection_by_id(self.selected_collection_id)
        videos = self.db.get_collection_videos(self.selected_collection_id)

        self.videos_title.setText(f"Videos in '{collection['name']}' ({len(videos)} videos)")

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

            # Date added to collection
            added_date = video.get('added_date', '')[:10] if video.get('added_date') else ''
            self.videos_table.setItem(row, 3, QTableWidgetItem(added_date))

    def add_videos_to_collection(self):
        """Add videos to the selected collection"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QHBoxLayout, \
                                 QPushButton, QLabel, QCheckBox

        if not self.selected_collection_id:
            return

        # Create video selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Videos to Collection")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        # Instructions
        layout.addWidget(QLabel("Select videos to add to the collection:"))

        # Video list with checkboxes
        self.video_checkboxes = []
        all_videos = self.db.get_all_videos()

        scroll_area = QWidget()
        scroll_layout = QVBoxLayout(scroll_area)

        for video in all_videos:
            checkbox = QCheckBox(f"{video['title']} - {video['activity_name']}")
            # Check if video is already in this collection
            video_collections = self.db.get_video_collections(video['id'])
            is_in_collection = any(c['id'] == self.selected_collection_id for c in video_collections)
            checkbox.setChecked(is_in_collection)
            scroll_layout.addWidget(checkbox)
            self.video_checkboxes.append((video['id'], checkbox))

        layout.addWidget(scroll_area)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        add_btn = QPushButton("➕ Add Selected")
        add_btn.clicked.connect(lambda checked, d=dialog: self.do_add_videos_to_collection(d))
        btn_layout.addWidget(add_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    def do_add_videos_to_collection(self, dialog):
        """Actually add selected videos to collection"""
        added_count = 0

        for video_id, checkbox in self.video_checkboxes:
            if checkbox.isChecked():
                if self.db.add_video_to_collection(self.selected_collection_id, video_id):
                    added_count += 1
            else:
                # Remove if unchecked
                self.db.remove_video_from_collection(self.selected_collection_id, video_id)

        if added_count > 0:
            QMessageBox.information(dialog, "Success", f"Added/updated {added_count} videos in collection")

        self.load_collection_videos()
        self.load_collections()
        dialog.accept()

    def show_video_context_menu(self, position):
        """Show context menu for video table"""
        from PyQt6.QtWidgets import QMenu
        
        if not self.videos_table.selectedItems():
            return

        row = self.videos_table.selectedItems()[0].row()
        video_id = int(self.videos_table.item(row, 0).text())

        menu = QMenu()

        # Add custom action to remove from collection
        remove_action = menu.addAction("❌ Remove from Collection")
        remove_action.triggered.connect(lambda: self.remove_video_from_collection(video_id))

        menu.exec(self.videos_table.viewport().mapToGlobal(position))

    def remove_video_from_collection(self, video_id):
        """Remove video from current collection"""
        if not self.selected_collection_id:
            return

        video = self.db.get_video_by_id(video_id)
        if not video:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove '{video['title']}' from this collection?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.remove_video_from_collection(self.selected_collection_id, video_id):
                self.load_collection_videos()
                self.load_collections()
            else:
                QMessageBox.warning(self, "Error", "Failed to remove video from collection")
