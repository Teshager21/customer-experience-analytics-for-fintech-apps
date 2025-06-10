import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from pathlib import Path
from typing import Optional

# from datetime import datetime
import logging
from matplotlib.backends.backend_pdf import PdfPages
import textwrap

# from matplotlib.backends.backend_pdf import PdfPages

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class ReviewVisualizer:
    def __init__(
        self,
        summary_df: pd.DataFrame,
        full_df: pd.DataFrame,
        out_dir: str = "outputs/plots",
    ):
        """
        Initializes the visualizer.

        Args:
            summary_df (pd.DataFrame): Output of ReviewAnalyzer.generate_summary_df().
            full_df (pd.DataFrame): Full DataFrame with raw review data
            (including REVIEW_DATE).out_dir (str): Directory
            to save generated plots.
        """
        self.summary_df = summary_df
        self.full_df = full_df
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"Visualizer initialized with output path: {self.out_dir.resolve()}"
        )

    def plot_top_themes_bar(
        self, bank: str, sentiment: str = "positive", top_n: int = 5, save: bool = True
    ):
        """
        Plot bar chart of top themes for a specific bank and sentiment.

        Args:
            bank (str): Bank name.
            sentiment (str): Sentiment type ("positive"/"negative").
            top_n (int): Number of top themes to show.
            save (bool): If True, saves the figure.
        """
        subset = self.summary_df[
            (self.summary_df["bank_name"] == bank)
            & (self.summary_df["SENTIMENT_LABEL"] == sentiment)
        ].nlargest(top_n, "count")

        if subset.empty:
            logger.warning(f"No data for {bank} - {sentiment}")
            return

        plt.figure(figsize=(8, 4))
        sns.barplot(x="count", y="theme_list", data=subset, palette="viridis")
        plt.title(f"Top {sentiment.capitalize()} Themes for {bank}")
        plt.xlabel("Frequency")
        plt.ylabel("Theme")
        plt.tight_layout()

        if save:
            path = self.out_dir / f"{bank}_{sentiment}_bar.png"
            plt.savefig(path, dpi=300)
            logger.info(f"Saved bar chart: {path}")
        else:
            plt.show()

        plt.close()

    def plot_theme_wordcloud(
        self, bank: Optional[str] = None, sentiment: str = "positive", save: bool = True
    ):
        """
        Plot a word cloud of themes for a given sentiment (optionally by bank).

        Args:
            bank (str): Optional bank name to filter.
            sentiment (str): Sentiment type.
            save (bool): If True, saves the figure.
        """
        df = self.summary_df[self.summary_df["SENTIMENT_LABEL"] == sentiment]
        if bank:
            df = df[df["bank_name"] == bank]

        freq = df.groupby("theme_list")["count"].sum().to_dict()
        if not freq:
            logger.warning(
                f"No themes for {sentiment} sentiment in {bank or 'all banks'}"
            )
            return

        wc = WordCloud(width=800, height=400, background_color="white", colormap="Set2")
        wc.generate_from_frequencies(freq)

        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"{bank or 'All Banks'} - {sentiment.capitalize()} Theme Word Cloud")
        plt.tight_layout()

        if save:
            fname = f"{bank or 'all'}_{sentiment}_wordcloud.png".replace(" ", "_")
            path = self.out_dir / fname
            plt.savefig(path, dpi=300)
            logger.info(f"Saved word cloud: {path}")
        else:
            plt.show()

        plt.close()

    def plot_sentiment_trend(self, save: bool = True):
        """
        Plot sentiment trends over time (across all banks).

        Args:
            save (bool): If True, saves the figure.
        """
        df = self.full_df.copy()
        if "REVIEW_DATE" not in df.columns:
            logger.warning("REVIEW_DATE column missing. Skipping trend plot.")
            return

        df["REVIEW_DATE"] = pd.to_datetime(df["REVIEW_DATE"])
        trend_df = (
            df.groupby([pd.Grouper(key="REVIEW_DATE", freq="W"), "SENTIMENT_LABEL"])
            .size()
            .unstack()
            .fillna(0)
        )

        plt.figure(figsize=(10, 5))
        trend_df.plot(ax=plt.gca(), marker="o")
        plt.title("Sentiment Trend Over Time")
        plt.xlabel("Date")
        plt.ylabel("Number of Reviews")
        plt.tight_layout()

        if save:
            path = self.out_dir / "sentiment_trend.png"
            plt.savefig(path, dpi=300)
            logger.info(f"Saved sentiment trend: {path}")
        else:
            plt.show()

        plt.close()

    def generate_all_visuals_per_bank(self, top_n: int = 5):
        """
        Generate bar + word cloud plots for each bank and sentiment.
        """
        banks = self.summary_df["bank_name"].unique()
        sentiments = ["positive", "negative"]

        for bank in banks:
            for sentiment in sentiments:
                self.plot_top_themes_bar(bank, sentiment, top_n)
                self.plot_theme_wordcloud(bank, sentiment)

    def export_visuals_to_pdf(self, pdf_name: str = "Review_Report.pdf"):
        """
        Export all plots in the output folder into a single PDF report.

        Args:
            pdf_name (str): Filename of the output PDF.
        """
        images = sorted(self.out_dir.glob("*.png"))
        if not images:
            logger.warning("No plots found to include in the PDF report.")
            return

        pdf_path = self.out_dir / pdf_name
        with PdfPages(pdf_path) as pdf:
            for img_path in images:
                img = plt.imread(img_path)
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.imshow(img)
                ax.axis("off")
                pdf.savefig(fig)
                plt.close(fig)

        logger.info(f"Exported all visuals to PDF: {pdf_path}")

    def add_insights(self, insights: dict):
        """
        Store insights dict to include in the report.

        Expected format:
        {
            "drivers": { "BankName": ["fast navigation", ...], ... },
            "pain_points": { "BankName": ["crashes", ...], ... },
            "recommendations": ["add budgeting tool", ...],
        }
        """
        self.insights = insights

    def _plot_text_page(self, title: str, paragraphs: list):
        """
        Create a PDF page with formatted text.

        Args:
            title (str): Title of the page
            paragraphs (list of str): Paragraphs of text to render
        """
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")

        wrapped_text = []
        for para in paragraphs:
            wrapped = textwrap.fill(para, width=80)
            wrapped_text.append(wrapped)

        full_text = "\n\n".join(wrapped_text)

        ax.text(
            0.5,
            0.95,
            title,
            ha="center",
            va="top",
            fontsize=16,
            fontweight="bold",
            wrap=True,
        )
        ax.text(
            0.05,
            0.9,
            full_text,
            ha="left",
            va="top",
            fontsize=12,
            wrap=True,
            linespacing=1.5,
        )
        return fig

    def export_visuals_and_insights_to_pdf(
        self, pdf_name: str = "Review_Report_with_Insights.pdf"
    ):
        """
        Export all plots and insights to a combined PDF.
        Ensures insights are calculated and displayed clearly in PDF.

        Args:
            pdf_name (str): Output filename for the PDF.
        """
        pdf_path = self.out_dir / pdf_name
        images = sorted(self.out_dir.glob("*.png"))

        # Ensure insights are available
        if not hasattr(self, "insights") or not self.insights:
            logger.info("Generating insights before exporting.")
            if hasattr(self, "analyzer"):
                self.insights = self.analyzer.analyze_per_bank(
                    display=False, return_format="dict"
                )
            else:
                logger.warning("No analyzer or insights found.")
                self.insights = {}

        with PdfPages(pdf_path) as pdf:
            # Add insight summary per bank
            for bank, bank_insights in self.insights.items():
                drivers = bank_insights.get("top_drivers", {})
                pain_points = bank_insights.get("top_pain_points", {})

                paragraphs = []
                paragraphs.append(f"📌 Insights for {bank}")
                paragraphs.append("")
                paragraphs.append("✅ Top Drivers (Positive Themes):")
                for theme, count in drivers.items():
                    paragraphs.append(f"   - {theme} ({count})")

                paragraphs.append("")
                paragraphs.append("❌ Top Pain Points (Negative Themes):")
                for theme, count in pain_points.items():
                    paragraphs.append(f"   - {theme} ({count})")

                fig = self._plot_text_page(f"Insights: {bank}", paragraphs)
                pdf.savefig(fig)
                plt.close(fig)

            # Add recommendations if available
            if hasattr(self, "recommendations") and self.recommendations:
                rec_fig = self._plot_text_page(
                    "💡 Recommendations", [f"- {r}" for r in self.recommendations]
                )
                pdf.savefig(rec_fig)
                plt.close(rec_fig)

            # Add image pages
            for img_path in images:
                img = plt.imread(img_path)
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.imshow(img)
                ax.axis("off")
                pdf.savefig(fig)
                plt.close(fig)

        logger.info(f"Exported combined visuals and insights report: {pdf_path}")
