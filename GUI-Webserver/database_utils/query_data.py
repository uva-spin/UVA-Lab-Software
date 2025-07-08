#!/usr/bin/env python3
"""
Utility script to query and view data from the SQLite database using schema-defined tables.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import argparse
from config import DATABASE_PATH, DATABASE_NAME

def connect_to_db():
    """Connect to the database"""
    return sqlite3.connect(f"{DATABASE_PATH}/{DATABASE_NAME}")

def get_recent_data(table_name='HMI', limit=100, hours=None):
    """Get recent data from the specified table"""
    conn = connect_to_db()
    
    if hours:
        # Get data from the last N hours
        cutoff_time = datetime.now() - timedelta(hours=hours)
        query = f"""
            SELECT * FROM {table_name} 
            WHERE created >= ? 
            ORDER BY created DESC 
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(cutoff_time.isoformat(), limit))
    else:
        # Get the most recent N records
        query = f"SELECT * FROM {table_name} ORDER BY created DESC LIMIT ?"
        df = pd.read_sql_query(query, conn, params=(limit,))
    
    conn.close()
    return df

def get_combined_data(hours=None, limit=None):
    """Get combined data from all tables"""
    conn = connect_to_db()
    
    try:
        # Get all tables, excluding system tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # Filter out system tables
        system_tables = ['sqlite_sequence', 'sqlite_stat1', 'sqlite_stat2', 'sqlite_stat3', 'sqlite_stat4']
        tables = [table for table in all_tables if table not in system_tables]
        
        all_data = {}
        
        for table_name in tables:
            if hours:
                # Get data from the last N hours
                cutoff_time = datetime.now() - timedelta(hours=hours)
                query = f"""
                    SELECT * FROM {table_name} 
                    WHERE created >= ? 
                    ORDER BY created DESC 
                    LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=(cutoff_time.isoformat(), limit or 1000))
            else:
                # Get the most recent N records
                query = f"SELECT * FROM {table_name} ORDER BY created DESC LIMIT ?"
                df = pd.read_sql_query(query, conn, params=(limit or 100,))
            
            all_data[table_name] = df
        
        return all_data
        
    except Exception as e:
        print(f"Error getting combined data: {e}")
        return {}
    finally:
        conn.close()

def get_latest_from_all_tables():
    """Get the latest record from each table"""
    conn = connect_to_db()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # Filter out system tables
        system_tables = ['sqlite_sequence', 'sqlite_stat1', 'sqlite_stat2', 'sqlite_stat3', 'sqlite_stat4']
        tables = [table for table in all_tables if table not in system_tables]
        
        latest_data = {}
        
        for table_name in tables:
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY created DESC LIMIT 1")
            latest_record = cursor.fetchone()
            
            if latest_record:
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Create dictionary
                record_dict = {}
                for i, column in enumerate(columns):
                    record_dict[column] = latest_record[i]
                
                latest_data[table_name] = record_dict
        
        return latest_data
        
    except Exception as e:
        print(f"Error getting latest data from all tables: {e}")
        return {}
    finally:
        conn.close()

def get_data_by_table(table_name, limit=100):
    """Get data from a specific table"""
    conn = connect_to_db()
    query = f"""
        SELECT * FROM {table_name} 
        ORDER BY created DESC 
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def get_data_summary():
    """Get a summary of the data in the database"""
    conn = connect_to_db()
    
    # Get all tables, excluding system tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    # Filter out system tables
    system_tables = ['sqlite_sequence', 'sqlite_stat1', 'sqlite_stat2', 'sqlite_stat3', 'sqlite_stat4']
    tables = [table for table in all_tables if table not in system_tables]
    
    summary = {}
    total_records = 0
    
    for table_name in tables:
        # Get total records for this table
        cursor.execute(f"SELECT COUNT(*) as total FROM {table_name}")
        table_total = cursor.fetchone()[0]
        total_records += table_total
        
        # Get date range for this table
        cursor.execute(f"""
            SELECT 
                MIN(created) as earliest,
                MAX(created) as latest
            FROM {table_name}
        """)
        date_range = cursor.fetchone()
        
        summary[table_name] = {
            'total_records': table_total,
            'earliest': date_range[0] if date_range[0] else None,
            'latest': date_range[1] if date_range[1] else None
        }
    
    conn.close()
    
    return {
        'total_records': total_records,
        'tables': summary
    }

def export_to_csv(table_name='HMI', filename=None, hours=None, limit=None):
    """Export data to CSV"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exported_{table_name}_data_{timestamp}.csv"
    
    df = get_recent_data(table_name=table_name, limit=limit or 10000, hours=hours)
    df.to_csv(filename, index=False)
    print(f"Data exported to: {filename}")
    return filename

def export_combined_to_csv(filename=None, hours=None, limit=None):
    """Export combined data from all tables to CSV"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exported_combined_data_{timestamp}.csv"
    
    all_data = get_combined_data(hours=hours, limit=limit)
    
    # Combine all dataframes
    combined_dfs = []
    for table_name, df in all_data.items():
        if not df.empty:
            # Add table prefix to columns to avoid conflicts
            df = df.copy()
            df.columns = [f"{table_name}_{col}" if col != 'created' else f"{table_name}_timestamp" 
                         for col in df.columns]
            combined_dfs.append(df)
    
    if combined_dfs:
        combined_df = pd.concat(combined_dfs, axis=1, sort=False)
        combined_df.to_csv(filename, index=False)
        print(f"Combined data exported to: {filename}")
        return filename
    else:
        print("No data to export")
        return None

def main():
    parser = argparse.ArgumentParser(description='Query and export database data')
    parser.add_argument('--table', default='HMI', choices=['HMI', 'Pressures', 'Flow_Rates'],
                       help='Table to query (default: HMI)')
    parser.add_argument('--limit', type=int, default=100,
                       help='Number of records to retrieve (default: 100)')
    parser.add_argument('--hours', type=int,
                       help='Get data from last N hours instead of using limit')
    parser.add_argument('--export', action='store_true',
                       help='Export data to CSV file')
    parser.add_argument('--summary', action='store_true',
                       help='Show database summary')
    parser.add_argument('--latest', action='store_true',
                       help='Show latest data from all tables')
    parser.add_argument('--combined', action='store_true',
                       help='Get combined data from all tables')
    parser.add_argument('--export-combined', action='store_true',
                       help='Export combined data from all tables to CSV (We shouldnt need to use this)')
    
    args = parser.parse_args()
    
    if args.summary:
        summary = get_data_summary()
        print("Database Summary:")
        print(f"Total records: {summary['total_records']}")
        print("\nBy table:")
        for table, info in summary['tables'].items():
            print(f"  {table}: {info['total_records']} records")
            if info['earliest'] and info['latest']:
                print(f"    Date range: {info['earliest']} to {info['latest']}")
    
    elif args.latest:
        latest_data = get_latest_from_all_tables()
        print("Latest data from all tables:")
        for table, data in latest_data.items():
            print(f"\n{table}:")
            for key, value in data.items():
                print(f"  {key}: {value}")
    
    elif args.combined:
        all_data = get_combined_data(hours=args.hours, limit=args.limit)
        print("Combined data from all tables:")
        for table, df in all_data.items():
            print(f"\n{table} ({len(df)} records):")
            print(df.head())
    
    else:
        df = get_recent_data(table_name=args.table, limit=args.limit, hours=args.hours)
        print(f"Retrieved {len(df)} records from {args.table} table:")
        print(df.head())
        
        if args.export:
            export_to_csv(table_name=args.table, hours=args.hours, limit=args.limit)
    
    if args.export_combined:
        export_combined_to_csv(hours=args.hours, limit=args.limit)

if __name__ == '__main__':
    main() 