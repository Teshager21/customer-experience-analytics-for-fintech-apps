import os
import time
from typing import Dict

import pandas as pd
from google_play_scraper import Sort, reviews


class PlayStoreReviewScraper:
    def __init__(self, app_id: str, bank_name: str, max_reviews: int = 500):
        self.app_id = app_id
        self.bank_name = bank_name
        self.max_reviews = max_reviews

    def fetch_reviews(self) -> pd.DataFrame:
        all_reviews = []
        count = 0
        try:
            while count < self.max_reviews:
                try:
                    rvws, _ = reviews(
                        self.app_id,
                        lang="en",
                        country="us",
                        sort=Sort.NEWEST,
                        count=min(200, self.max_reviews - count),
                        filter_score_with=None,
                    )
                except Exception as e:
                    print(f"[WARN] Retry due to error: {e}")
                    time.sleep(3)
                    continue
                if not rvws:
                    break
                all_reviews.extend(rvws)
                count = len(all_reviews)
        except Exception as e:
            print(f"[ERROR] Failed to fetch reviews for {self.bank_name}: {e}")
        return pd.DataFrame(all_reviews)


class ReviewPreprocessor:
    @staticmethod
    def clean_reviews(df: pd.DataFrame, bank_name: str) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        df = df[["content", "score", "at"]].copy()
        df.rename(
            columns={"content": "review", "score": "rating", "at": "date"}, inplace=True
        )
        df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        df.drop_duplicates(subset=["review", "date"], inplace=True)
        df.dropna(subset=["review", "rating"], inplace=True)
        df.loc[:, "bank"] = bank_name
        df.loc[:, "source"] = "Google Play"
        return df


def scrape_all_banks(
    app_dict: Dict[str, str], output_path: str, max_reviews: int = 500
):
    all_dfs = []
    for bank, app_id in app_dict.items():
        print(f"[INFO] Scraping {bank}...")
        scraper = PlayStoreReviewScraper(app_id, bank, max_reviews)
        raw_df = scraper.fetch_reviews()

        # Save raw data
        raw_path = f"data/raw/{bank}_raw_reviews.csv"
        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        raw_df.to_csv(raw_path, index=False)
        print(f"[INFO] Saved raw data for {bank} to {raw_path}")

        # Clean and validate
        clean_df = ReviewPreprocessor.clean_reviews(raw_df, bank)
        if len(clean_df) < 400:
            print(
                f"[WARNING] Only {len(clean_df)} cleaned reviews/ found for {bank} "
                f"(expected: 400+)"
            )

        # Save cleaned per bank
        clean_path = f"data/processed/{bank}_cleaned_reviews.csv"
        clean_df.to_csv(clean_path, index=False)
        print(f"[INFO] Saved cleaned data for {bank} to {clean_path}")

        if not clean_df.empty:
            all_dfs.append(clean_df)

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_df.to_csv(output_path, index=False)
        print(
            f"[SUCCESS] Saved combined dataset with {len(final_df)} reviews "
            f"to {output_path}"
        )

    else:
        print("[WARNING] No reviews were successfully scraped.")


if __name__ == "__main__":
    BANK_APPS = {
        "CBE": "com.combanketh.mobilebanking",
        "BOA": "com.boa.boaMobileBanking",
        "Dashen": "com.dashen.dashensuperapp",
    }
    OUTPUT_CSV = "data/processed/cleaned_reviews.csv"
    scrape_all_banks(BANK_APPS, OUTPUT_CSV, max_reviews=500)
