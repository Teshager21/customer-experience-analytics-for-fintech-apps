# tests/features/test_sentiment_analysis.py

import pytest
from models.sentiment_model import analyze_sentiment


class TestAnalyzeSentiment:

    def test_positive_sentiment(self):
        label, score = analyze_sentiment("I love using this fintech app. It's amazing!")
        assert label in ["positive", "negative"]
        assert 0.0 <= score <= 1.0
        assert label == "positive"

    def test_negative_sentiment(self):
        label, score = analyze_sentiment("The app keeps crashing. It's so frustrating!")
        assert label == "negative"

    def test_mixed_sentiment(self):
        label, score = analyze_sentiment(
            "I like the design but the service is terrible."
        )
        assert label in [
            "positive",
            "negative",
        ]  # Simplified BERT model doesn't support "neutral"

    def test_empty_input(self):
        with pytest.raises(ValueError):
            analyze_sentiment("")

    def test_non_string_input(self):
        with pytest.raises(ValueError):
            analyze_sentiment(12345)

    def test_truncates_long_input(self):
        long_text = "great " * 600  # 600 words should trigger truncation
        label, score = analyze_sentiment(long_text)
        assert label in ["positive", "negative"]
        assert isinstance(score, float)
