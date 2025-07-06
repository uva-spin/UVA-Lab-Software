#!/usr/bin/env python3
"""
Diagnostic script to check database status and test data insertion
"""

import sqlite3
import os
from datetime import datetime

def diagnose_database():
    """Diagnose database issues"""
    db_path = "../instance/flaskr.sqlite"
    
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
        
        # Test HMI insertion
        try:
            hmi_data = [25.5, 26.2, 24.8, 25.1, 26.0, 25.3, 25.7, 25.9, 25.4, 25.6, 25.8, 25.2, 25.0, 25.1, 25.3, 25.5, 25.7, 25.9]
            cursor.execute('''
                INSERT INTO hmi (
                    fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                    pt501_ai, pt502_ai, pt503_ai, pt504_ai, purity_downstream,
                    purity_upstream, ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                    ti504_ai, ti505_ai, ti523_ai
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', hmi_data)
            conn.commit()
            print("✅ HMI data insertion successful")
        except Exception as e:
            print(f"❌ HMI data insertion failed: {e}")
        
        # Test LabJack insertion
        try:
            cursor.execute('INSERT INTO labjack (pressure_1) VALUES (?)', (101.3,))
            conn.commit()
            print("✅ LabJack data insertion successful")
        except Exception as e:
            print(f"❌ LabJack data insertion failed: {e}")
        
        # Test Teledyne insertion
        try:
            cursor.execute('INSERT INTO teledyne (flow_1, flow_2, flow_3) VALUES (?, ?, ?)', (30.1, 30.2, 30.3))
            conn.commit()
            print("✅ Teledyne data insertion successful")
        except Exception as e:
            print(f"❌ Teledyne data insertion failed: {e}")
        
        # Check final counts
        print(f"\n--- Final Record Counts ---")
        for table_name in user_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} records")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    diagnose_database() 