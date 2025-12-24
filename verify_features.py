
import sys
import os
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.append(os.getcwd())

from database.db_manager import DatabaseManager
from utils.backup_manager import BackupManager

def verify():
    print("=== Verifying Pagination & Backups ===")
    
    # --- 1. Pagination Verification ---
    print("\n[Pagination] Initializing DatabaseManager...")
    db = DatabaseManager()
    
    # Create dummy videos
    print("[Pagination] Creating 55 dummy videos for pagination test...")
    # Use a dummy activity ID 9999 (assuming it doesn't exist, we'll create it)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO activities (id, name, created_date) VALUES (9999, 'PaginationTest', ?)", (datetime.now().isoformat(),))
    conn.commit()
    
    # Clean up old test videos
    cursor.execute("DELETE FROM videos WHERE activity_id = 9999")
    conn.commit()
    conn.close()
    
    # Insert 55 videos
    for i in range(55):
        video_data = {
            'activity_id': 9999,
            'title': f'Video {i+1}',
            'file_name': f'video_{i+1}.mp4',
            'file_path': f'C:/dummy/video_{i+1}.mp4',
            'upload_date': datetime.now().isoformat(),
            'description': 'Dummy video for pagination test',
            'has_local_copy': 1
        }
        try:
            db.add_video(video_data)
        except Exception as e:
            print(f"FAILED to add video: {video_data}")
            print(f"Error: {e}")
            raise e
        
    print("[Pagination] Videos created.")
    
    # Test Count
    count = db.get_total_video_count(activity_id=9999)
    print(f"[Pagination] Total Count Link: {count}")
    if count == 55:
        print("  ✅ Count OK")
    else:
        print(f"  ❌ Count Mismatch (Expected 55)")
        
    # Test Limit/Offset
    print("[Pagination] Fetching Page 1 (Limit 10, Offset 0)...")
    page1 = db.get_videos_by_activity(9999, limit=10, offset=0)
    print(f"  Result count: {len(page1)}")
    if len(page1) == 10:
        print("  ✅ Page 1 Size OK")
    else:
        print("  ❌ Page 1 Size Error")
        
    print("[Pagination] Fetching Page 2 (Limit 10, Offset 10)...")
    page2 = db.get_videos_by_activity(9999, limit=10, offset=10)
    # Verify different IDs
    ids1 = {v['id'] for v in page1}
    ids2 = {v['id'] for v in page2}
    intersection = ids1.intersection(ids2)
    
    if len(intersection) == 0:
         print("  ✅ Distinct Pages OK (No overlap)")
    else:
         print(f"  ❌ Pages Overlap: {intersection}")

    # Cleanup
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM videos WHERE activity_id = 9999")
    cursor.execute("DELETE FROM activities WHERE id = 9999")
    conn.commit()
    conn.close()
    print("[Pagination] Cleanup Done.")

    # --- 2. Backup Verification ---
    print("\n[Backups] Testing BackupManager...")
    bm = BackupManager(backup_dir="storage/backups_test") # Use test dir
    
    # Clear test dir
    if os.path.exists("storage/backups_test"):
        shutil.rmtree("storage/backups_test")
    os.makedirs("storage/backups_test")
    
    print("[Backups] Creating Auto Backup...")
    success, msg = bm.create_backup(manual=False)
    if success:
        print(f"  ✅ Auto Backup: {msg}")
    else:
        print(f"  ❌ Auto Backup Failed: {msg}")
        
    print("[Backups] Creating Manual Backup...")
    success, msg = bm.create_backup(manual=True)
    if success:
        print(f"  ✅ Manual Backup: {msg}")
    else:
        print(f"  ❌ Manual Backup Failed: {msg}")
        
    # Check files
    files = os.listdir("storage/backups_test")
    print(f"[Backups] Files in backup dir: {files}")
    if len(files) == 2:
        print("  ✅ File Count OK")
    else:
        print("  ❌ File Count Error")
        
    # Cleanup test backups
    if os.path.exists("storage/backups_test"):
        shutil.rmtree("storage/backups_test")
    print("[Backups] Cleanup Done.")
    
if __name__ == "__main__":
    verify()
