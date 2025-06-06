import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SentimentThemeVisualizer:
    """
    A class for generating sentiment and thematic analysis visualizations.

    Attributes:
        df (pd.DataFrame): The dataset with processed reviews.
    """

    def __init__(self, filepath: str):
        """
        Initializes the visualizer with the dataset.

        Args:
            filepath (str): Path to the CSV file.
        """
        try:
            self.df = pd.read_csv(filepath)
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
            self.df["themes"] = self.df["themes"].apply(eval)
            self.df["keywords"] = self.df["keywords"].apply(eval)
            logging.info("Data loaded successfully from %s", filepath)
        except Exception as e:
            logging.error("Failed to load or parse data: %s", e)
            raise

    def plot_sentiment_distribution(self):
        """Plot the overall sentiment distribution."""
        try:
            sns.countplot(data=self.df, x="sentiment_label", palette="coolwarm")
            plt.title("Sentiment Distribution")
            plt.xlabel("Sentiment")
            plt.ylabel("Count")
            plt.show()
        except Exception as e:
            logging.error("Error plotting sentiment distribution: %s", e)

    def plot_sentiment_by_bank(self):
        """Plot sentiment distribution by bank."""
        try:
            sns.countplot(
                data=self.df, x="bank", hue="sentiment_label", palette="coolwarm"
            )
            plt.title("Sentiment per Bank")
            plt.xlabel("Bank")
            plt.ylabel("Count")
            plt.legend(title="Sentiment")
            plt.show()
        except Exception as e:
            logging.error("Error plotting sentiment by bank: %s", e)

    def plot_theme_distribution(self):
        """Plot overall distribution of themes."""
        try:
            theme_exploded = self.df.explode("themes")
            sns.countplot(
                data=theme_exploded,
                y="themes",
                order=theme_exploded["themes"].value_counts().index,
            )
            plt.title("Theme Distribution")
            plt.xlabel("Count")
            plt.ylabel("Theme")
            plt.show()
        except Exception as e:
            logging.error("Error plotting theme distribution: %s", e)

    def plot_theme_by_bank(self):
        """Plot theme distribution per bank."""
        try:
            theme_exploded = self.df.explode("themes")
            sns.countplot(data=theme_exploded, x="bank", hue="themes")
            plt.title("Themes by Bank")
            plt.xlabel("Bank")
            plt.ylabel("Count")
            plt.legend(title="Themes", bbox_to_anchor=(1.05, 1), loc="upper left")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            logging.error("Error plotting themes by bank: %s", e)

    def plot_sentiment_over_time(self):
        """Plot sentiment trends over time."""
        try:
            sentiment_over_time = (
                self.df.groupby(["date", "sentiment_label"])
                .size()
                .unstack(fill_value=0)
            )
            sentiment_over_time.plot(marker="o")
            plt.title("Sentiment Trend Over Time")
            plt.xlabel("Date")
            plt.ylabel("Number of Reviews")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            logging.error("Error plotting sentiment over time: %s", e)

    def generate_wordcloud(self, sentiment: Optional[str] = "positive"):
        """
        Generate and display a word cloud for the given sentiment.

        Args:
            sentiment (str, optional): Sentiment to filter by. Defaults to "positive".
        """
        try:
            keywords = (
                self.df[self.df["sentiment_label"] == sentiment]["keywords"]
                .explode()
                .dropna()
                .tolist()
            )
            text = " ".join(keywords)
            if not text:
                logging.warning("No keywords found for sentiment: %s", sentiment)
                return
            wordcloud = WordCloud(
                width=800, height=400, background_color="white"
            ).generate(text)
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.title(
                f"Top Keywords in {(sentiment or 'Unknown').capitalize()} Reviews"
            )
            plt.show()
        except Exception as e:
            logging.error(
                "Error generating wordcloud for sentiment '%s': %s", sentiment, e
            )
