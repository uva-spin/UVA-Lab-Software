#!/usr/bin/env python3
"""
Check database status and recent data
"""

import sqlite3
import os
from datetime import datetime, timedelta

def check_database():
    """Check database status and show recent data"""
    db_path = "../instance/flaskr.sqlite"
    
    if not os.path.exists(db_path):
        print("✗ Database file not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(merged_data)")
        columns = cursor.fetchall()
        print(f"✓ Database found with {len(columns)} columns")
        
        # Get total record count
        cursor.execute("SELECT COUNT(*) FROM merged_data")
        total_records = cursor.fetchone()[0]
        print(f"✓ Total records: {total_records}")
        
        # Get records by data source
        cursor.execute("""
            SELECT data_source, COUNT(*) as count 
            FROM merged_data 
            GROUP BY data_source
        """)
        source_counts = cursor.fetchall()
        
        print("\nRecords by data source:")
        for source, count in source_counts:
            print(f"  - {source}: {count} records")
        
        # Get recent data (last 10 records)
        cursor.execute("""
            SELECT timestamp, data_source, fc501_ai, fc502_ai, ti501_ai, ti502_ai
            FROM merged_data 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        recent_data = cursor.fetchall()
        
        print(f"\nRecent data (last 10 records):")
        print("-" * 80)
        print(f"{'Timestamp':<20} {'Source':<15} {'FC501_AI':<10} {'FC502_AI':<10} {'TI501_AI':<10} {'TI502_AI':<10}")
        print("-" * 80)
        
        for record in recent_data:
            timestamp, source, fc501, fc502, ti501, ti502 = record
            print(f"{timestamp:<20} {source:<15} {fc501:<10.2f} {fc502:<10.2f} {ti501:<10.2f} {ti502:<10.2f}")
        
        # Check for data in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        cursor.execute("""
            SELECT COUNT(*) FROM merged_data 
            WHERE timestamp > ?
        """, (one_hour_ago.strftime('%Y-%m-%d %H:%M:%S'),))
        
        recent_count = cursor.fetchone()[0]
        print(f"\n✓ Records in last hour: {recent_count}")
        
        if recent_count == 0:
            print("⚠️  No recent data - check if data sources are sending data")
        else:
            print("✓ Data is being received")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Error checking database: {e}")

if __name__ == "__main__":
    check_database() 