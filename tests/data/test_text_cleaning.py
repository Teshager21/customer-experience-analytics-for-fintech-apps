import pytest
from data.text_cleaning import preprocess_reviews


class TestPreprocessReviews:
    """Unit tests for the preprocess_reviews function in data.text_cleaning."""

    @pytest.mark.parametrize(
        "input_text, expected_output",
        [
            ("Best Mobile Banking App EVER!", "good mobile banking app"),
            ("It was good, but it doesn't work right.", "good not work right"),
            ("👌👍", ""),
            ("", ""),
            (None, ""),
            ("dedeb", "dedeb"),
        ],
    )
    def test_preprocess_reviews_valid_cases(self, input_text, expected_output):
        """Test that valid inputs are processed and cleaned correctly."""
        result = preprocess_reviews(input_text)
        assert (
            result == expected_output
        ), f"Expected '{expected_output}', got '{result}'"

    def test_preprocess_reviews_type_handling(self):
        """Test that non-string inputs do not raise errors."""
        assert preprocess_reviews(1234) == "1234"
        assert preprocess_reviews(True) == "true"
        assert preprocess_reviews(["test"]) == "test"

    def test_preprocess_reviews_stopwords_removal(self):
        """Ensure common stopwords are removed correctly."""
        text = "This is an example of a sentence with many stopwords."
        result = preprocess_reviews(text)
        # Token list depends on lemmatization
        assert "this" not in result
        assert "is" not in result
        assert "example" in result
        assert "sentence" in result
