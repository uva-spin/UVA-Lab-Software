#!/usr/bin/env python3
"""
Diagnostic script to check database status and test data insertion
"""

import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH

def diagnose_database():
    """Diagnose database issues"""
    db_path = DATABASE_PATH
    
    print("=== Database Diagnosis ===")
    print(f"Database path: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        print(f"\nAll tables: {all_tables}")
        
        # Filter user tables
        system_tables = ['sqlite_sequence', 'sqlite_stat1', 'sqlite_stat2', 'sqlite_stat3', 'sqlite_stat4']
        user_tables = [table for table in all_tables if table not in system_tables]
        print(f"User tables: {user_tables}")
        
        # Check each table
        for table_name in user_tables:
            print(f"\n--- Table: {table_name} ---")
            
            # Get schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema = cursor.fetchall()
            print(f"Schema: {schema}")
            
            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Record count: {count}")
            
            # Get sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} ORDER BY created DESC LIMIT 3")
                samples = cursor.fetchall()
                print(f"Latest records: {samples}")
        
        # Test insertion
        print(f"\n--- Testing Data Insertion ---")
        test_table = user_tables[0] if user_tables else None
        if test_table:
            # Get column names excluding id and created
            cursor.execute(f"PRAGMA table_info({test_table})")
            columns = [col[1] for col in cursor.fetchall() if col[1] not in ['id', 'created']]
            
            # Create test data
            test_values = [1.0] * len(columns)
            placeholders = ','.join(['?'] * len(columns))
            column_names = ','.join(columns)
            
            # Insert test data
            cursor.execute(f"""
                INSERT INTO {test_table} ({column_names})
                VALUES ({placeholders})
            """, test_values)
            conn.commit()
            print(f"✓ Successfully inserted test data into {test_table}")
            
            # Clean up test data
            cursor.execute(f"DELETE FROM {test_table} WHERE id = last_insert_rowid()")
            conn.commit()
            print(f"✓ Successfully cleaned up test data")
        
        conn.close()
        print("\n✓ Database diagnosis completed")
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    diagnose_database() 