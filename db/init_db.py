import os
import oracledb
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# === Oracle Connection Settings from env ===
ORACLE_USER = os.getenv("ORACLE_USER", "system")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "oracle")
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = os.getenv("ORACLE_PORT", "1521")
ORACLE_SID = os.getenv("ORACLE_SID", "XEPDB1")
SCHEMA_FILE = os.getenv("SCHEMA_FILE", "db/schema.sql")

# Create DSN using oracledb.makedsn
dsn = oracledb.makedsn(ORACLE_HOST, ORACLE_PORT, service_name=ORACLE_SID)


def execute_schema(cursor, filepath):
    logging.info(f"Loading schema from: {filepath}")
    with open(filepath, "r") as file:
        sql_script = file.read()

    # Split on ';' and filter empty or comment-only statements
    statements = [
        stmt.strip()
        for stmt in sql_script.split(";")
        if stmt.strip() and not stmt.strip().startswith("--")
    ]

    for stmt in statements:
        try:
            logging.info(f"Executing:\n{stmt[:80]}...")
            cursor.execute(stmt)
        except oracledb.DatabaseError as e:
            logging.error(f"Error executing statement:\n{stmt}\n{e}")
            raise


def main():
    logging.info("Connecting to Oracle XE database...")
    try:
        with oracledb.connect(
            user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=dsn
        ) as connection:
            with connection.cursor() as cursor:
                execute_schema(cursor, SCHEMA_FILE)
                connection.commit()
                logging.info("Database schema initialized successfully.")
    except oracledb.DatabaseError as e:
        logging.error(f"Database connection failed: {e}")
        raise


if __name__ == "__main__":
    main()
