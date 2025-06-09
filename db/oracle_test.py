import oracledb

# Connect using thin mode (no Oracle client required)
connection = oracledb.connect(
    user="myappuser", password="My$ecurePassw0rd", dsn="localhost/XEPDB1"
)
print("✅ Connected to Oracle XE successfully!")

with connection.cursor() as cursor:
    # 1. List all users
    print("\n👥 Users:")
    cursor.execute("SELECT username FROM all_users ORDER BY username")
    for user in cursor.fetchall():
        print("-", user[0])

    # 2. List all tables in the current schema
    print("\n📦 Tables in current schema:")
    cursor.execute("SELECT table_name FROM user_tables")
    for table in cursor.fetchall():
        print("-", table[0])

    # 3. Describe the BANKS table
    print("\n🔍 BANKS table schema:")
    try:
        cursor.execute(
            "SELECT column_name, data_type "
            "FROM user_tab_columns "
            "WHERE table_name = 'BANKS'"
        )
        for col in cursor.fetchall():
            print(f"- {col[0]} ({col[1]})")
    except Exception as e:
        print("❌ BANKS table not found or error:", e)

    # 4. Describe the REVIEWS table
    print("\n🔍 REVIEWS table schema:")
    try:
        cursor.execute(
            "SELECT column_name, data_type "
            "FROM user_tab_columns "
            "WHERE table_name = 'REVIEWS'"
        )
        for col in cursor.fetchall():
            print(f"- {col[0]} ({col[1]})")
    except Exception as e:
        print("❌ REVIEWS table not found or error:", e)

connection.close()
