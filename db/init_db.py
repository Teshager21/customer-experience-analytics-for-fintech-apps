"""
Initialize Oracle database schema using SQL script.
Creates a new Oracle user if needed, then initializes schema under that user.

Usage:
    python db/init_db.py
"""

import logging
import os
import re

import oracledb
from dotenv import load_dotenv

from analytics.path_config import DB_DIR

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# Oracle admin connection parameters (privileged user to create new user)
ORACLE_ADMIN_USER = os.getenv("ORACLE_ADMIN_USER", "system")
ORACLE_ADMIN_PASSWORD = os.getenv("ORACLE_ADMIN_PASSWORD", "oracle")

# Oracle host/port/SID (same for all connections)
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = os.getenv("ORACLE_PORT", "1521")
ORACLE_SID = os.getenv("ORACLE_SID", "XEPDB1")

# New user to create and use
NEW_ORACLE_USER = os.getenv("NEW_ORACLE_USER", "myappuser")
NEW_ORACLE_PASSWORD = os.getenv("NEW_ORACLE_PASSWORD", "securepass123")

SCHEMA_FILE = os.path.join(DB_DIR, "schema.sql")

# DSN string for connections
dsn = oracledb.makedsn(ORACLE_HOST, ORACLE_PORT, service_name=ORACLE_SID)


def create_user_if_not_exists(cursor, username: str, password: str):
    """Create user with given username and password if it does not already exist."""
    logging.info(f"Checking if user '{username}' exists...")

    cursor.execute(
        "SELECT COUNT(*) FROM dba_users WHERE username = :username", [username.upper()]
    )
    (count,) = cursor.fetchone()

    if count == 0:
        logging.info(f"User '{username}' does not exist. Creating user...")
        try:
            cursor.execute(f'CREATE USER {username} IDENTIFIED BY "{password}"')
            cursor.execute(f"GRANT CONNECT TO {username}")
            cursor.execute(
                f"GRANT CREATE SESSION, CREATE TABLE, "
                f"CREATE SEQUENCE, CREATE VIEW TO {username}"
            )
            cursor.execute(f"ALTER USER {username} QUOTA UNLIMITED ON USERS")
            logging.info(f"User '{username}' created successfully.")
        except Exception as e:
            logging.error(f"Failed to create user '{username}': {e}")
            raise
    else:
        logging.info(f"User '{username}' already exists. Skipping creation.")


def execute_schema(cursor, filepath: str) -> None:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Schema file not found: {filepath}")

    logging.info(f"Loading schema from: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            raw_sql = file.read()

        def remove_sql_comments(sql: str) -> str:
            sql = re.sub(r"--.*?(\r\n|\r|\n)", "\n", sql)
            sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
            return sql

        def split_statements(script: str) -> list:
            statements = []
            buffer = []

            lines = script.splitlines()
            inside_plsql = False

            for line in lines:
                stripped = line.strip()

                if not inside_plsql and stripped.upper().startswith(
                    "CREATE OR REPLACE TRIGGER"
                ):
                    inside_plsql = True

                if inside_plsql:
                    buffer.append(line)
                    if stripped == "/":  # End of PL/SQL block
                        statements.append("\n".join(buffer[:-1]).strip())  # Exclude '/'
                        buffer = []
                        inside_plsql = False
                else:
                    if stripped.endswith(";"):
                        buffer.append(line)
                        statements.append("\n".join(buffer).strip().rstrip(";"))
                        buffer = []
                    else:
                        buffer.append(line)

            # Remaining buffer
            if buffer:
                statements.append("\n".join(buffer).strip().rstrip(";"))

            return [
                remove_sql_comments(stmt).strip() for stmt in statements if stmt.strip()
            ]

        statements = split_statements(raw_sql)

        logging.info(f"Executing {len(statements)} SQL statements...")

        for stmt in statements:
            try:
                logging.info(f"Executing SQL statement:\n{stmt[:500]}")
                cursor.execute(stmt)
            except oracledb.DatabaseError as exec_err:
                (error_obj,) = exec_err.args
                if error_obj.code == 955:
                    # ORA-00955: name is already used by an existing object
                    obj_type = "object"
                    if "TABLE" in stmt.upper():
                        obj_type = "table"
                    elif "SEQUENCE" in stmt.upper():
                        obj_type = "sequence"
                    elif "TRIGGER" in stmt.upper():
                        obj_type = "trigger"
                    elif "VIEW" in stmt.upper():
                        obj_type = "view"

                    logging.warning(f"Skipped creating {obj_type}: already exists.")
                else:
                    logging.error(
                        f"Failed to execute SQL:\n{stmt[:200]}"
                        f"...\nError: {error_obj.message}"
                    )
                    raise

    except Exception as e:
        logging.error(f"Failed to load or execute schema file: {e}")
        raise


def main():
    # Step 1: Connect as admin to create user
    logging.info(f"Connecting as admin user '{ORACLE_ADMIN_USER}' to create user...")
    try:
        with oracledb.connect(
            user=ORACLE_ADMIN_USER, password=ORACLE_ADMIN_PASSWORD, dsn=dsn
        ) as admin_conn:
            with admin_conn.cursor() as cursor:
                create_user_if_not_exists(cursor, NEW_ORACLE_USER, NEW_ORACLE_PASSWORD)
                admin_conn.commit()
    except oracledb.DatabaseError as e:
        logging.error(f"Failed to create user '{NEW_ORACLE_USER}': {e}")
        raise

    # Step 2: Connect as the new user to initialize schema
    logging.info(f"Connecting as new user '{NEW_ORACLE_USER}' to initialize schema...")
    try:
        with oracledb.connect(
            user=NEW_ORACLE_USER, password=NEW_ORACLE_PASSWORD, dsn=dsn
        ) as user_conn:
            with user_conn.cursor() as cursor:
                cursor.execute("SELECT user FROM dual")
                current_user = cursor.fetchone()[0]
                logging.info(f"Connected as Oracle user: {current_user}")

                execute_schema(cursor, SCHEMA_FILE)
                user_conn.commit()
                logging.info("✅ Database schema initialized successfully.")

                # Optional: Log all user tables
                cursor.execute("SELECT table_name FROM user_tables")
                tables = cursor.fetchall()
                logging.info(f"Tables created in schema: {[t[0] for t in tables]}")

    except oracledb.DatabaseError as e:
        logging.error(f"Oracle DB connection or execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
