"""
Configuration file for Video Management Application
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Storage paths
STORAGE_DIR = os.path.join(BASE_DIR, 'storage')
VIDEOS_DIR = os.path.join(STORAGE_DIR, 'videos')
THUMBNAILS_DIR = os.path.join(STORAGE_DIR, 'thumbnails')
DOCUMENTS_DIR = os.path.join(STORAGE_DIR, 'documents')

# Database
DATABASE_PATH = os.path.join(STORAGE_DIR, 'video_manager.db')

# Application settings
APP_NAME = "Video Organizer"
APP_VERSION = "2.0.0"
ORGANIZATION = "Jingle Bell Nursery School Society"
DEVELOPER = "Amit Kumar Upadhyay"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Video settings
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v']
MAX_FILE_SIZE_MB = 5000  # Maximum file size in MB
THUMBNAIL_SIZE = (320, 180)  # Width x Height for thumbnails

# Document settings
SUPPORTED_DOCUMENT_FORMATS = ['.txt', '.docx']
MAX_DOCUMENT_SIZE_MB = 10  # Maximum document size in MB

# Create directories if they don't exist
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
