import pandas as pd
import oracledb
import logging
from typing import Optional

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class OracleReviewLoader:
    """
    A class to handle Oracle DB connection and review data extraction.
    """

    def __init__(self, user: str, password: str, dsn: str) -> None:
        self.user = user
        self.password = password
        self.dsn = dsn
        self.conn: Optional[oracledb.Connection] = None

    def connect(self) -> None:
        """
        Establish a connection to the Oracle database.
        """
        try:
            self.conn = oracledb.connect(
                user=self.user, password=self.password, dsn=self.dsn
            )
            logger.info("Successfully connected to Oracle database.")
        except oracledb.Error as e:
            logger.error(f"Failed to connect to Oracle database: {e}", exc_info=True)
            raise ConnectionError(f"Could not connect to Oracle database: {e}") from e

    def disconnect(self) -> None:
        """
        Close the Oracle database connection.
        """
        if self.conn:
            try:
                self.conn.close()
                logger.info("Oracle database connection closed.")
            except oracledb.Error as e:
                logger.warning(
                    f"Error occurred while closing the database: {e}", exc_info=True
                )

    def fetch_reviews(self) -> pd.DataFrame:
        """
        Fetch reviews and metadata from the database.

        Returns:
            pd.DataFrame: DataFrame with bank_name, review_text, rating,
                          sentiment_label, keywords, and themes.
        """
        if self.conn is None:
            self.connect()

        assert self.conn is not None  # for mypy

        query = """
        SELECT
            b.NAME AS bank_name,
            r.REVIEW_TEXT,
            r.RATING,
            r.SENTIMENT_LABEL,
            r.KEYWORDS,
            r.THEMES
        FROM REVIEWS r
        JOIN BANKS b ON r.BANK_ID = b.ID
        WHERE r.SENTIMENT_LABEL IS NOT NULL AND r.THEMES IS NOT NULL
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            rows = []

            for row in cursor:
                # Convert CLOBs to string (e.g., from LOBs)
                clean_row = [col.read() if hasattr(col, "read") else col for col in row]
                rows.append(clean_row)

            df = pd.DataFrame(
                rows,
                columns=[
                    "bank_name",
                    "review_text",
                    "rating",
                    "sentiment_label",
                    "keywords",
                    "themes",
                ],
            )

            logger.info(f"Fetched {len(df)} review records from Oracle DB.")
            return df

        except Exception as e:
            logger.error(
                "Failed to execute query or load data into DataFrame.", exc_info=True
            )
            raise RuntimeError("Error fetching reviews from Oracle.") from e
