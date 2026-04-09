# test_connection.py
import mysql.connector
import requests
import time

print("🔍 Testing Family Healthcare Assistant Setup")
print("=" * 50)

# Test 1: MySQL Connection
print("\n1. Testing MySQL connection...")
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="9850337042",
        database="healthcare",
        connection_timeout=5
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM members")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f"✅ MySQL connected successfully! Found {count} members in database")
except Exception as e:
    print(f"❌ MySQL connection failed: {e}")
    print("   Run: mysql -u root -p")
    print("   Enter password: 9850337042")
    print("   Then run: CREATE DATABASE healthcare;")

# Test 2: Backend Server
print("\n2. Testing backend server...")
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend running! Database: {data.get('database', 'unknown')}")
    else:
        print(f"❌ Backend returned status {response.status_code}")
except Exception as e:
    print(f"❌ Backend not reachable: {e}")
    print("   Run: cd backend && python app.py")

# Test 3: Frontend
print("\n3. Testing frontend...")
try:
    response = requests.get("http://localhost:5173", timeout=2)
    if response.status_code == 200:
        print("✅ Frontend running on http://localhost:5173")
    else:
        print(f"❌ Frontend returned status {response.status_code}")
except Exception as e:
    print(f"❌ Frontend not reachable: {e}")
    print("   Run: cd frontend && npm run dev")

print("\n" + "=" * 50)
print("📝 Summary:")
print("- If all tests passed, open http://localhost:5173 in your browser")
print("- If MySQL failed, follow the commands in Step 1-3 above")
print("- If backend failed, run: cd backend && python app.py")
print("- If frontend failed, run: cd frontend && npm run dev")