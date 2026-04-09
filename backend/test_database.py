# backend/test_database.py
from db import get_db
import traceback

print("🧪 Testing database connection...")

try:
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Test query
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"✅ Database connected. Tables found: {len(tables)}")
    
    for table in tables:
        table_name = list(table.values())[0]
        print(f"   - {table_name}")
        
        # Show table structure
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print(f"     Columns: {[col['Field'] for col in columns]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database test failed: {e}")
    traceback.print_exc()