"""File manager for handling video files, thumbnail generation, and YouTube helpers."""
import logging
import os
import shutil
import subprocess
import platform
import cv2
import threading
from PIL import Image
from typing import Optional, Tuple
import sys
from urllib.parse import urlparse, parse_qs

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VIDEOS_DIR, THUMBNAILS_DIR, DOCUMENTS_DIR, SUPPORTED_VIDEO_FORMATS, SUPPORTED_DOCUMENT_FORMATS, THUMBNAIL_SIZE, MAX_DOCUMENT_SIZE_MB

# Module logger
logger = logging.getLogger(__name__)


class FileManager:
    """Handles all file operations for videos"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove special characters from filename"""
        # Replace spaces with underscores, remove special characters, and trim
        invalid_chars = '<>:"/\\|?*'
        filename = filename.strip()
        filename = filename.replace(' ', '_')
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # Collapse repeated underscores
        while '__' in filename:
            filename = filename.replace('__', '_')
        # Limit filename length to a reasonable size
        max_len = 200
        if len(filename) > max_len:
            name, ext = os.path.splitext(filename)
            filename = name[: max_len - len(ext)] + ext
        return filename
    
    @staticmethod
    def get_activity_folder(activity_name: str) -> str:
        """Get or create folder path for an activity"""
        folder_name = FileManager.sanitize_filename(activity_name)
        folder_path = os.path.join(VIDEOS_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
    
    @staticmethod
    def copy_video_file(source_path: str, activity_name: str, new_filename: Optional[str] = None) -> Tuple[bool, str, str]:
        """
        Copy video file to managed storage
        Returns: (success, destination_path, error_message)
        """
        try:
            # Validate source file exists
            if not os.path.exists(source_path):
                return False, "", "Source file does not exist"
            
            # Validate file format
            file_ext = os.path.splitext(source_path)[1].lower()
            if file_ext not in SUPPORTED_VIDEO_FORMATS:
                return False, "", f"Unsupported video format: {file_ext}"
            
            # Get activity folder
            activity_folder = FileManager.get_activity_folder(activity_name)
            
            # Determine destination filename
            if new_filename:
                dest_filename = FileManager.sanitize_filename(new_filename)
                if not dest_filename.endswith(file_ext):
                    dest_filename += file_ext
            else:
                dest_filename = os.path.basename(source_path)
                dest_filename = FileManager.sanitize_filename(dest_filename)
            
            # Check if file already exists and create unique name
            dest_path = os.path.join(activity_folder, dest_filename)
            counter = 1
            base_name, ext = os.path.splitext(dest_filename)
            while os.path.exists(dest_path):
                dest_filename = f"{base_name}_{counter}{ext}"
                dest_path = os.path.join(activity_folder, dest_filename)
                counter += 1
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            return True, dest_path, ""
            
        except Exception as e:
            return False, "", f"Error copying file: {str(e)}"
    
    @staticmethod
    def delete_video_file(file_path: str) -> Tuple[bool, str]:
        """
        Delete video file from storage
        Returns: (success, error_message)
        """
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                return True, ""
            return False, "File does not exist"
        except Exception as e:
            logger.exception("Error deleting file: %s", file_path)
            return False, f"Error deleting file: {str(e)}"
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return 0
        except:
            return 0
    
    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """Format file size to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    @staticmethod
    def get_video_metadata(file_path: str) -> dict:
        """
        Extract video metadata using OpenCV with timeout
        Returns dict with duration, resolution, format
        """
        metadata = {
            'duration': 0,
            'resolution': 'Unknown',
            'format': os.path.splitext(file_path)[1].lstrip('.').upper(),
            'fps': 0
        }

        if not os.path.exists(file_path):
            return metadata

        def extract_metadata():
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS) or 0
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
                cap.release()

                result = {
                    'fps': fps,
                    'frame_count': frame_count,
                    'width': width,
                    'height': height
                }
                return result
            return None

        success, result = FileManager.run_with_timeout(extract_metadata, 15)

        if success and result:
            fps = result.get('fps', 0)
            frame_count = result.get('frame_count', 0)
            width = result.get('width', 0)
            height = result.get('height', 0)

            # Calculate duration
            if fps > 0 and frame_count > 0:
                duration = frame_count / fps
                metadata['duration'] = duration
                metadata['fps'] = fps

            # Set resolution
            if width and height:
                metadata['resolution'] = f"{width}x{height}"
        else:
            logger.warning("Failed to extract video metadata for %s (timeout or error)", file_path)

        return metadata

    @staticmethod
    def validate_video_file(file_path: str) -> bool:
        """
        Validate if the file is a valid video using ffprobe
        Returns True if valid, False otherwise
        """
        try:
            # Use ffprobe to check if file is a valid video
            result = subprocess.run([
                'ffprobe', '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name', '-of', 'csv=p=0', file_path
            ], capture_output=True, text=True, timeout=10)

            return result.returncode == 0 and result.stdout.strip() != ""

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # If ffprobe not available or times out, fall back to basic check
            try:
                # Basic check: try to open with cv2 briefly
                cap = cv2.VideoCapture(file_path)
                if cap.isOpened():
                    # Check if we can read at least one frame
                    ret, _ = cap.read()
                    cap.release()
                    return ret
                return False
            except:
                return False

    @staticmethod
    def run_with_timeout(func, timeout_seconds=30):
        """
        Run a function with a timeout using threading
        Returns tuple: (success, result)
        success is False if timeout or exception
        """
        result = [None]
        exception = [None]

        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout_seconds)

        if thread.is_alive():
            # Thread is still running (timed out)
            return False, None
        elif exception[0]:
            # Exception occurred
            return False, None
        else:
            return True, result[0]

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to HH:MM:SS"""
        if not seconds or seconds <= 0:
            return "00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def generate_thumbnail(video_path: str, video_id: int) -> Optional[str]:
        """
        Generate thumbnail from video file with timeout
        Returns path to thumbnail or None if failed
        """
        try:
            if not os.path.exists(video_path):
                return None

            def extract_frame():
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    return None

                # Get frame from 10% into the video; fallback to first frame
                total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
                target_frame = int(total_frames * 0.1) if total_frames > 0 else 0

                cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                ret, frame = cap.read()

                if not ret or frame is None:
                    # Try first frame
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()

                cap.release()

                if ret and frame is not None:
                    return frame
                return None

            success, frame = FileManager.run_with_timeout(extract_frame, 20)

            if not success or frame is None:
                logger.warning("Failed to extract frame from video %s (timeout or error)", video_path)
                return None

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create PIL Image and resize
            img = Image.fromarray(frame_rgb)
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

            # Save thumbnail
            thumbnail_filename = f"thumb_{video_id}.jpg"
            thumbnail_path = os.path.join(THUMBNAILS_DIR, thumbnail_filename)
            img.save(thumbnail_path, "JPEG", quality=85)

            return thumbnail_path

        except Exception:
            logger.exception("Error generating thumbnail for %s", video_path)
            return None
    
    @staticmethod
    def delete_thumbnail(thumbnail_path: str) -> bool:
        """Delete thumbnail file"""
        try:
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
                return True
            return False
        except:
            return False
    
    @staticmethod
    def open_file_location(file_path: str) -> bool:
        """Open file location in file explorer"""
        try:
            if not file_path or not os.path.exists(file_path):
                return False

            folder_path = os.path.dirname(file_path)
            system = platform.system()

            if system == 'Windows':
                os.startfile(folder_path)
            elif system == 'Darwin':
                subprocess.run(['open', folder_path], check=False)
            else:
                # Assume Linux / Unix
                subprocess.run(['xdg-open', folder_path], check=False)

            return True
        except Exception:
            logger.exception("Failed to open file location for %s", file_path)
            return False
    
    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """Validate if the URL is a valid YouTube link"""
        if not url:
            return False

        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower()
            if 'youtube.com' in host or 'youtu.be' in host:
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_youtube_embed_url(url: str) -> str:
        """Convert YouTube URL to embed URL"""
        if not url:
            return ""

        try:
            parsed = urlparse(url)

            # If already an embed url, return as-is
            if 'youtube.com' in parsed.netloc and parsed.path.startswith('/embed/'):
                return url

            video_id = None

            # Short link: youtu.be/VIDEO_ID
            if 'youtu.be' in parsed.netloc:
                video_id = parsed.path.lstrip('/')

            # Standard link: youtube.com/watch?v=VIDEO_ID
            if 'youtube.com' in parsed.netloc:
                qs = parse_qs(parsed.query)
                if 'v' in qs:
                    video_id = qs['v'][0]

            # YouTube Live streams or premieres
            if 'youtube.com' in parsed.netloc and '/live/' in parsed.path:
                qs = parse_qs(parsed.query)
                if 'v' in qs:
                    video_id = qs['v'][0]

            # YouTube Shorts
            if 'youtube.com' in parsed.netloc and '/shorts/' in parsed.path:
                path_parts = parsed.path.split('/')
                if len(path_parts) >= 3:
                    video_id = path_parts[2]

            # Fallback: try path segments
            if not video_id:
                parts = parsed.path.split('/')
                for part in parts[::-1]:  # Start from end
                    if part and len(part) == 11:  # YouTube IDs are 11 chars
                        # Check if it looks like a valid YouTube ID (alphanumeric + -_)
                        if part.replace('-', '').replace('_', '').isalnum():
                            video_id = part
                            break

            if video_id:
                # Strip any additional params
                video_id = video_id.split('?')[0].split('&')[0]
                # Return embed URL with parameters for better compatibility
                return f"https://www.youtube.com/embed/{video_id}"

        except Exception:
            logger.exception("Error parsing YouTube URL: %s", url)

        return url

    @staticmethod
    def copy_document_file(source_path: str, video_id: int) -> Tuple[bool, str, str]:
        """
        Copy document file to managed storage
        Returns: (success, destination_path, error_message)
        """
        try:
            # Validate source file exists
            if not os.path.exists(source_path):
                return False, "", "Source file does not exist"

            # Validate file size (10MB limit)
            file_size = os.path.getsize(source_path) / (1024 * 1024)  # Convert to MB
            if file_size > MAX_DOCUMENT_SIZE_MB:
                return False, "", f"Document file too large: {file_size:.1f}MB (max {MAX_DOCUMENT_SIZE_MB}MB)"

            # Validate file format
            file_ext = os.path.splitext(source_path)[1].lower()
            if file_ext not in SUPPORTED_DOCUMENT_FORMATS:
                return False, "", f"Unsupported document format: {file_ext}"

            # Create destination filename
            dest_filename = f"doc_{video_id}{file_ext}"
            dest_path = os.path.join(DOCUMENTS_DIR, dest_filename)

            # Copy the file (overwrite any existing document for this video)
            shutil.copy2(source_path, dest_path)

            return True, dest_path, ""

        except Exception as e:
            return False, "", f"Error copying document: {str(e)}"

    @staticmethod
    def delete_document_file(document_path: str) -> Tuple[bool, str]:
        """
        Delete document file from storage
        Returns: (success, error_message)
        """
        try:
            if document_path and os.path.exists(document_path):
                os.remove(document_path)
                return True, ""
            return False, "Document file does not exist"
        except Exception as e:
            logger.exception("Error deleting document: %s", document_path)
            return False, f"Error deleting document: {str(e)}"

    @staticmethod
    def open_document_file(file_path: str) -> bool:
        """
        Open document file in system default application
        Returns: success
        """
        try:
            if not file_path or not os.path.exists(file_path):
                return False

            system = platform.system()

            if system == 'Windows':
                # For .docx files, use start command
                # For .txt files, also use start command
                subprocess.run(['start', '', file_path], shell=True, check=False)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=False)
            else:  # Linux/Unix
                # Try xdg-open for both file types
                subprocess.run(['xdg-open', file_path], check=False)

            return True
        except Exception as e:
            logger.exception("Failed to open document: %s", file_path)
            return False
