#!/usr/bin/env python3
"""
Check database status and recent data using schema-defined tables
"""

import sqlite3
import os
from datetime import datetime, timedelta
from config import DATABASE_PATH

def check_database():
    """Check database status and show recent data"""
    db_path = f"{DATABASE_PATH}"
    
    if not os.path.exists(db_path):
        print("✗ Database file not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables, excluding system tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # Filter out system tables
        system_tables = ['sqlite_sequence', 'sqlite_stat1', 'sqlite_stat2', 'sqlite_stat3', 'sqlite_stat4']
        tables = [table for table in all_tables if table not in system_tables]
        
        print(f"✓ Database found with {len(tables)} user tables: {', '.join(tables)}")
        
        total_records = 0
        
        for table_name in tables:
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"\n Table '{table_name}' ({len(columns)} columns):")
            
            # Get total record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            table_records = cursor.fetchone()[0]
            total_records += table_records
            print(f"  ✓ Total records: {table_records}")
            
            # Show column names
            column_names = [col[1] for col in columns]
            print(f"  ✓ Columns: {', '.join(column_names)}")
            
            # Get recent data (last 5 records)
            if table_records > 0:
                cursor.execute(f"""
                    SELECT * FROM {table_name} 
                    ORDER BY created DESC 
                    LIMIT 5
                """)
                recent_data = cursor.fetchall()
                
                print(f"   Recent data (last 5 records):")
                for i, record in enumerate(recent_data, 1):
                    print(f"    {i}. {record}")
        
        print(f"\n📈 Total records across all user tables: {total_records}")
        
        # Check for data in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_count = 0
        
        for table_name in tables:
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table_name} 
                WHERE created > ?
            """, (one_hour_ago.strftime('%Y-%m-%d %H:%M:%S'),))
            table_recent = cursor.fetchone()[0]
            recent_count += table_recent
        
        print(f"\n⏰ Records in last hour: {recent_count}")
        
        if recent_count == 0:
            print("⚠️  No recent data - check if data sources are sending data")
        else:
            print("✓ Data is being received")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Error checking database: {e}")

if __name__ == "__main__":
    check_database() 