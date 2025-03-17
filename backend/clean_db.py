import duckdb

# ✅ Connect to DuckDB
DB_PATH = "uploads/intelligent_data_lake.duckdb"
conn = duckdb.connect(DB_PATH)

# ✅ Fetch all table names
tables = conn.execute("SHOW TABLES").fetchall()

# ✅ Drop each table
for table in tables:
    conn.execute(f"DROP TABLE {table[0]};")

print("✅ All tables deleted successfully!")

# ✅ Close connection
conn.close()