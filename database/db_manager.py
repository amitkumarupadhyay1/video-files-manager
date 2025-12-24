"""
Database manager for Video Management Application
Handles all database operations including CRUD for activities, videos, and links
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os
import sys
import shutil
from threading import Lock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH


class DatabaseManager:
    """Manages all database operations with performance optimizations"""

    def __init__(self):
        self.db_path = DATABASE_PATH
        self.connection_lock = Lock()
        self.cache_lock = Lock()
        self._stats_cache = None
        self._cache_timestamp = None
        self._cache_timeout = 30  # Cache statistics for 30 seconds
        self.init_database()
    
    def get_connection(self):
        """Create and return a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Initialize database tables and indexes"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create Activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                class TEXT,
                section TEXT,
                class_id INTEGER,
                section_id INTEGER,
                created_date TEXT NOT NULL,
                FOREIGN KEY (class_id) REFERENCES classes (id),
                FOREIGN KEY (section_id) REFERENCES sections (id)
            )
        ''')

        # Create Videos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                file_path TEXT,
                youtube_url TEXT,
                file_name TEXT,
                file_size INTEGER,
                duration REAL,
                format TEXT,
                resolution TEXT,
                version_number INTEGER DEFAULT 1,
                event_date TEXT,
                upload_date TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                thumbnail_path TEXT,
                document_path TEXT,
                has_local_copy INTEGER DEFAULT 0,
                has_youtube_link INTEGER DEFAULT 0,
                has_document INTEGER DEFAULT 0,
                FOREIGN KEY (activity_id) REFERENCES activities (id) ON DELETE CASCADE
            )
        ''')

        # Create Tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT,
                created_date TEXT NOT NULL
            )
        ''')

        # Create Video Tags junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE,
                UNIQUE(video_id, tag_id)
            )
        ''')

        # Create Collections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                color TEXT,
                created_date TEXT NOT NULL
            )
        ''')

        # Create Collection Videos junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                video_id INTEGER NOT NULL,
                added_date TEXT NOT NULL,
                FOREIGN KEY (collection_id) REFERENCES collections (id) ON DELETE CASCADE,
                FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE,
                UNIQUE(collection_id, video_id)
            )
        ''')

        # Create Classes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                color TEXT,
                created_date TEXT NOT NULL
            )
        ''')

        # Create Sections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                color TEXT,
                created_date TEXT NOT NULL
            )
        ''')

        # Create Links table (for additional external links)
        cursor.execute('''CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                created_date TEXT NOT NULL,
                FOREIGN KEY (activity_id) REFERENCES activities (id) ON DELETE CASCADE
            )
        ''')

        # Create performance indexes
        self._create_indexes(cursor)

        # Migration for existing databases: add new columns
        self._add_missing_columns(cursor)

        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")

        conn.commit()
        conn.close()

    def _create_indexes(self, cursor):
        """Create performance indexes"""
        indexes = [
            # Videos table indexes
            "CREATE INDEX IF NOT EXISTS idx_videos_activity_id ON videos(activity_id)",
            "CREATE INDEX IF NOT EXISTS idx_videos_title ON videos(title)",
            "CREATE INDEX IF NOT EXISTS idx_videos_upload_date ON videos(upload_date)",
            "CREATE INDEX IF NOT EXISTS idx_videos_format ON videos(format)",
            "CREATE INDEX IF NOT EXISTS idx_videos_file_size ON videos(file_size)",
            "CREATE INDEX IF NOT EXISTS idx_videos_duration ON videos(duration)",
            "CREATE INDEX IF NOT EXISTS idx_videos_version_number ON videos(version_number)",
            "CREATE INDEX IF NOT EXISTS idx_videos_has_local_copy ON videos(has_local_copy)",
            "CREATE INDEX IF NOT EXISTS idx_videos_has_youtube_link ON videos(has_youtube_link)",
            "CREATE INDEX IF NOT EXISTS idx_videos_has_document ON videos(has_document)",

            # Activities table indexes
            "CREATE INDEX IF NOT EXISTS idx_activities_class ON activities(class)",
            "CREATE INDEX IF NOT EXISTS idx_activities_section ON activities(section)",
            "CREATE INDEX IF NOT EXISTS idx_activities_class_section ON activities(class, section)",

            # Video Tags table indexes
            "CREATE INDEX IF NOT EXISTS idx_video_tags_video_id ON video_tags(video_id)",
            "CREATE INDEX IF NOT EXISTS idx_video_tags_tag_id ON video_tags(tag_id)",
            "CREATE INDEX IF NOT EXISTS idx_video_tags_composite ON video_tags(video_id, tag_id)",

            # Tags table indexes
            "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)",

            # Collections table indexes
            "CREATE INDEX IF NOT EXISTS idx_collections_name ON collections(name)",
            "CREATE INDEX IF NOT EXISTS idx_collection_videos_collection_id ON collection_videos(collection_id)",
            "CREATE INDEX IF NOT EXISTS idx_collection_videos_video_id ON collection_videos(video_id)",
        ]

        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError:
                pass  # Index might already exist

    def _add_missing_columns(self, cursor):
        """Add missing columns to existing tables"""
        columns_to_add = [
            ("videos", "document_path", "TEXT"),
            ("videos", "has_document", "INTEGER DEFAULT 0"),
            ("videos", "version_status", "TEXT DEFAULT 'ACTIVE'"),
            ("videos", "version_notes", "TEXT"),
            ("activities", "class", "TEXT"),
            ("activities", "section", "TEXT"),
            ("activities", "class_id", "INTEGER"),
            ("activities", "section_id", "INTEGER"),
        ]

        for table, column, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
            except sqlite3.OperationalError:
                pass  # Column already exists

    # ==================== ACTIVITY OPERATIONS ====================
    
    def add_activity(self, name: str, description: str = "", class_name: str = "", section: str = "") -> int:
        """Add a new activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_date = datetime.now().isoformat()

        try:
            cursor.execute(
                "INSERT INTO activities (name, description, class, section, created_date) VALUES (?, ?, ?, ?, ?)",
                (name, description, class_name, section, created_date)
            )
            conn.commit()
            activity_id = cursor.lastrowid
            return activity_id
        except sqlite3.IntegrityError:
            return -1  # Activity with this name already exists
        finally:
            conn.close()
    
    def get_all_activities(self) -> List[Dict]:
        """Get all activities"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Return activities with video counts and colors to avoid repeated queries in UI
        cursor.execute('''
            SELECT a.*, 
                   COUNT(v.id) as videos_count,
                   c.color as class_color,
                   s.color as section_color
            FROM activities a
            LEFT JOIN videos v ON v.activity_id = a.id
            LEFT JOIN classes c ON a.class = c.name
            LEFT JOIN sections s ON a.section = s.name
            GROUP BY a.id
            ORDER BY a.name
        ''')
        activities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return activities
    
    def get_activity_by_id(self, activity_id: int) -> Optional[Dict]:
        """Get activity by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_activity(self, activity_id: int, name: str, description: str, class_name: str = "", section: str = "") -> bool:
        """Update an activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE activities SET name = ?, description = ?, class = ?, section = ? WHERE id = ?",
                (name, description, class_name, section, activity_id)
            )
            conn.commit()
            success = cursor.rowcount > 0
            return success
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def delete_activity(self, activity_id: int) -> bool:
        """Delete an activity and all associated videos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    # ==================== VIDEO OPERATIONS ====================
    
    def add_video(self, video_data: Dict) -> int:
        """Add a new video"""
        conn = self.get_connection()
        cursor = conn.cursor()
        upload_date = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO videos (
                activity_id, title, file_path, youtube_url, file_name,
                file_size, duration, format, resolution, version_number,
                event_date, upload_date, description, tags, thumbnail_path,
                document_path, has_local_copy, has_youtube_link, has_document,
                version_status, version_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_data.get('activity_id'),
            video_data.get('title'),
            video_data.get('file_path'),
            video_data.get('youtube_url'),
            video_data.get('file_name'),
            video_data.get('file_size'),
            video_data.get('duration'),
            video_data.get('format'),
            video_data.get('resolution'),
            video_data.get('version_number', 1),
            video_data.get('event_date'),
            upload_date,
            video_data.get('description'),
            video_data.get('tags'),
            video_data.get('thumbnail_path'),
            video_data.get('document_path'),
            video_data.get('has_local_copy', 0),
            video_data.get('has_youtube_link', 0),
            video_data.get('has_document', 0),
            video_data.get('version_status', 'ACTIVE'),
            video_data.get('version_notes', '')
        ))
        
        conn.commit()
        video_id = cursor.lastrowid
        conn.close()
        return video_id
    
    def get_all_videos(self, limit: int = 0, offset: int = 0) -> List[Dict]:
        """Get all videos with activity information, optionally paginated"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT v.*, a.name as activity_name, a.class as activity_class, a.section as activity_section
            FROM videos v
            LEFT JOIN activities a ON v.activity_id = a.id
            ORDER BY v.upload_date DESC
        '''
        
        if limit > 0:
            query += f" LIMIT {limit} OFFSET {offset}"
            
        cursor.execute(query)
        videos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return videos

    def get_total_video_count(self, activity_id: Optional[int] = None) -> int:
        """Get total number of videos, optionally filtered by activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if activity_id:
            cursor.execute("SELECT COUNT(*) as count FROM videos WHERE activity_id = ?", (activity_id,))
        else:
            cursor.execute("SELECT COUNT(*) as count FROM videos")
            
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def get_videos_by_activity(self, activity_id: int, limit: int = 0, offset: int = 0) -> List[Dict]:
        """Get all videos for a specific activity, optionally paginated"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT v.*, a.name as activity_name 
            FROM videos v
            LEFT JOIN activities a ON v.activity_id = a.id
            WHERE v.activity_id = ?
            ORDER BY v.version_number DESC, v.upload_date DESC
        '''
        
        if limit > 0:
            query += f" LIMIT {limit} OFFSET {offset}"
            
        cursor.execute(query, (activity_id,))
        videos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return videos
    
    def get_video_by_id(self, video_id: int) -> Optional[Dict]:
        """Get video by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, a.name as activity_name 
            FROM videos v
            LEFT JOIN activities a ON v.activity_id = a.id
            WHERE v.id = ?
        ''', (video_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_video(self, video_id: int, video_data: Dict) -> bool:
        """Update video information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE videos SET
                title = ?, file_path = ?, youtube_url = ?, file_name = ?,
                file_size = ?, duration = ?, format = ?, resolution = ?,
                version_number = ?, event_date = ?, description = ?, tags = ?,
                thumbnail_path = ?, document_path = ?, has_local_copy = ?,
                has_youtube_link = ?, has_document = ?, version_status = ?,
                version_notes = ?
            WHERE id = ?
        ''', (
            video_data.get('title'),
            video_data.get('file_path'),
            video_data.get('youtube_url'),
            video_data.get('file_name'),
            video_data.get('file_size'),
            video_data.get('duration'),
            video_data.get('format'),
            video_data.get('resolution'),
            video_data.get('version_number'),
            video_data.get('event_date'),
            video_data.get('description'),
            video_data.get('tags'),
            video_data.get('thumbnail_path'),
            video_data.get('document_path'),
            video_data.get('has_local_copy'),
            video_data.get('has_youtube_link'),
            video_data.get('has_document'),
            video_data.get('version_status'),
            video_data.get('version_notes'),
            video_id
        ))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def delete_video(self, video_id: int) -> bool:
        """Delete a video"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def search_videos(self, search_term: str, class_filter: str = "", section_filter: str = "",
                      date_from: str = "", date_to: str = "", format_filter: str = "",
                      tags: str = "", size_min: int = 0, size_max: int = 0, duration_min: int = 0,
                      duration_max: int = 0, version_min: int = 0, status_filter: str = "",
                      has_local: bool = None, has_youtube: bool = None,
                      limit: int = 0, offset: int = 0) -> List[Dict]:
        """Advanced search with multiple filter criteria"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Parse tags
        tag_list = []
        if tags and tags.strip():
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Determine if we need to join with tags
        needs_tag_join = bool(tag_list)

        if needs_tag_join:
            query = '''
                SELECT DISTINCT v.*, a.name as activity_name, a.class as activity_class, a.section as activity_section
                FROM videos v
                LEFT JOIN activities a ON v.activity_id = a.id
                LEFT JOIN video_tags vt ON vt.video_id = v.id
                LEFT JOIN tags t ON vt.tag_id = t.id
                WHERE 1=1
            '''
        else:
            query = '''
                SELECT v.*, a.name as activity_name, a.class as activity_class, a.section as activity_section
                FROM videos v
                LEFT JOIN activities a ON v.activity_id = a.id
                WHERE 1=1
            '''

        params = []

        # Text search
        if search_term and search_term.strip():
            search_pattern = f"%{search_term.strip()}%"
            query += ''' AND (
                v.title LIKE ? OR v.description LIKE ? OR v.tags LIKE ? OR
                a.name LIKE ? OR v.file_name LIKE ?
            )'''
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

        # Tag filter
        if tag_list:
            placeholders = ','.join('?' * len(tag_list))
            query += f" AND t.name IN ({placeholders})"
            params.extend(tag_list)

        # Class filter
        if class_filter and class_filter != "All":
            query += " AND a.class = ?"
            params.append(class_filter)

        # Section filter
        if section_filter and section_filter != "All":
            query += " AND a.section = ?"
            params.append(section_filter)

        # Date range filters
        if date_from:
            query += " AND v.upload_date >= ?"
            params.append(date_from + " 00:00:00")
        if date_to:
            query += " AND v.upload_date <= ?"
            params.append(date_to + " 23:59:59")

        # Format filter
        if format_filter and format_filter != "All":
            query += " AND v.format = ?"
            params.append(format_filter)

        # Size filters
        if size_min > 0:
            query += " AND v.file_size >= ?"
            params.append(size_min)
        if size_max > 0:
            query += " AND v.file_size <= ?"
            params.append(size_max)

        # Duration filters
        if duration_min > 0:
            query += " AND v.duration >= ?"
            params.append(duration_min)
        if duration_max > 0:
            query += " AND v.duration <= ?"
            params.append(duration_max)

        # Version filter
        if version_min > 0:
            query += " AND v.version_number >= ?"
            params.append(version_min)

        # Status filter
        if status_filter and status_filter != "All":
            query += " AND v.version_status = ?"
            params.append(status_filter)

        # Availability filters
        if has_local is True:
            query += " AND v.has_local_copy = 1"
        elif has_local is False:
            query += " AND v.has_local_copy = 0"

        if has_youtube is True:
            query += " AND v.has_youtube_link = 1"
        elif has_youtube is False:
            query += " AND v.has_youtube_link = 0"

        query += " ORDER BY v.upload_date DESC"

        if limit > 0:
            # IMPORTANT: parameters must be passed to execute, not f-string, but limit/offset are safe integers
            # However, since we are building query string dynamically with params list, we handle it carefully.
            # Append to query string, but we don't need to add to params list for simple integer literals if passed directly, 
            # OR we can add placeholders. Let's use direct formatting for integers which is safe here.
            query += f" LIMIT {limit} OFFSET {offset}"

        cursor.execute(query, params)
        videos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return videos

    def get_search_count(self, search_term: str, class_filter: str = "", section_filter: str = "",
                      date_from: str = "", date_to: str = "", format_filter: str = "",
                      tags: str = "", size_min: int = 0, size_max: int = 0, duration_min: int = 0,
                      duration_max: int = 0, version_min: int = 0, status_filter: str = "",
                      has_local: bool = None, has_youtube: bool = None) -> int:
        """Get total count of videos matching search criteria (without pagination limits)"""
        # This duplicates the logic of search_videos but returns COUNT(*)
        # Ideally, we would refactor to share the query building logic, but for safety in this modification
        # we will copy the query building logic.
        
        conn = self.get_connection()
        cursor = conn.cursor()

        # Parse tags
        tag_list = []
        if tags and tags.strip():
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Determine if we need to join with tags
        needs_tag_join = bool(tag_list)

        if needs_tag_join:
            query = '''
                SELECT COUNT(DISTINCT v.id) as count
                FROM videos v
                LEFT JOIN activities a ON v.activity_id = a.id
                LEFT JOIN video_tags vt ON vt.video_id = v.id
                LEFT JOIN tags t ON vt.tag_id = t.id
                WHERE 1=1
            '''
        else:
            query = '''
                SELECT COUNT(*) as count
                FROM videos v
                LEFT JOIN activities a ON v.activity_id = a.id
                WHERE 1=1
            '''

        params = []

        # Text search
        if search_term and search_term.strip():
            search_pattern = f"%{search_term.strip()}%"
            query += ''' AND (
                v.title LIKE ? OR v.description LIKE ? OR v.tags LIKE ? OR
                a.name LIKE ? OR v.file_name LIKE ?
            )'''
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

        # Tag filter
        if tag_list:
            placeholders = ','.join('?' * len(tag_list))
            query += f" AND t.name IN ({placeholders})"
            params.extend(tag_list)

        # Class filter
        if class_filter and class_filter != "All":
            query += " AND a.class = ?"
            params.append(class_filter)

        # Section filter
        if section_filter and section_filter != "All":
            query += " AND a.section = ?"
            params.append(section_filter)

        # Date range filters
        if date_from:
            query += " AND v.upload_date >= ?"
            params.append(date_from + " 00:00:00")
        if date_to:
            query += " AND v.upload_date <= ?"
            params.append(date_to + " 23:59:59")

        # Format filter
        if format_filter and format_filter != "All":
            query += " AND v.format = ?"
            params.append(format_filter)

        # Size filters
        if size_min > 0:
            query += " AND v.file_size >= ?"
            params.append(size_min)
        if size_max > 0:
            query += " AND v.file_size <= ?"
            params.append(size_max)

        # Duration filters
        if duration_min > 0:
            query += " AND v.duration >= ?"
            params.append(duration_min)
        if duration_max > 0:
            query += " AND v.duration <= ?"
            params.append(duration_max)

        # Version filter
        if version_min > 0:
            query += " AND v.version_number >= ?"
            params.append(version_min)

        # Status filter
        if status_filter and status_filter != "All":
            query += " AND v.version_status = ?"
            params.append(status_filter)

        # Availability filters
        if has_local is True:
            query += " AND v.has_local_copy = 1"
        elif has_local is False:
            query += " AND v.has_local_copy = 0"

        if has_youtube is True:
            query += " AND v.has_youtube_link = 1"
        elif has_youtube is False:
            query += " AND v.has_youtube_link = 0"

        cursor.execute(query, params)
        count = cursor.fetchone()['count']
        conn.close()
        return count

    def get_search_count(self, search_term: str, class_filter: str = "", section_filter: str = "",
                      date_from: str = "", date_to: str = "", format_filter: str = "",
                      tags: str = "", size_min: int = 0, size_max: int = 0, duration_min: int = 0,
                      duration_max: int = 0, version_min: int = 0, status_filter: str = "",
                      has_local: bool = None, has_youtube: bool = None) -> int:
        """Get total count of videos matching search criteria (without pagination limits)"""
        
        conn = self.get_connection()
        cursor = conn.cursor()

        # Parse tags
        tag_list = []
        if tags and tags.strip():
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Determine if we need to join with tags
        needs_tag_join = bool(tag_list)

        if needs_tag_join:
            query = '''
                SELECT COUNT(DISTINCT v.id) as count
                FROM videos v
                LEFT JOIN activities a ON v.activity_id = a.id
                LEFT JOIN video_tags vt ON vt.video_id = v.id
                LEFT JOIN tags t ON vt.tag_id = t.id
                WHERE 1=1
            '''
        else:
            query = '''
                SELECT COUNT(*) as count
                FROM videos v
                LEFT JOIN activities a ON v.activity_id = a.id
                WHERE 1=1
            '''

        params = []

        # Text search
        if search_term and search_term.strip():
            search_pattern = f"%{search_term.strip()}%"
            query += ''' AND (
                v.title LIKE ? OR v.description LIKE ? OR v.tags LIKE ? OR
                a.name LIKE ? OR v.file_name LIKE ?
            )'''
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

        # Tag filter
        if tag_list:
            placeholders = ','.join('?' * len(tag_list))
            query += f" AND t.name IN ({placeholders})"
            params.extend(tag_list)

        # Class filter
        if class_filter and class_filter != "All":
            query += " AND a.class = ?"
            params.append(class_filter)

        # Section filter
        if section_filter and section_filter != "All":
            query += " AND a.section = ?"
            params.append(section_filter)

        # Date range filters
        if date_from:
            query += " AND v.upload_date >= ?"
            params.append(date_from + " 00:00:00")
        if date_to:
            query += " AND v.upload_date <= ?"
            params.append(date_to + " 23:59:59")

        # Format filter
        if format_filter and format_filter != "All":
            query += " AND v.format = ?"
            params.append(format_filter)

        # Size filters
        if size_min > 0:
            query += " AND v.file_size >= ?"
            params.append(size_min)
        if size_max > 0:
            query += " AND v.file_size <= ?"
            params.append(size_max)

        # Duration filters
        if duration_min > 0:
            query += " AND v.duration >= ?"
            params.append(duration_min)
        if duration_max > 0:
            query += " AND v.duration <= ?"
            params.append(duration_max)

        # Version filter
        if version_min > 0:
            query += " AND v.version_number >= ?"
            params.append(version_min)

        # Status filter
        if status_filter and status_filter != "All":
            query += " AND v.version_status = ?"
            params.append(status_filter)

        # Availability filters
        if has_local is True:
            query += " AND v.has_local_copy = 1"
        elif has_local is False:
            query += " AND v.has_local_copy = 0"

        if has_youtube is True:
            query += " AND v.has_youtube_link = 1"
        elif has_youtube is False:
            query += " AND v.has_youtube_link = 0"

        cursor.execute(query, params)
        count = cursor.fetchone()['count']
        conn.close()
        return count
            
    def get_unique_formats(self) -> List[str]:
        """Get all unique video formats in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT format FROM videos WHERE format IS NOT NULL AND format != '' ORDER BY format")
        formats = [row['format'] for row in cursor.fetchall()]
        conn.close()
        return formats

    def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query"""
        if len(query.strip()) < 2:
            return []

        conn = self.get_connection()
        cursor = conn.cursor()

        search_pattern = f"{query.strip()}%"

        cursor.execute('''
            SELECT DISTINCT title FROM videos
            WHERE title LIKE ?
            UNION
            SELECT DISTINCT name FROM activities
            WHERE name LIKE ?
            ORDER BY 1
            LIMIT ?
        ''', (search_pattern, search_pattern, limit))

        suggestions = [row[0] for row in cursor.fetchall()]
        conn.close()
        return suggestions
    
    def get_next_version_number(self, activity_id: int, title: str) -> int:
        """Get the next version number for a video with the same title in an activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT MAX(version_number) as max_version
            FROM videos
            WHERE activity_id = ? AND title = ?
        ''', (activity_id, title))
        row = cursor.fetchone()
        conn.close()

        max_version = row['max_version'] if row and row['max_version'] else 0
        return max_version + 1

    def get_video_versions(self, activity_id: int, title: str) -> List[Dict]:
        """Get all versions of a video (same title within activity)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, a.name as activity_name
            FROM videos v
            LEFT JOIN activities a ON v.activity_id = a.id
            WHERE v.activity_id = ? AND v.title = ?
            ORDER BY v.version_number ASC, v.upload_date ASC
        ''', (activity_id, title))
        versions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return versions

    def get_unique_version_statuses(self) -> List[str]:
        """Get all unique version statuses"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT version_status FROM videos WHERE version_status IS NOT NULL AND version_status != '' ORDER BY version_status")
        statuses = [row['version_status'] for row in cursor.fetchall()]
        conn.close()
        return statuses
    
    def get_class_names(self) -> List[str]:
        """Get all class names from the predefined classes table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM classes ORDER BY name")
        classes = [row['name'] for row in cursor.fetchall()]
        conn.close()
        return classes

    def get_section_names(self) -> List[str]:
        """Get all section names from the predefined sections table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sections ORDER BY name")
        sections = [row['name'] for row in cursor.fetchall()]
        conn.close()
        return sections

    # Keep backward compatibility
    def get_unique_classes(self) -> List[str]:
        """Get all unique class names (backward compatibility)"""
        return self.get_class_names() + self.get_unique_classes_from_activities()

    def get_unique_classes_from_activities(self) -> List[str]:
        """Get all unique class names from activities table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT class FROM activities WHERE class IS NOT NULL AND class != '' ORDER BY class")
        classes = [row['class'] for row in cursor.fetchall()]
        conn.close()
        return classes

    def get_unique_sections_from_activities(self) -> List[str]:
        """Get all unique section names from activities table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT section FROM activities WHERE section IS NOT NULL AND section != '' ORDER BY section")
        sections = [row['section'] for row in cursor.fetchall()]
        conn.close()
        return sections

    def get_unique_sections_for_class(self, class_name: str) -> List[str]:
        """Get unique sections for a specific class"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT section FROM activities
            WHERE class = ? AND section IS NOT NULL AND section != ''
            ORDER BY section
        ''', (class_name,))
        sections = [row['section'] for row in cursor.fetchall()]
        conn.close()
        return sections

    def get_unique_classes_for_section(self, section_name: str) -> List[str]:
        """Get unique classes that have a specific section"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT class FROM activities
            WHERE section = ? AND class IS NOT NULL AND class != ''
            ORDER BY class
        ''', (section_name,))
        classes = [row['class'] for row in cursor.fetchall()]
        conn.close()
        return classes

    def get_activities_filtered(self, class_filter: str = "", section_filter: str = "") -> List[Dict]:
        """Get activities filtered by class and/or section"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT a.*, COUNT(v.id) as videos_count
            FROM activities a
            LEFT JOIN videos v ON v.activity_id = a.id
        '''
        conditions = []
        params = []

        if class_filter and class_filter != "All":
            conditions.append("a.class = ?")
            params.append(class_filter)

        if section_filter and section_filter != "All":
            conditions.append("a.section = ?")
            params.append(section_filter)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " GROUP BY a.id ORDER BY a.name"

        cursor.execute(query, params)
        activities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return activities

    def get_videos_filtered(self, class_filter: str = "", section_filter: str = "") -> List[Dict]:
        """Get videos filtered by activity's class and/or section"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT v.*, a.name as activity_name, a.class as activity_class, a.section as activity_section
            FROM videos v
            LEFT JOIN activities a ON v.activity_id = a.id
        '''
        conditions = []
        params = []

        if class_filter and class_filter != "All":
            conditions.append("a.class = ?")
            params.append(class_filter)

        if section_filter and section_filter != "All":
            conditions.append("a.section = ?")
            params.append(section_filter)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY v.upload_date DESC"

        cursor.execute(query, params)
        videos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return videos

    # ==================== STATISTICS ====================

    def get_statistics(self) -> Dict:
        """Get overall statistics with caching for performance"""
        current_time = datetime.now()

        with self.cache_lock:
            # Return cached statistics if within timeout
            if (self._stats_cache and self._cache_timestamp and
                (current_time - self._cache_timestamp).seconds < self._cache_timeout):
                return self._stats_cache.copy()

        conn = self.get_connection()
        cursor = conn.cursor()

        # Execute multiple queries in a single call using UNION for better performance
        cursor.execute('''
            SELECT 'video_count' as metric, COUNT(*) as value FROM videos
            UNION ALL
            SELECT 'activity_count', COUNT(*) FROM activities
            UNION ALL
            SELECT 'storage_total', COALESCE(SUM(file_size), 0) FROM videos WHERE has_local_copy = 1
            UNION ALL
            SELECT 'local_video_count', COUNT(*) FROM videos WHERE has_local_copy = 1
            UNION ALL
            SELECT 'youtube_video_count', COUNT(*) FROM videos WHERE has_youtube_link = 1
        ''')

        results = {row['metric']: row['value'] for row in cursor.fetchall()}
        conn.close()

        # Get disk usage information
        available_space_gb = 0.0
        try:
            # Get disk usage for the current drive (where the database is stored)
            disk_usage = shutil.disk_usage('/')
            available_space_gb = round(disk_usage.free / (1024 ** 3), 2)  # Convert bytes to GB
        except (OSError, PermissionError):
            # If we can't access disk info, leave as 0
            available_space_gb = 0.0

        stats = {
            'total_videos': results.get('video_count', 0),
            'total_activities': results.get('activity_count', 0),
            'total_storage_bytes': results.get('storage_total', 0),
            'total_storage_mb': round(results.get('storage_total', 0) / (1024 * 1024), 2),
            'available_space_gb': available_space_gb,
            'local_videos': results.get('local_video_count', 0),
            'youtube_videos': results.get('youtube_video_count', 0)
        }

        # Cache the results
        with self.cache_lock:
            self._stats_cache = stats.copy()
            self._cache_timestamp = current_time

        return stats

    def clear_statistics_cache(self):
        """Clear the statistics cache"""
        with self.cache_lock:
            self._stats_cache = None
            self._cache_timestamp = None

    def update_video(self, video_id: int, video_data: Dict) -> bool:
        """Update video information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE videos SET
                title = ?, file_path = ?, youtube_url = ?, file_name = ?,
                file_size = ?, duration = ?, format = ?, resolution = ?,
                version_number = ?, event_date = ?, description = ?, tags = ?,
                thumbnail_path = ?, document_path = ?, has_local_copy = ?,
                has_youtube_link = ?, has_document = ?
            WHERE id = ?
        ''', (
            video_data.get('title'),
            video_data.get('file_path'),
            video_data.get('youtube_url'),
            video_data.get('file_name'),
            video_data.get('file_size'),
            video_data.get('duration'),
            video_data.get('format'),
            video_data.get('resolution'),
            video_data.get('version_number'),
            video_data.get('event_date'),
            video_data.get('description'),
            video_data.get('tags'),
            video_data.get('thumbnail_path'),
            video_data.get('document_path'),
            video_data.get('has_local_copy'),
            video_data.get('has_youtube_link'),
            video_data.get('has_document'),
            video_id
        ))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def delete_video(self, video_id: int) -> bool:
        """Delete a video"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        conn.commit()
        success = cursor.rowcount > 0
        
        # Clear statistics cache since we deleted a video
        self.clear_statistics_cache()
        
        conn.close()
        return success

    # ==================== TAGS OPERATIONS ====================

    def add_tag(self, name: str, color: str = "") -> int:
        """Add a new tag"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_date = datetime.now().isoformat()

        try:
            cursor.execute(
                "INSERT INTO tags (name, color, created_date) VALUES (?, ?, ?)",
                (name, color, created_date)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Tag already exists, return existing ID
            cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
            row = cursor.fetchone()
            return row['id'] if row else -1
        finally:
            conn.close()

    def get_all_tags(self) -> List[Dict]:
        """Get all tags"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tags ORDER BY name")
        tags = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tags

    def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def assign_tags_to_video(self, video_id: int, tag_names: List[str]) -> bool:
        """Assign multiple tags to a video (replaces existing tags)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Remove existing tags
            cursor.execute("DELETE FROM video_tags WHERE video_id = ?", (video_id,))

            # Add new tags
            for tag_name in tag_names:
                if tag_name.strip():
                    tag_id = self.add_tag(tag_name.strip())
                    if tag_id > 0:
                        cursor.execute(
                            "INSERT INTO video_tags (video_id, tag_id) VALUES (?, ?)",
                            (video_id, tag_id)
                        )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_video_tags(self, video_id: int) -> List[Dict]:
        """Get all tags for a video"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.* FROM tags t
            JOIN video_tags vt ON vt.tag_id = t.id
            WHERE vt.video_id = ?
            ORDER BY t.name
        ''', (video_id,))
        tags = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tags

    def get_unique_tags(self) -> List[str]:
        """Get all unique tag names"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT name FROM tags ORDER BY name")
        tag_names = [row['name'] for row in cursor.fetchall()]
        conn.close()
        return tag_names

    def get_videos_by_tags(self, tag_names: List[str]) -> List[Dict]:
        """Get videos that have any of the specified tags"""
        if not tag_names:
            return []

        conn = self.get_connection()
        cursor = conn.cursor()

        placeholders = ','.join('?' * len(tag_names))
        query = f'''
            SELECT DISTINCT v.*, a.name as activity_name, a.class as activity_class, a.section as activity_section
            FROM videos v
            LEFT JOIN activities a ON v.activity_id = a.id
            JOIN video_tags vt ON vt.video_id = v.id
            JOIN tags t ON vt.tag_id = t.id
            WHERE t.name IN ({placeholders})
            ORDER BY v.upload_date DESC
        '''

        cursor.execute(query, tag_names)
        videos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return videos

    # ==================== COLLECTIONS OPERATIONS ====================

    def add_collection(self, name: str, description: str = "", color: str = "") -> int:
        """Add a new collection"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_date = datetime.now().isoformat()

        try:
            cursor.execute(
                "INSERT INTO collections (name, description, color, created_date) VALUES (?, ?, ?, ?)",
                (name, description, color, created_date)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1  # Collection with this name already exists
        finally:
            conn.close()

    def get_all_collections(self) -> List[Dict]:
        """Get all collections"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*,
                   COUNT(cv.id) as videos_count,
                   GROUP_CONCAT(DISTINCT t.name) as tags
            FROM collections c
            LEFT JOIN collection_videos cv ON cv.collection_id = c.id
            LEFT JOIN videos v ON cv.video_id = v.id
            LEFT JOIN video_tags vt ON vt.video_id = v.id
            LEFT JOIN tags t ON vt.tag_id = t.id
            GROUP BY c.id
            ORDER BY c.name
        ''')
        collections = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return collections

    def get_collection_by_id(self, collection_id: int) -> Optional[Dict]:
        """Get collection by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM collections WHERE id = ?", (collection_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_collection(self, collection_id: int, name: str, description: str = "", color: str = "") -> bool:
        """Update a collection"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE collections SET name = ?, description = ?, color = ? WHERE id = ?",
                (name, description, color, collection_id)
            )
            conn.commit()
            success = cursor.rowcount > 0
            return success
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_collection(self, collection_id: int) -> bool:
        """Delete a collection"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def add_video_to_collection(self, collection_id: int, video_id: int) -> bool:
        """Add a video to a collection"""
        conn = self.get_connection()
        cursor = conn.cursor()
        added_date = datetime.now().isoformat()

        try:
            cursor.execute(
                "INSERT INTO collection_videos (collection_id, video_id, added_date) VALUES (?, ?, ?)",
                (collection_id, video_id, added_date)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Already in collection
        finally:
            conn.close()

    def remove_video_from_collection(self, collection_id: int, video_id: int) -> bool:
        """Remove a video from a collection"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM collection_videos WHERE collection_id = ? AND video_id = ?",
            (collection_id, video_id)
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def get_collection_videos(self, collection_id: int) -> List[Dict]:
        """Get all videos in a collection"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, a.name as activity_name, a.class as activity_class, a.section as activity_section,
                   cv.added_date
            FROM videos v
            LEFT JOIN activities a ON v.activity_id = a.id
            JOIN collection_videos cv ON cv.video_id = v.id
            WHERE cv.collection_id = ?
            ORDER BY cv.added_date DESC
        ''', (collection_id,))
        videos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return videos

    def get_video_collections(self, video_id: int) -> List[Dict]:
        """Get all collections containing a video"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, cv.added_date
            FROM collections c
            JOIN collection_videos cv ON cv.collection_id = c.id
            WHERE cv.video_id = ?
            ORDER BY c.name
        ''', (video_id,))
        collections = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return collections

    # ==================== CLASSES OPERATIONS ====================

    def add_class(self, name: str, description: str = "", color: str = "") -> int:
        """Add a new class"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_date = datetime.now().isoformat()

        try:
            cursor.execute('''
                INSERT INTO classes (name, description, color, created_date)
                VALUES (?, ?, ?, ?)
            ''', (name, description, color, created_date))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1  # Class with this name already exists
        finally:
            conn.close()

    def get_all_classes(self) -> List[Dict]:
        """Get all classes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT c.*, COUNT(a.id) as activities_count
                         FROM classes c
                         LEFT JOIN activities a ON a.class_id = c.id
                         GROUP BY c.id ORDER BY c.name''')
        classes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return classes

    def get_class_by_id(self, class_id: int) -> Optional[Dict]:
        """Get class by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes WHERE id = ?", (class_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_class(self, class_id: int, name: str, description: str = "", color: str = "") -> bool:
        """Update a class"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE classes SET name = ?, description = ?, color = ?
                WHERE id = ?
            ''', (name, description, color, class_id))
            conn.commit()
            success = cursor.rowcount > 0
            return success
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_class(self, class_id: int) -> bool:
        """Delete a class"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    # ==================== SECTIONS OPERATIONS ====================

    def add_section(self, name: str, description: str = "", color: str = "") -> int:
        """Add a new section"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_date = datetime.now().isoformat()

        try:
            cursor.execute('''INSERT INTO sections (name, description, color, created_date)
                             VALUES (?, ?, ?, ?)''', (name, description, color, created_date))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1  # Section with this name already exists
        finally:
            conn.close()

    def get_all_sections(self) -> List[Dict]:
        """Get all sections"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT s.*, COUNT(a.id) as activities_count
                         FROM sections s
                         LEFT JOIN activities a ON a.section_id = s.id
                         GROUP BY s.id ORDER BY s.name''')
        sections = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sections

    def get_section_by_id(self, section_id: int) -> Optional[Dict]:
        """Get section by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_section(self, section_id: int, name: str, description: str = "", color: str = "") -> bool:
        """Update a section"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE sections SET name = ?, description = ?, color = ?
                WHERE id = ?
            ''', (name, description, color, section_id))
            conn.commit()
            success = cursor.rowcount > 0
            return success
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_section(self, section_id: int) -> bool:
        """Delete a section"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sections WHERE id = ?", (section_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
