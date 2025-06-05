import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud


class ReviewVisualizer:
    """
    An object-oriented utility to analyze and visualize user reviews with ratings,
    thumbs up, review text, and timestamps.

    Attributes:
        df (pd.DataFrame): Input DataFrame with user reviews.
        output_dir (str): Directory to save generated plots.
    """

    def __init__(self, df: pd.DataFrame, output_dir: str = "plots"):
        """
        Initializes the ReviewVisualizer class.

        Args:
            df (pd.DataFrame): Input DataFrame with columns:
            ['userName', 'review', 'rating', 'thumbsUpCount', 'date', 'bank']
            output_dir (str): Folder to store the generated plots.
        """
        self.df = df.copy()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self._validate_and_prepare()

    def _validate_and_prepare(self):
        """
        Validates the required columns and converts date column to datetime.
        """
        required_cols = {
            "userName",
            "review",
            "rating",
            "thumbsUpCount",
            "date",
            "bank",
        }
        if not required_cols.issubset(set(self.df.columns)):
            missing = required_cols - set(self.df.columns)
            raise ValueError(f"Missing columns in data: {missing}")

        try:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
            self.df.dropna(subset=["date", "review"], inplace=True)
        except Exception as e:
            raise RuntimeError("Failed to convert 'date' column to datetime.") from e

    def plot_rating_distribution(self):
        """Plots and saves a bar chart of rating frequencies."""
        try:
            sns.countplot(data=self.df, x="rating", palette="viridis")
            plt.title("Rating Distribution")
            plt.xlabel("Rating")
            plt.ylabel("Count")
            self._save_plot("rating_distribution.png")
        except Exception as e:
            print(f"[ERROR] Could not generate rating distribution: {e}")

    def plot_average_rating_over_time(self):
        """Plots and saves a time series of average rating per day."""
        try:
            avg_rating = self.df.set_index("date").resample("D")["rating"].mean()
            avg_rating.plot(marker="o")
            plt.title("Average Rating Over Time")
            plt.ylabel("Rating")
            plt.xlabel("Date")
            plt.grid(True)
            self._save_plot("average_rating_over_time.png")
        except Exception as e:
            print(f"[ERROR] Could not generate average rating plot: {e}")

    def plot_thumbs_up_vs_rating(self):
        """Plots and saves a boxplot of thumbs up count by rating."""
        try:
            sns.boxplot(x="rating", y="thumbsUpCount", data=self.df, palette="coolwarm")
            plt.title("Thumbs Up Count by Rating")
            self._save_plot("thumbs_up_vs_rating.png")
        except Exception as e:
            print(f"[ERROR] Could not generate thumbs up boxplot: {e}")

    def plot_wordcloud(self):
        """Generates and saves a word cloud from the review text."""
        try:
            text = " ".join(self.df["review"].astype(str))
            wordcloud = WordCloud(
                width=1000, height=500, background_color="white"
            ).generate(text)
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.title("Word Cloud of Reviews")
            self._save_plot("wordcloud_reviews.png")
        except Exception as e:
            print(f"[ERROR] Could not generate word cloud: {e}")

    def plot_sentiment_vs_rating(self):
        """Computes sentiment score using VADER and plots it against rating."""
        try:
            analyzer = SentimentIntensityAnalyzer()
            self.df["sentiment"] = self.df["review"].apply(
                lambda x: analyzer.polarity_scores(str(x))["compound"]
            )
            sns.boxplot(x="rating", y="sentiment", data=self.df, palette="magma")
            plt.title("Sentiment Score by Rating")
            self._save_plot("sentiment_vs_rating.png")
        except Exception as e:
            print(f"[ERROR] Could not generate sentiment vs rating plot: {e}")

    def _save_plot(self, filename: str):
        """
        Saves and displays the current matplotlib plot.

        Args:
            filename (str): Name of the file to save the plot as.
        """
        try:
            plt.tight_layout()
            full_path = os.path.join(self.output_dir, filename)
            plt.savefig(full_path)
            print(f"[INFO] Saved plot: {full_path}")
            plt.show()  # Display plot after saving
            plt.close()
        except Exception as e:
            print(f"[ERROR] Failed to save or show plot '{filename}': {e}")
