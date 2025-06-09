"""
Seed the Oracle database with review data from a CSV file.

Each row in the CSV represents a review and is inserted into the `reviews` table.

Usage:
    python db/seed_reviews.py [optional_csv_path]
"""

import csv
import json
import logging
import os
import sys

import oracledb
from dotenv import load_dotenv

from analytics.path_config import DATA_DIR

# ─────────────────────────────
# 🔧 Setup & Config
# ─────────────────────────────
load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Oracle DB Config
ORACLE_USER = os.getenv("NEW_ORACLE_USER", "myappuser")
ORACLE_PASSWORD = os.getenv("NEW_ORACLE_PASSWORD", "My$ecurePassw0rd")
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = os.getenv("ORACLE_PORT", "1521")
ORACLE_SID = os.getenv("ORACLE_SID", "XEPDB1")

DSN = oracledb.makedsn(ORACLE_HOST, ORACLE_PORT, service_name=ORACLE_SID)


# ─────────────────────────────
# 🔧 Helpers
# ─────────────────────────────
def format_json_field(raw: str) -> str:
    """
    Convert a stringified list with single quotes to valid JSON string.
    Returns '[]' if invalid.
    """
    try:
        return json.dumps(json.loads(raw.replace("'", '"')))
    except json.JSONDecodeError:
        logging.warning(f"⚠️ Failed to parse JSON field: {raw}")
        return "[]"


def insert_reviews_from_csv(csv_path: str) -> None:
    """
    Reads reviews from the CSV and inserts them into the Oracle `REVIEWS` table.
    """
    logging.info(f"📥 Starting to insert data from: {csv_path}")

    if not os.path.exists(csv_path):
        logging.error(f"❌ CSV file not found: {csv_path}")
        return

    try:
        with oracledb.connect(
            user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=DSN
        ) as conn:
            with conn.cursor() as cursor:
                # Log tables in current schema
                cursor.execute("SELECT table_name FROM user_tables")
                tables = [row[0] for row in cursor.fetchall()]
                logging.info(f"Existing tables in current schema: {tables}")

                # Insert the three banks first (if not exists)
                banks = ["BOA", "Dashen", "CBE"]
                for bank_name in banks:
                    try:
                        cursor.execute(
                            "INSERT INTO BANKS (NAME) VALUES (:name)", [bank_name]
                        )
                    except oracledb.IntegrityError:
                        # Bank already exists, skip
                        pass
                conn.commit()
                logging.info("✅ Banks table populated with initial banks.")

                # Build name→ID mapping
                cursor.execute("SELECT ID, NAME FROM BANKS")
                bank_name_to_id = {name: id for id, name in cursor.fetchall()}

                # Then proceed to read and insert rows
                with open(csv_path, mode="r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        bank_name = row["bank"]
                        bank_id = bank_name_to_id.get(bank_name)
                        if bank_id is None:
                            logging.warning(
                                f"⚠️ Skipping review for unknown bank: {bank_name}"
                            )
                            continue

                        cursor.execute(
                            (
                                "INSERT INTO REVIEWS ("
                                " REVIEW_TEXT, RATING, REVIEW_DATE, BANK_ID, SOURCE,"
                                " CLEANED_TEXT, SENTIMENT_LABEL, SENTIMENT_SCORE,"
                                " KEYWORDS, THEMES"
                                ") VALUES ("
                                ":review_text, :rating, TO_DATE(:date_value, "
                                "'YYYY-MM-DD'),"
                                " :bank_id, :source_value, :cleaned_text, "
                                ":sentiment_label,"
                                " :sentiment_score, :keywords, :themes"
                                ")"
                            ),
                            {
                                "review_text": row["review_text"],
                                "rating": float(row["rating"]),
                                "date_value": row["date"],
                                "bank_id": bank_name_to_id[row["bank"]],
                                "source_value": row["source"],
                                "cleaned_text": row["cleaned_text"],
                                "sentiment_label": row["sentiment_label"],
                                "sentiment_score": float(row["sentiment_score"]),
                                "keywords": format_json_field(row["keywords"]),
                                "themes": format_json_field(row["themes"]),
                            },
                        )

                conn.commit()
                logging.info("✅ Data inserted successfully.")

    except oracledb.DatabaseError as db_err:
        logging.error(f"❌ Database error: {db_err}")
        raise

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        raise


# ─────────────────────────────
# 🚀 Entry Point
# ─────────────────────────────
if __name__ == "__main__":
    default_csv_path = os.path.join(DATA_DIR, "outputs", "sentiment_theme_output.csv")
    csv_path = sys.argv[1] if len(sys.argv) > 1 else default_csv_path
    insert_reviews_from_csv(csv_path)
