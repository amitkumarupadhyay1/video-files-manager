#!/usr/bin/env python3
"""
Script to generate thumbnails for all videos that don't have them
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.file_manager import FileManager

def main():
    """Generate thumbnails for all videos without them"""
    print("Generating thumbnails for videos...")

    db = DatabaseManager()
    file_manager = FileManager()

    # Get all videos
    videos = db.get_all_videos()
    updated_count = 0

    for video in videos:
        # Check if video has a file path and no thumbnail
        if video.get('file_path') and (not video.get('thumbnail_path') or not os.path.exists(video['thumbnail_path'])):
            print(f"Generating thumbnail for: {video['title']}")

            # Generate thumbnail
            thumbnail_path = file_manager.generate_thumbnail(video['file_path'], video['id'])

            if thumbnail_path and os.path.exists(thumbnail_path):
                # Update video in database
                video_data = db.get_video_by_id(video['id'])
                if video_data:
                    video_data['thumbnail_path'] = thumbnail_path
                    db.update_video(video['id'], video_data)
                    updated_count += 1
                    print(f"  ✓ Thumbnail generated: {thumbnail_path}")
            else:
                print(f"  ✗ Failed to generate thumbnail")

    print(f"\nThumbnail generation complete! Updated {updated_count} videos.")
    print("You may need to refresh the main application to see the thumbnails.")

if __name__ == "__main__":
    main()
