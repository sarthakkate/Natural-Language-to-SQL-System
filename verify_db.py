#!/usr/bin/env python
"""Quick database verification script"""
import sqlite3
import os

db_path = 'clinic.db'
if not os.path.exists(db_path):
    print("✗ clinic.db not found")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get table names
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    print("✓ Database tables found:", tables)
    
    # Get row counts
    for table in tables:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        print(f"  - {table}: {count} rows")
    
    conn.close()
    print("\n✓ Database verification PASSED")
    
except Exception as e:
    print(f"✗ Database error: {e}")
    exit(1)
