# src/features/sentiment_analysis.py

from transformers import pipeline
from typing import Tuple, Union
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load model once at module level for performance
try:
    sentiment_pipeline = pipeline(
        "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    logger.info("Sentiment pipeline loaded successfully.")
except Exception as e:
    logger.error("Failed to load sentiment pipeline: %s", str(e))
    sentiment_pipeline = None


def analyze_sentiment(text: str) -> Tuple[str, float]:
    """
    Analyze sentiment of the input text using a pre-trained BERT model.

    Args:
        text (str): Input text string.

    Returns:
        Tuple[str, float]: Sentiment label ("positive" or "negative")
        and confidence score.

    Raises:
        ValueError: If text is invalid or pipeline is not loaded.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")

    if sentiment_pipeline is None:
        raise RuntimeError("Sentiment analysis model not loaded properly.")

    truncated_text = text[:512]  # BERT models have a 512 token limit
    result = sentiment_pipeline(truncated_text)[0]
    label = result["label"].lower()
    score = result["score"]

    logger.debug(f"Sentiment analysis result: {label} ({score:.2f})")
    return label, score


def safe_analyze_sentiment(text: Union[str, None]) -> Tuple[str, float]:
    """
    Safe wrapper around analyze_sentiment.
    Returns default sentiment if input is invalid.

    Args:
        text (str or None): Input text.

    Returns:
        Tuple[str, float]: Sentiment result or neutral fallback.
    """
    try:
        if text is None or not isinstance(text, str) or not text.strip():
            raise ValueError("Empty or invalid text.")

        return analyze_sentiment(text)
    except Exception as e:
        logger.warning(
            f"Skipping invalid input during sentiment analysis: {text!r} ({e})"
        )
        return "neutral", 0.0
