# import pytest
from features.keyword_extraction import extract_keywords


class TestExtractKeywords:
    """Unit tests for the extract_keywords function in features.keyword_extraction."""

    def test_extract_keywords_basic_functionality(self):
        """Test that keywords are extracted correctly from simple texts."""
        texts = [
            "This is a great app for finance",
            "The app has excellent features and great usability",
            "Finance tools and features are very helpful",
        ]
        result = extract_keywords(texts, top_k=3)

        assert isinstance(result, list)
        assert len(result) == len(texts)
        for keywords in result:
            assert isinstance(keywords, list)
            assert len(keywords) <= 3
            assert all(isinstance(kw, str) for kw in keywords)

    def test_extract_keywords_with_empty_strings(self):
        """Ensure that empty input strings return empty keyword lists."""
        texts = ["", "   ", "\n"]
        result = extract_keywords(texts, top_k=5)

        assert isinstance(result, list)
        assert all(isinstance(keywords, list) for keywords in result)
        assert all(len(keywords) == 0 for keywords in result)

    def test_extract_keywords_top_k_respected(self):
        """Ensure the function returns no more than top_k keywords per document."""
        texts = [
            "keyword1 keyword2 keyword3 keyword4 keyword5 keyword6",
            "keyword1 keyword2 keyword3",
        ]
        result = extract_keywords(texts, top_k=4)

        for keywords in result:
            assert (
                len(keywords) <= 4
            ), f"Expected ≤ 4 keywords, got {len(keywords)}: {keywords}"

    def test_extract_keywords_output_consistency(self):
        """Check consistency across runs (deterministic output)."""
        texts = ["finance app usability", "finance app usability"]
        result1 = extract_keywords(texts, top_k=2)
        result2 = extract_keywords(texts, top_k=2)

        assert result1 == result2

    def test_extract_keywords_edge_cases(self):
        """Test function with edge cases such as numbers and special characters."""
        texts = [
            "123 456 !@# $%^",  # mostly ignored by tokenizer
            "finance $$$ app ***",
        ]
        result = extract_keywords(texts, top_k=3)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(kw, list) for kw in result)
