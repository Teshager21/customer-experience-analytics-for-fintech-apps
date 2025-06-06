from transformers import pipeline

# Load model once
sentiment_pipeline = pipeline(
    "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
)


def analyze_sentiment(text):
    result = sentiment_pipeline(text[:512])[0]
    label = result["label"].lower()
    score = result["score"]
    return label, score
