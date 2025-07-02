#!/usr/bin/env python3
"""
Utility script to query and view merged data from the SQLite database.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import argparse

def connect_to_db():
    """Connect to the database"""
    return sqlite3.connect("../instance/flaskr.sqlite")

def get_recent_data(limit=100, hours=None):
    """Get recent data from the database"""
    conn = connect_to_db()
    
    if hours:
        # Get data from the last N hours
        cutoff_time = datetime.now() - timedelta(hours=hours)
        query = """
            SELECT * FROM merged_data 
            WHERE timestamp >= ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(cutoff_time.isoformat(), limit))
    else:
        # Get the most recent N records
        query = "SELECT * FROM merged_data ORDER BY timestamp DESC LIMIT ?"
        df = pd.read_sql_query(query, conn, params=(limit,))
    
    conn.close()
    return df

def get_data_by_source(data_source, limit=100):
    """Get data from a specific source"""
    conn = connect_to_db()
    query = """
        SELECT * FROM merged_data 
        WHERE data_source = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(data_source, limit))
    conn.close()
    return df

def get_data_summary():
    """Get a summary of the data in the database"""
    conn = connect_to_db()
    
    # Get total records
    total_query = "SELECT COUNT(*) as total FROM merged_data"
    total = conn.execute(total_query).fetchone()[0]
    
    # Get records by source
    source_query = """
        SELECT data_source, COUNT(*) as count 
        FROM merged_data 
        GROUP BY data_source
    """
    sources = pd.read_sql_query(source_query, conn)
    
    # Get date range
    date_query = """
        SELECT 
            MIN(timestamp) as earliest,
            MAX(timestamp) as latest
        FROM merged_data
    """
    date_range = pd.read_sql_query(date_query, conn)
    
    conn.close()
    
    return {
        'total_records': total,
        'by_source': sources,
        'date_range': date_range
    }

def export_to_csv(filename=None, hours=None, limit=None):
    """Export data to CSV"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exported_data_{timestamp}.csv"
    
    df = get_recent_data(limit=limit or 10000, hours=hours)
    df.to_csv(filename, index=False)
    print(f"Data exported to: {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description='Query merged data from the database')
    parser.add_argument('--limit', type=int, default=100, help='Number of records to retrieve')
    parser.add_argument('--hours', type=int, help='Get data from last N hours')
    parser.add_argument('--source', choices=['hmi', 'r_values', 'channel_data'], help='Filter by data source')
    parser.add_argument('--summary', action='store_true', help='Show data summary')
    parser.add_argument('--export', help='Export to CSV file')
    parser.add_argument('--export-hours', type=int, help='Export data from last N hours')
    
    args = parser.parse_args()
    
    if args.summary:
        summary = get_data_summary()
        print("\n=== DATA SUMMARY ===")
        print(f"Total records: {summary['total_records']}")
        print("\nRecords by source:")
        print(summary['by_source'].to_string(index=False))
        print("\nDate range:")
        print(summary['date_range'].to_string(index=False))
        
    elif args.export:
        export_to_csv(args.export, hours=args.export_hours, limit=args.limit)
        
    elif args.source:
        df = get_data_by_source(args.source, args.limit)
        print(f"\n=== {args.source.upper()} DATA (Last {len(df)} records) ===")
        print(df.to_string(index=False))
        
    else:
        df = get_recent_data(args.limit, args.hours)
        print(f"\n=== RECENT DATA (Last {len(df)} records) ===")
        print(df.to_string(index=False))

if __name__ == '__main__':
    main() 