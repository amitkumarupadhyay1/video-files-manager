"""
Comprehensive Test Suite for Video Management System
Tests all major components and generates detailed report
"""
import sys
import os
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Tuple

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.file_manager import FileManager
from utils.backup_manager import BackupManager
from config import DATABASE_PATH, STORAGE_DIR, VIDEOS_DIR, THUMBNAILS_DIR


class TestResult:
    """Store test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.warnings = []
        self.performance_metrics = {}
        
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
        
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
        
    def add_warning(self, warning: str):
        self.warnings.append(warning)
        print(f"⚠️  WARNING: {warning}")
        
    def add_metric(self, name: str, value: float):
        self.performance_metrics[name] = value
        print(f"📊 METRIC: {name} = {value:.4f}s")


class VideoManagementTester:
    """Comprehensive test suite for Video Management System"""
    
    def __init__(self):
        self.result = TestResult()
        self.db = None
        self.file_manager = None
        self.test_data = {}
        
    def setup(self):
        """Initialize test environment"""
        print("\n" + "="*70)
        print("VIDEO MANAGEMENT SYSTEM - COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {DATABASE_PATH}")
        print(f"Storage: {STORAGE_DIR}")
        print("="*70 + "\n")
        
        try:
            self.db = DatabaseManager()
            self.file_manager = FileManager()
            self.result.add_pass("Test environment setup")
        except Exception as e:
            self.result.add_fail("Test environment setup", str(e))
            return False
        return True
    
    def test_database_initialization(self):
        """Test database initialization and schema"""
        print("\n--- Testing Database Initialization ---")
        
        try:
            # Check if database file exists
            if not os.path.exists(DATABASE_PATH):
                self.result.add_fail("Database file existence", "Database file not found")
                return
            self.result.add_pass("Database file exists")
            
            # Check database connection
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if all required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['activities', 'videos', 'tags', 'video_tags', 
                             'collections', 'collection_videos', 'classes', 'sections']
            
            for table in required_tables:
                if table in tables:
                    self.result.add_pass(f"Table '{table}' exists")
                else:
                    self.result.add_fail(f"Table '{table}' exists", "Table not found")
            
            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            if len(indexes) >= 10:
                self.result.add_pass(f"Database has {len(indexes)} indexes")
            else:
                self.result.add_warning(f"Only {len(indexes)} indexes found (expected 10+)")
            
            conn.close()
            
        except Exception as e:
            self.result.add_fail("Database initialization test", str(e))
    
    def test_activity_operations(self):
        """Test activity CRUD operations"""
        print("\n--- Testing Activity Operations ---")
        
        try:
            # Test CREATE
            start_time = time.time()
            activity_id = self.db.add_activity(
                name="Test Activity",
                description="Test Description",
                class_name="Class 10",
                section="A"
            )
            create_time = time.time() - start_time
            self.result.add_metric("Activity CREATE", create_time)
            
            if activity_id:
                self.result.add_pass("Create activity")
                self.test_data['activity_id'] = activity_id
            else:
                self.result.add_fail("Create activity", "No activity ID returned")
                return
            
            # Test READ
            start_time = time.time()
            activity = self.db.get_activity_by_id(activity_id)
            read_time = time.time() - start_time
            self.result.add_metric("Activity READ", read_time)
            
            if activity and activity['name'] == "Test Activity":
                self.result.add_pass("Read activity")
            else:
                self.result.add_fail("Read activity", "Activity data mismatch")
            
            # Test UPDATE
            start_time = time.time()
            self.db.update_activity(
                activity_id,
                name="Updated Test Activity",
                description="Updated Description",
                class_name="Class 11",
                section="B"
            )
            update_time = time.time() - start_time
            self.result.add_metric("Activity UPDATE", update_time)
            
            updated = self.db.get_activity_by_id(activity_id)
            if updated and updated['name'] == "Updated Test Activity":
                self.result.add_pass("Update activity")
            else:
                self.result.add_fail("Update activity", "Update not reflected")
            
            # Test LIST
            start_time = time.time()
            activities = self.db.get_all_activities()
            list_time = time.time() - start_time
            self.result.add_metric("Activity LIST", list_time)
            
            if len(activities) > 0:
                self.result.add_pass(f"List activities ({len(activities)} found)")
            else:
                self.result.add_fail("List activities", "No activities found")
            
        except Exception as e:
            self.result.add_fail("Activity operations test", str(e))
    
    def test_video_operations(self):
        """Test video CRUD operations"""
        print("\n--- Testing Video Operations ---")
        
        if 'activity_id' not in self.test_data:
            self.result.add_fail("Video operations test", "No activity ID available")
            return
        
        try:
            # Test CREATE
            video_data = {
                'activity_id': self.test_data['activity_id'],
                'title': 'Test Video',
                'description': 'Test video description',
                'tags': 'test,video,sample',
                'file_name': 'test_video.mp4',
                'file_size': 1024000,
                'duration': 120,
                'format': 'mp4',
                'resolution': '1920x1080',
                'youtube_url': 'https://www.youtube.com/watch?v=test',
                'has_local_copy': True,
                'has_youtube_link': True,
                'version_number': 1,
                'event_date': '2024-01-01'
            }
            
            start_time = time.time()
            video_id = self.db.add_video(video_data)
            create_time = time.time() - start_time
            self.result.add_metric("Video CREATE", create_time)
            
            if video_id:
                self.result.add_pass("Create video")
                self.test_data['video_id'] = video_id
            else:
                self.result.add_fail("Create video", "No video ID returned")
                return
            
            # Test READ
            start_time = time.time()
            video = self.db.get_video_by_id(video_id)
            read_time = time.time() - start_time
            self.result.add_metric("Video READ", read_time)
            
            if video and video['title'] == 'Test Video':
                self.result.add_pass("Read video")
            else:
                self.result.add_fail("Read video", "Video data mismatch")
            
            # Test UPDATE
            video_data['title'] = 'Updated Test Video'
            video_data['description'] = 'Updated description'
            
            start_time = time.time()
            self.db.update_video(video_id, video_data)
            update_time = time.time() - start_time
            self.result.add_metric("Video UPDATE", update_time)
            
            updated = self.db.get_video_by_id(video_id)
            if updated and updated['title'] == 'Updated Test Video':
                self.result.add_pass("Update video")
            else:
                self.result.add_fail("Update video", "Update not reflected")
            
            # Test LIST
            start_time = time.time()
            videos = self.db.get_all_videos()
            list_time = time.time() - start_time
            self.result.add_metric("Video LIST", list_time)
            
            if len(videos) > 0:
                self.result.add_pass(f"List videos ({len(videos)} found)")
            else:
                self.result.add_fail("List videos", "No videos found")
            
        except Exception as e:
            self.result.add_fail("Video operations test", str(e))
    
    def test_tag_operations(self):
        """Test tag management"""
        print("\n--- Testing Tag Operations ---")
        
        try:
            # Create tag
            start_time = time.time()
            tag_id = self.db.create_tag("test-tag", "#FF5733", "Test tag description")
            create_time = time.time() - start_time
            self.result.add_metric("Tag CREATE", create_time)
            
            if tag_id:
                self.result.add_pass("Create tag")
                self.test_data['tag_id'] = tag_id
            else:
                self.result.add_fail("Create tag", "No tag ID returned")
                return
            
            # Get all tags
            tags = self.db.get_all_tags()
            if len(tags) > 0:
                self.result.add_pass(f"List tags ({len(tags)} found)")
            else:
                self.result.add_fail("List tags", "No tags found")
            
            # Assign tag to video
            if 'video_id' in self.test_data:
                self.db.assign_tag_to_video(self.test_data['video_id'], tag_id)
                video_tags = self.db.get_video_tags(self.test_data['video_id'])
                if len(video_tags) > 0:
                    self.result.add_pass("Assign tag to video")
                else:
                    self.result.add_fail("Assign tag to video", "Tag not assigned")
            
        except Exception as e:
            self.result.add_fail("Tag operations test", str(e))
    
    def test_collection_operations(self):
        """Test collection management"""
        print("\n--- Testing Collection Operations ---")
        
        try:
            # Create collection
            start_time = time.time()
            collection_id = self.db.create_collection(
                "Test Collection",
                "Test collection description",
                "#3498db"
            )
            create_time = time.time() - start_time
            self.result.add_metric("Collection CREATE", create_time)
            
            if collection_id:
                self.result.add_pass("Create collection")
                self.test_data['collection_id'] = collection_id
            else:
                self.result.add_fail("Create collection", "No collection ID returned")
                return
            
            # Get all collections
            collections = self.db.get_all_collections()
            if len(collections) > 0:
                self.result.add_pass(f"List collections ({len(collections)} found)")
            else:
                self.result.add_fail("List collections", "No collections found")
            
            # Add video to collection
            if 'video_id' in self.test_data:
                self.db.add_video_to_collection(collection_id, self.test_data['video_id'])
                collection_videos = self.db.get_collection_videos(collection_id)
                if len(collection_videos) > 0:
                    self.result.add_pass("Add video to collection")
                else:
                    self.result.add_fail("Add video to collection", "Video not added")
            
        except Exception as e:
            self.result.add_fail("Collection operations test", str(e))
    
    def test_search_functionality(self):
        """Test search and filter functionality"""
        print("\n--- Testing Search Functionality ---")
        
        try:
            # Basic search
            start_time = time.time()
            results = self.db.search_videos("Test")
            search_time = time.time() - start_time
            self.result.add_metric("Basic SEARCH", search_time)
            
            if isinstance(results, list):
                self.result.add_pass(f"Basic search ({len(results)} results)")
            else:
                self.result.add_fail("Basic search", "Invalid results")
            
            # Advanced search with filters
            start_time = time.time()
            results = self.db.search_videos(
                "Test",
                class_filter="Class 11",
                format_filter="mp4",
                has_local=True
            )
            advanced_search_time = time.time() - start_time
            self.result.add_metric("Advanced SEARCH", advanced_search_time)
            
            if isinstance(results, list):
                self.result.add_pass(f"Advanced search ({len(results)} results)")
            else:
                self.result.add_fail("Advanced search", "Invalid results")
            
            # Search suggestions
            suggestions = self.db.get_search_suggestions("Test")
            if isinstance(suggestions, list):
                self.result.add_pass(f"Search suggestions ({len(suggestions)} found)")
            else:
                self.result.add_fail("Search suggestions", "Invalid suggestions")
            
        except Exception as e:
            self.result.add_fail("Search functionality test", str(e))
    
    def test_class_section_operations(self):
        """Test class and section management"""
        print("\n--- Testing Class/Section Operations ---")
        
        try:
            # Create class
            class_id = self.db.create_class("Test Class 12")
            if class_id:
                self.result.add_pass("Create class")
            else:
                self.result.add_fail("Create class", "No class ID returned")
            
            # Get all classes
            classes = self.db.get_all_classes()
            if len(classes) > 0:
                self.result.add_pass(f"List classes ({len(classes)} found)")
            else:
                self.result.add_fail("List classes", "No classes found")
            
            # Create section
            section_id = self.db.create_section("Test Section C")
            if section_id:
                self.result.add_pass("Create section")
            else:
                self.result.add_fail("Create section", "No section ID returned")
            
            # Get all sections
            sections = self.db.get_all_sections()
            if len(sections) > 0:
                self.result.add_pass(f"List sections ({len(sections)} found)")
            else:
                self.result.add_fail("List sections", "No sections found")
            
        except Exception as e:
            self.result.add_fail("Class/Section operations test", str(e))
    
    def test_statistics(self):
        """Test statistics and analytics"""
        print("\n--- Testing Statistics ---")
        
        try:
            start_time = time.time()
            stats = self.db.get_statistics()
            stats_time = time.time() - start_time
            self.result.add_metric("Statistics query", stats_time)
            
            if stats:
                print(f"   Total Videos: {stats.get('total_videos', 0)}")
                print(f"   Total Activities: {stats.get('total_activities', 0)}")
                print(f"   Total Collections: {stats.get('total_collections', 0)}")
                print(f"   Total Tags: {stats.get('total_tags', 0)}")
                print(f"   Storage Used: {stats.get('storage_used', 0)} bytes")
                self.result.add_pass("Get statistics")
            else:
                self.result.add_fail("Get statistics", "No statistics returned")
            
        except Exception as e:
            self.result.add_fail("Statistics test", str(e))
    
    def test_backup_functionality(self):
        """Test backup functionality"""
        print("\n--- Testing Backup Functionality ---")
        
        try:
            backup_manager = BackupManager()
            
            # Create backup
            start_time = time.time()
            success, message = backup_manager.create_backup(manual=True)
            backup_time = time.time() - start_time
            self.result.add_metric("Backup creation", backup_time)
            
            if success:
                self.result.add_pass("Create backup")
            else:
                self.result.add_fail("Create backup", message)
            
            # List backups
            backups = backup_manager.list_backups()
            if len(backups) > 0:
                self.result.add_pass(f"List backups ({len(backups)} found)")
            else:
                self.result.add_warning("No backups found")
            
        except Exception as e:
            self.result.add_fail("Backup functionality test", str(e))
    
    def test_file_operations(self):
        """Test file management operations"""
        print("\n--- Testing File Operations ---")
        
        try:
            # Check storage directories
            if os.path.exists(STORAGE_DIR):
                self.result.add_pass("Storage directory exists")
            else:
                self.result.add_fail("Storage directory exists", "Directory not found")
            
            if os.path.exists(VIDEOS_DIR):
                self.result.add_pass("Video directory exists")
            else:
                self.result.add_fail("Video directory exists", "Directory not found")
            
            if os.path.exists(THUMBNAILS_DIR):
                self.result.add_pass("Thumbnail directory exists")
            else:
                self.result.add_fail("Thumbnail directory exists", "Directory not found")
            
            # Test file sanitization
            sanitized = self.file_manager.sanitize_filename("Test File (2024).mp4")
            if sanitized and sanitized != "":
                self.result.add_pass("Filename sanitization")
            else:
                self.result.add_fail("Filename sanitization", "Invalid result")
            
        except Exception as e:
            self.result.add_fail("File operations test", str(e))
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n--- Cleaning Up Test Data ---")
        
        try:
            # Delete test video
            if 'video_id' in self.test_data:
                self.db.delete_video(self.test_data['video_id'])
                self.result.add_pass("Delete test video")
            
            # Delete test collection
            if 'collection_id' in self.test_data:
                self.db.delete_collection(self.test_data['collection_id'])
                self.result.add_pass("Delete test collection")
            
            # Delete test tag
            if 'tag_id' in self.test_data:
                self.db.delete_tag(self.test_data['tag_id'])
                self.result.add_pass("Delete test tag")
            
            # Delete test activity (should cascade delete)
            if 'activity_id' in self.test_data:
                self.db.delete_activity(self.test_data['activity_id'])
                self.result.add_pass("Delete test activity")
            
        except Exception as e:
            self.result.add_fail("Cleanup test data", str(e))
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*70)
        print("TEST REPORT")
        print("="*70)
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nTotal Tests: {self.result.passed + self.result.failed}")
        print(f"✅ Passed: {self.result.passed}")
        print(f"❌ Failed: {self.result.failed}")
        print(f"⚠️  Warnings: {len(self.result.warnings)}")
        
        if self.result.failed > 0:
            print("\n--- ERRORS ---")
            for error in self.result.errors:
                print(f"  • {error}")
        
        if len(self.result.warnings) > 0:
            print("\n--- WARNINGS ---")
            for warning in self.result.warnings:
                print(f"  • {warning}")
        
        print("\n--- PERFORMANCE METRICS ---")
        for metric, value in self.result.performance_metrics.items():
            print(f"  • {metric}: {value:.4f}s")
        
        # Calculate success rate
        total = self.result.passed + self.result.failed
        if total > 0:
            success_rate = (self.result.passed / total) * 100
            print(f"\n✨ Success Rate: {success_rate:.2f}%")
        
        print("="*70)
        
        # Save report to file
        report_file = os.path.join(STORAGE_DIR, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("VIDEO MANAGEMENT SYSTEM - TEST REPORT\n")
                f.write("="*70 + "\n")
                f.write(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"\nTotal Tests: {self.result.passed + self.result.failed}\n")
                f.write(f"Passed: {self.result.passed}\n")
                f.write(f"Failed: {self.result.failed}\n")
                f.write(f"Warnings: {len(self.result.warnings)}\n")
                
                if self.result.failed > 0:
                    f.write("\nERRORS:\n")
                    for error in self.result.errors:
                        f.write(f"  • {error}\n")
                
                if len(self.result.warnings) > 0:
                    f.write("\nWARNINGS:\n")
                    for warning in self.result.warnings:
                        f.write(f"  • {warning}\n")
                
                f.write("\nPERFORMANCE METRICS:\n")
                for metric, value in self.result.performance_metrics.items():
                    f.write(f"  • {metric}: {value:.4f}s\n")
                
                if total > 0:
                    f.write(f"\nSuccess Rate: {success_rate:.2f}%\n")
            
            print(f"\n📄 Report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        if not self.setup():
            print("Setup failed. Aborting tests.")
            return
        
        # Run all test suites
        self.test_database_initialization()
        self.test_activity_operations()
        self.test_video_operations()
        self.test_tag_operations()
        self.test_collection_operations()
        self.test_search_functionality()
        self.test_class_section_operations()
        self.test_statistics()
        self.test_file_operations()
        self.test_backup_functionality()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Generate report
        self.generate_report()


def main():
    """Main test runner"""
    tester = VideoManagementTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
