#!/usr/bin/env python3
"""
Database optimization script for Video Management Application
Performs database maintenance, analysis, and performance optimizations
"""
import sys
import os
import sqlite3
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE_PATH


class DatabaseOptimizer:
    """Tools for database performance optimization"""

    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path

    def connect(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def analyze_database(self):
        """Analyze database structure and performance"""
        print("🔍 Analyzing database...")

        conn = self.connect()
        cursor = conn.cursor()

        # Get basic statistics
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]

        print(f"📊 Database Statistics:")
        print(f"   Tables: {table_count}")

        # Analyze each table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} rows")

        # Check for existing indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        print(f"   Indexes: {len(indexes)}")

        # Check database file size
        file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        print(f"   Database size: {file_size / (1024 * 1024):.1f} MB")

        conn.close()

    def run_optimization(self):
        """Run database optimizations"""
        print("⚡ Optimizing database...")

        start_time = time.time()
        conn = self.connect()
        cursor = conn.cursor()

        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        result = cursor.fetchone()
        journal_mode = result[0] if result else "unknown"
        print(f"   Journal mode: {journal_mode}")

        # Set synchronous mode to NORMAL for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")

        # Set cache size (64MB)
        cursor.execute("PRAGMA cache_size=-64000")
        result = cursor.fetchone()
        cache_size = result[0] if result else -64000
        print(f"   Cache size: {abs(cache_size)} KB")

        # Enable memory-based temp storage
        cursor.execute("PRAGMA temp_store=MEMORY")

        # Run VACUUM to compact database
        print("   Running VACUUM (this may take a while)...")
        cursor.execute("VACUUM")

        # Run ANALYZE to update query statistics
        print("   Updating query statistics...")
        cursor.execute("ANALYZE")

        conn.commit()
        conn.close()

        duration = time.time() - start_time
        print(f"   ✅ Optimization completed in {duration:.2f} seconds")
    def check_indexes(self):
        """Check and report on database indexes"""
        print("🔗 Checking indexes...")

        conn = self.connect()
        cursor = conn.cursor()

        # Get all indexes
        cursor.execute("""
            SELECT name, tbl_name, sql
            FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY tbl_name, name
        """)

        indexes = cursor.fetchall()
        print(f"   Found {len(indexes)} custom indexes:")

        for idx in indexes:
            print(f"     {idx[0]} on {idx[1]}")

        conn.close()

    def run_integrity_check(self):
        """Run database integrity check"""
        print("✅ Running integrity check...")

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]

        if result == "ok":
            print("   ✅ Integrity check passed")
        else:
            print(f"   ❌ Integrity check failed: {result}")

        conn.close()

    def optimize_query_performance(self):
        """Apply query optimizations"""
        print("🚀 Applying query optimizations...")

        conn = self.connect()
        cursor = conn.cursor()

        # Enable query planner optimizations
        optimizations = [
            "PRAGMA automatic_index = ON",  # Allow automatic indexes
            "PRAGMA foreign_keys = ON",     # Enable foreign key checks
            "PRAGMA case_sensitive_like = OFF",  # Case-insensitive LIKE
            "PRAGMA query_only = OFF",      # Allow modifications
        ]

        for opt in optimizations:
            try:
                cursor.execute(opt)
                print(f"   ✅ {opt}")
            except sqlite3.Error as e:
                print(f"   ❌ {opt} failed: {e}")

        conn.commit()
        conn.close()

    def run_all_optimizations(self):
        """Run all optimization steps"""
        print("=" * 60)
        print("🏁 STARTING DATABASE OPTIMIZATION")
        print("=" * 60)

        self.analyze_database()
        print()

        self.check_indexes()
        print()

        self.run_integrity_check()
        print()

        self.optimize_query_performance()
        print()

        self.run_optimization()
        print()

        print("=" * 60)
        print("✅ DATABASE OPTIMIZATION COMPLETED")
        print("=" * 60)


def main():
    """Main optimization function"""
    optimizer = DatabaseOptimizer()

    try:
        optimizer.run_all_optimizations()
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
