import duckdb
import os

# ✅ Define database path
DB_PATH = "uploads/intelligent_data_lake.duckdb"

# ✅ Create database connection
conn = duckdb.connect(DB_PATH)

# ✅ Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

def initialize_database():
    """Initialize DuckDB and create necessary tables if they don't exist."""
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS file_metadata (
            id UUID DEFAULT uuid(),
            table_name TEXT UNIQUE NOT NULL,
            file_name TEXT,
            file_type TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
        """)
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

# ✅ Run database initialization
initialize_database()
