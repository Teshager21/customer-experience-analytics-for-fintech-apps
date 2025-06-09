import oracledb

# Connect using thin mode (no Oracle client required)
connection = oracledb.connect(user="system", password="oracle", dsn="localhost/XEPDB1")

print("✅ Connected to Oracle XE successfully!")
connection.close()
