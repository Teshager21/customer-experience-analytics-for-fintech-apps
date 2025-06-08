# tests/pipeline/test_main_pipeline.py

import pandas as pd
import tempfile
from pathlib import Path

from pipeline.sentiment_thematic_pipeline import run_pipeline


def test_run_pipeline_end_to_end():
    """Test the full pipeline with mock input and output files."""

    # Create sample input data
    test_df = pd.DataFrame(
        {
            "review": [
                "I can't log in to my account. Very frustrating!",
                "Great app! Love the new design and features.",
                "Slow transactions and poor support response.",
            ]
        }
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "test_input.csv"
        output_path = Path(temp_dir) / "test_output.csv"

        # Save sample input to CSV
        test_df.to_csv(input_path, index=False)

        # Run pipeline
        run_pipeline(str(input_path), str(output_path))

        # Check output file exists
        assert output_path.exists(), "Output CSV was not created"

        # Load and verify output structure
        result_df = pd.read_csv(output_path)
        expected_columns = {
            "review_text",
            "cleaned_text",
            "sentiment_label",
            "sentiment_score",
            "keywords",
            "themes",
        }
        assert expected_columns.issubset(
            result_df.columns
        ), f"Missing expected columns: {expected_columns - set(result_df.columns)}"

        # Check if sentiment and theme are non-null
        assert result_df["sentiment_label"].notnull().all()
        assert result_df["themes"].notnull().all()
