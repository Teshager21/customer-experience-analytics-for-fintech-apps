import os
import tempfile
from unittest.mock import patch, MagicMock, call

import pandas as pd
import pytest

from data.collect_reviews import (
    PlayStoreReviewScraper,
    ReviewPreprocessor,
    scrape_all_banks,
)

# Sample data used across tests
MOCK_PAGE_1 = (
    [
        {"content": "Awesome app!", "score": 5, "at": "2024-01-01T12:00:00Z"},
        {"content": "Needs work", "score": 3, "at": "2024-01-02T12:00:00Z"},
    ],
    "next-token",
)

MOCK_PAGE_2 = (
    [
        {"content": "Worst app ever", "score": 1, "at": "2024-01-03T12:00:00Z"},
    ],
    None,  # No more pages
)


@pytest.fixture
def sample_raw_df():
    return pd.DataFrame(
        [
            {"content": "Great!", "score": 5, "at": "2024-01-01T12:00:00Z"},
            {"content": "Bad.", "score": 1, "at": "2024-01-01T12:00:00Z"},
            {
                "content": "Great!",
                "score": 5,
                "at": "2024-01-01T12:00:00Z",
            },  # Duplicate
            {"content": None, "score": 4, "at": "2024-01-04T12:00:00Z"},  # Null review
        ]
    )


@patch("data.collect_reviews.reviews")
def test_fetch_reviews_with_pagination(mock_reviews):
    # Simulate two pages
    mock_reviews.side_effect = [MOCK_PAGE_1, MOCK_PAGE_2]

    scraper = PlayStoreReviewScraper("com.example.app", "TestBank", max_reviews=5)
    df = scraper.fetch_reviews()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "content" in df.columns
    assert df.iloc[0]["content"] == "Awesome app!"

    assert mock_reviews.call_count == 2
    mock_reviews.assert_has_calls(
        [
            call(
                "com.example.app",
                lang="en",
                country="us",
                sort=2,
                count=5,
                filter_score_with=None,
                continuation_token=None,
            ),
            call(
                "com.example.app",
                lang="en",
                country="us",
                sort=2,
                count=3,
                filter_score_with=None,
                continuation_token="next-token",
            ),
        ]
    )


def test_clean_reviews_removes_duplicates_and_nulls(sample_raw_df):
    cleaned = ReviewPreprocessor.clean_reviews(sample_raw_df, "TestBank")

    assert isinstance(cleaned, pd.DataFrame)
    assert len(cleaned) == 2  # Deduplicated and nulls dropped
    assert "review" in cleaned.columns
    assert cleaned["bank"].iloc[0] == "TestBank"
    assert cleaned["source"].iloc[0] == "Google Play"


@patch("data.collect_reviews.PlayStoreReviewScraper")
@patch("data.collect_reviews.pd.DataFrame.to_csv")
def test_scrape_all_banks_saves_cleaned_and_combined(mock_to_csv, mock_scraper_cls):
    # Setup mock scraper
    mock_scraper = MagicMock()
    mock_scraper.fetch_reviews.return_value = pd.DataFrame(
        [{"content": "Nice", "score": 4, "at": "2024-01-01T00:00:00Z"}]
    )
    mock_scraper_cls.side_effect = lambda app_id, bank_name, max_reviews: mock_scraper

    app_dict = {"TestBank": "com.example.app"}

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "combined.csv")
        scrape_all_banks(app_dict, output_path, max_reviews=5)

        # Check scraper was created
        mock_scraper_cls.assert_called_once_with("com.example.app", "TestBank", 5)

        # Check if to_csv was called for:
        # - raw file
        # - cleaned per bank
        # - final combined dataset
        assert mock_to_csv.call_count == 3
        saved_paths = [args[0] for args, _ in mock_to_csv.call_args_list]
        assert any("raw" in path for path in saved_paths)
        assert any("processed" in path for path in saved_paths)
        assert output_path in saved_paths
