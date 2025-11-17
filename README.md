# video-files-manager

A comprehensive desktop application for managing school activity videos with local storage, YouTube integration, advanced tagging, collection management, and professional-grade performance optimizations.

Developed by Amit Kumar Upadhyay | Version 1.0.0 | November 16, 2025

## 🚀 Key Highlights

- **🏆 Enterprise Performance** - 16 database indexes, query caching, WAL journaling
- **🏷️ Advanced Organization** - Tags, collections, and hierarchical categorization
- **🎬 Professional Playback** - VLC-style player with thumbnail previews
- **🔍 Intelligent Search** - Multi-criteria filtering with auto-complete suggestions
- **📦 Easy Deployment** - Professional installer + portable executable options

## Features

### 📹 Video Management
- **Upload and store videos locally** - Videos are organized in activity-based folders
- **YouTube link integration** - Store and play YouTube links alongside local files
- **Dual playback options** - Play either local copy or YouTube version
- **Version control** - Manage multiple versions of the same video
- **Metadata management** - Store comprehensive information including:
  - Title, description, tags
  - Event date
  - Duration, resolution, file size
  - Auto-generated thumbnails

### 🏷️ Advanced Tagging System
- **Flexible Categorization** - Add unlimited custom tags to videos
- **Tag Management** - Create, edit, and delete tags with colors
- **Multi-tag Search** - Find videos by single or multiple tags
- **Auto-suggestions** - Smart tag recommendations during input
- **Tag Relationships** - Automatic tag-to-video associations

### 📚 Collection Management
- **Custom Collections** - Create themed video collections
- **Visual Organization** - Color-coded collections for easy identification
- **Batch Operations** - Add/remove multiple videos to collections
- **Collection Analytics** - View video counts and tag distributions
- **Quick Access** - Context menus for instant collection management

### 🗂️ Activity Organization
- Create and manage activity categories (Annual Function, Sports Day, etc.)
- Group videos by activities and classes/sections
- Track video count per activity
- Hierarchical organization (Class → Section → Activity)

### 🔍 Advanced Search & Filter
- **Real-time Search** - Instant results across titles, descriptions, tags, activities
- **Multi-criteria Filtering** - Class, section, format, date range, size, duration
- **Tag-based Filtering** - Find videos by content categories
- **Auto-complete Suggestions** - Smart search predictions
- **Combined Queries** - Complex filter combinations for precise results

### 📊 Performance Monitoring
- Total videos, activities, collections, and tags count
- Storage usage tracking with automatic optimization
- Videos with local/YouTube availability breakdown
- Database performance statistics and optimization suggestions
- Status bar with real-time metrics

### 🏆 Database Performance
- **16 Strategic Indexes** - Optimized queries for search and filtering
- **Query Caching** - Statistics cached for 30 seconds
- **WAL Journaling** - Concurrent reads during writes
- **Batch Operations** - Efficient bulk data processing
- **Connection Pooling** - Optimized database connections

### 🎬 Professional Players
- **Local Video Player** - VLC-style interface with:
  - Play/Pause/Stop controls and seek functionality
  - Volume control and time tracking
  - Thumbnail preview before playback
  - Fullscreen support
- **YouTube Player** - Embedded player with browser fallback option

## Installation

### 🎯 Choose Your Installation Method

#### Option 1: Professional Installer (Recommended)
**Best for end-users and production deployment**

**System Requirements:**
- Windows 7 SP1 or later (64-bit recommended)
- 4GB RAM minimum, 8GB recommended
- 500MB free disk space
- DirectX compatible graphics for video playback

**Installation Steps:**
1. Download the installer: `VideoManager_Setup.exe`
2. Run the installer as Administrator
3. Follow the installation wizard
4. Launch Video Manager from desktop shortcut or Start menu

**What You Get:**
- ✅ Professional installation with uninstaller
- ✅ Windows Add/Remove Programs integration
- ✅ Desktop and Start menu shortcuts
- ✅ Automatic database and storage creation
- ✅ No Python installation required
- ✅ Clean uninstall with option to keep data

**First Run:**
- Application automatically creates database
- Storage folders are created automatically
- No manual configuration needed
- Ready to use immediately

#### Option 2: Portable Version
**Best for testing on different machines**

1. Extract the `dist/VideoManager/` folder to any location
2. Run `VideoManager.exe` directly (no installation required)
3. All data stored in local `storage/` folder

**What You Get:**
- ✅ Runs from any location (USB drive, network share, etc.)
- ✅ No administrator privileges required
- ✅ No system modifications
- ✅ Easy cleanup (just delete the folder)
- ✅ Portable data - take it anywhere

#### Option 3: Developer Installation
**Best for development and customization**

**Prerequisites:**
- Python 3.8 or higher
- pip package manager

**Setup Steps:**

1. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```
   *Required packages: PyQt6, PyQt6-WebEngine, opencv-python, Pillow*

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **On first run:**
   - Database and storage folders are created automatically
   - Application is ready to use

#### Option 4: Build Your Own Installer
**For developers who want to create custom installers**

**Prerequisites:**
- Python 3.8+ with all dependencies
- PyInstaller (`pip install pyinstaller`)
- NSIS (Nullsoft Scriptable Install System)
  - Download from: https://nsis.sourceforge.io/Download

**Build Steps:**
```bash
# Run the professional build script
build_professional_installer.bat
```

This will:
- ✅ Verify all dependencies
- ✅ Clean previous builds
- ✅ Build executable with PyInstaller
- ✅ Create professional NSIS installer
- ✅ Generate VideoManager_Setup.exe

**Output:**
- `VideoManager_Setup.exe` - Professional installer
- `dist/VideoManager/` - Portable version

See `INSTALLER_README.md` for detailed build instructions.

## Usage Guide

### First Time Setup
1. Launch the application
2. Click "📁 Manage Activities" to create your first activity
3. Add activities like "Annual Function 2024", "Sports Day", etc.

### Adding Videos
1. Click "➕ Add Video" in the toolbar
2. Select an activity from the dropdown (or create new with + button)
3. Enter video title and details
4. **Upload local file** (optional):
   - Click "📁 Browse..." to select video file
   - Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, M4V
5. **Add YouTube link** (optional):
   - Paste YouTube URL in the YouTube Link field
6. Fill in description, tags, and other metadata
7. Click "💾 Save Video"

**Note:** You must provide either a local file OR YouTube link (or both)

### Managing Videos
- **Search:** Type in the search box to find videos
- **View Details:** Click on any video to see full details in the right panel
- **Edit:** Select a video and click "✏️ Edit Video"
- **Delete:** Select a video and click "🗑️ Delete Video"
- **Play Local:** Click "🎬 Play Local Copy" (if available)
- **Play YouTube:** Click "▶️ Play YouTube Link" (if available)

### Version Management
- When adding a new version of an existing video:
  - Use the same title as the original video
  - Check "Auto-increment version" for automatic versioning
  - Or manually set version number

### Context Menu Options
Right-click on any video for quick actions:
- Play Local Copy
- Play YouTube Link
- Open File Location
- Edit
- Delete

## Project Structure

```
Video Management/
├── main.py                      # Application entry point
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── database/
│   ├── __init__.py
│   └── db_manager.py           # Database operations
├── utils/
│   ├── __init__.py
│   └── file_manager.py         # File handling utilities
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│   ├── activity_manager.py     # Activity management dialog
│   ├── add_video_dialog.py     # Add video form
│   ├── edit_video_dialog.py    # Edit video form
│   ├── video_player.py         # Local video player
│   └── youtube_player.py       # YouTube video player
└── storage/
    ├── videos/                 # Organized video files by activity
    ├── thumbnails/             # Auto-generated thumbnails
    └── video_manager.db        # SQLite database
```

## Database Schema

### Activities Table
- id, name, description, created_date

### Videos Table
- id, activity_id, title, file_path, youtube_url
- file_name, file_size, duration, format, resolution
- version_number, event_date, upload_date
- description, tags, thumbnail_path
- has_local_copy, has_youtube_link

## Storage Management

### Video Files
- Videos are copied to: `storage/videos/<activity_name>/`
- Original files remain unchanged
- Automatic file renaming if duplicates exist
- Files are sanitized for safe storage

### Thumbnails
- Auto-generated from video at 10% duration
- Stored in: `storage/thumbnails/`
- Size: 320x180 pixels
- Format: JPEG

### Database
- SQLite database: `storage/video_manager.db`
- Automatic initialization on first run
- Cascading deletes for data integrity

## Tips & Best Practices

1. **Organize by Activities:** Create clear activity names like "Annual Function 2024" rather than just "Annual Function"

2. **Use Both Local & YouTube:**
   - Upload local files for offline access
   - Add YouTube links for easy sharing

3. **Add Descriptive Tags:** Use comma-separated tags for better searchability
   - Example: "sports, relay, 100m, winners, 2024"

4. **Version Control:** Use the version system to track video edits
   - Original: v1
   - Edited with intro: v2
   - Final cut: v3

5. **Regular Backups:** Backup the entire `storage/` folder periodically

## Troubleshooting

### Video won't play
- Ensure video file still exists in storage folder
- Check if required codecs are installed on your system
- Try updating PyQt6-Multimedia

### YouTube videos not loading
- Check internet connection
- Verify YouTube URL is valid
- Some videos may have embedding restrictions

### Application won't start
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8 or higher required)

### Database errors
- Don't manually edit the database file
- If corrupted, delete `storage/video_manager.db` (data will be lost)

## Technical Details

- **Framework:** PyQt6
- **Database:** SQLite3
- **Video Processing:** OpenCV (cv2)
- **Image Processing:** Pillow (PIL)
- **Web Engine:** PyQt6-WebEngine (for YouTube player)

## Future Enhancements

Potential features for future versions:
- Bulk video import
- Export reports (PDF/Excel)
- Cloud storage integration
- Video trimming/editing tools
- Multi-user support
- Advanced filters (by date range, file size, duration)

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the application logs
3. Ensure all dependencies are properly installed

## License

This application is created for school video management purposes.

---

**Version:** 1.0.0
**Created:** 2025
**Platform:** Windows (compatible with other OS with minor modifications)
