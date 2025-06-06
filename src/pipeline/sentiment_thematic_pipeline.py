import pandas as pd
from pathlib import Path

from data.text_cleaning import preprocess_reviews
from models.sentiment_model import analyze_sentiment
from features.keyword_extraction import extract_keywords
from features.theme_clustering import assign_themes


def run_pipeline(input_csv: str, output_csv: str):
    """Orchestrates the sentiment and thematic analysis pipeline."""

    print("📥 Loading data...")
    df = pd.read_csv(input_csv)
    df.rename(columns={"review": "review_text"}, inplace=True)

    print("🧹 Preprocessing review text...")
    df["cleaned_text"] = df["review_text"].apply(preprocess_reviews)

    print("🧠 Performing sentiment analysis with DistilBERT...")
    sentiment_results = df["cleaned_text"].apply(analyze_sentiment)
    df[["sentiment_label", "sentiment_score"]] = pd.DataFrame(
        sentiment_results.tolist(), index=df.index
    )

    print("🔍 Extracting keywords...")
    df["keywords"] = extract_keywords(df["cleaned_text"].tolist(), top_k=5)

    print("🧩 Assigning themes based on keyword clustering...")
    df["themes"] = df["keywords"].apply(assign_themes)

    print("💾 Saving results...")
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    print(f"✅ Pipeline completed. Results saved to {output_csv}")


if __name__ == "__main__":
    run_pipeline(
        "data/processed/cleaned_reviews.csv", "data/outputs/sentiment_theme_output.csv"
    )
