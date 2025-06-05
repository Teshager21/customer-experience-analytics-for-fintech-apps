"""
collect_reviews.py

This script scrapes user reviews from the Google Play Store for mobile banking
applicationsof Ethiopian banks and performs basic cleaning and preprocessing.
The output is saved as a CSV file for further analysis.

Author: 10 Academy - AIM Week 2 Participant
Date: 2025-06-05
"""

import os

# from datetime import datetime
from typing import Dict

import pandas as pd
from google_play_scraper import Sort, reviews


class PlayStoreReviewScraper:
    """
    Scrapes reviews for a given app from the Google Play Store.
    """

    def __init__(self, app_id: str, bank_name: str, max_reviews: int = 500):
        self.app_id = app_id
        self.bank_name = bank_name
        self.max_reviews = max_reviews

    def fetch_reviews(self) -> pd.DataFrame:
        """
        Fetch reviews using google-play-scraper.

        Returns:
            pd.DataFrame: Raw scraped reviews.
        """
        all_reviews = []
        count = 0
        try:
            while count < self.max_reviews:
                rvws, _ = reviews(
                    self.app_id,
                    lang="en",
                    country="us",
                    sort=Sort.NEWEST,
                    count=min(200, self.max_reviews - count),
                    filter_score_with=None,
                )
                if not rvws:
                    break
                all_reviews.extend(rvws)
                count = len(all_reviews)
        except Exception as e:
            print(f"[ERROR] Failed to fetch reviews for {self.bank_name}: {e}")
        return pd.DataFrame(all_reviews)


class ReviewPreprocessor:
    """
    Cleans and standardizes scraped review data.
    """

    @staticmethod
    def clean_reviews(df: pd.DataFrame, bank_name: str) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        df = df[["content", "score", "at"]]
        df.rename(
            columns={"content": "review", "score": "rating", "at": "date"}, inplace=True
        )
        df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        df.drop_duplicates(subset=["review", "date"], inplace=True)
        df.dropna(subset=["review", "rating"], inplace=True)
        df["bank"] = bank_name
        df["source"] = "Google Play"
        return df


def scrape_all_banks(
    app_dict: Dict[str, str], output_path: str, max_reviews: int = 500
):
    """
    Coordinates the scraping and preprocessing process for all banks.

    Args:
        app_dict: Dictionary mapping bank names to app IDs.
        output_path: CSV file path to save the results.
        max_reviews: Maximum reviews to fetch per bank.
    """
    all_dfs = []
    for bank, app_id in app_dict.items():
        print(f"[INFO] Scraping {bank}...")
        scraper = PlayStoreReviewScraper(app_id, bank, max_reviews)
        raw_df = scraper.fetch_reviews()
        clean_df = ReviewPreprocessor.clean_reviews(raw_df, bank)
        all_dfs.append(clean_df)

    final_df = pd.concat(all_dfs, ignore_index=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Saved {len(final_df)} reviews to {output_path}")


if __name__ == "__main__":
    BANK_APPS = {
        "CBE": "com.cbe.mobile",
        "BOA": "com.bankofabyssinia.boamobile",
        "Dashen": "com.dashenbank.app",
    }
    OUTPUT_CSV = "data/processed/cleaned_reviews.csv"
    scrape_all_banks(BANK_APPS, OUTPUT_CSV, max_reviews=500)
