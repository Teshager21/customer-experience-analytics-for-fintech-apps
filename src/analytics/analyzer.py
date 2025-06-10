import pandas as pd
from typing import Dict, List, Union, Optional
from collections import defaultdict
import logging
from rich.table import Table
from rich.console import Console

console = Console()

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class ReviewAnalyzer:
    """
    A class for analyzing bank customer reviews to extract
    key drivers (positive themes) and pain points (negative themes).

    Attributes:
        df (pd.DataFrame): The input review data with required columns:
            ['bank_name', 'REVIEW_TEXT', 'RATING', 'SENTIMENT_LABEL', 'THEMES'].
    """

    def __init__(self, df: pd.DataFrame):
        if not all(
            col in df.columns
            for col in [
                "bank_name",
                "REVIEW_TEXT",
                "RATING",
                "SENTIMENT_LABEL",
                "THEMES",
            ]
        ):
            raise ValueError(
                "DataFrame must include ['bank_name', 'REVIEW_TEXT', "
                "'RATING', 'SENTIMENT_LABEL', 'THEMES'] columns."
            )

        self.df = df.copy()
        self.insights: Optional[Dict[str, Dict[str, Dict[str, int]]]] = None
        logger.info(f"Initializing analyzer with {len(self.df)} reviews.")
        self.df["theme_list"] = self.df["THEMES"].apply(self._parse_themes)

    def _parse_themes(self, theme_str: str) -> List[str]:
        """
        Splits comma-separated themes and returns them as a cleaned list.
        """
        if not isinstance(theme_str, str):
            return []
        return [t.strip().lower() for t in theme_str.split(",") if t.strip()]

    def analyze_per_bank(
        self,
        top_n: int = 3,
        display: bool = True,
        return_format: str = "dict",
    ) -> Union[Dict[str, Dict[str, Dict[str, int]]], pd.DataFrame]:
        """
        Analyze top positive and negative themes for each bank.

        Returns:
            Union[Dict[str, Dict[str, Dict[str, int]]], pd.DataFrame]: Insights.
        """
        insights: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(dict)

        try:
            if "theme_list" not in self.df.columns:
                self.df["theme_list"] = self.df["THEMES"].apply(
                    lambda x: [t.strip() for t in x.split(",")] if pd.notnull(x) else []
                )

            for bank in self.df["bank_name"].unique():
                bank_df = self.df[self.df["bank_name"] == bank]

                pos_themes = (
                    bank_df[bank_df["SENTIMENT_LABEL"] == "positive"]
                    .explode("theme_list")["theme_list"]
                    .value_counts()
                    .head(top_n)
                    .to_dict()
                )

                neg_themes = (
                    bank_df[bank_df["SENTIMENT_LABEL"] == "negative"]
                    .explode("theme_list")["theme_list"]
                    .value_counts()
                    .head(top_n)
                    .to_dict()
                )

                insights[bank] = {
                    "top_drivers": pos_themes,
                    "top_pain_points": neg_themes,
                }

            logger.info(f"Generated insights for {len(insights)} banks.")

            if display:
                for bank, data in insights.items():
                    table = Table(title=f"✨ Insights for {bank}", show_lines=True)
                    table.add_column("Top Drivers", justify="center", style="green")
                    table.add_column("Count", justify="right", style="green")
                    table.add_column("Top Pain Points", justify="center", style="red")
                    table.add_column("Count", justify="right", style="red")

                    max_len = max(
                        len(data["top_drivers"]), len(data["top_pain_points"])
                    )
                    drivers = list(data["top_drivers"].items())
                    pain_points = list(data["top_pain_points"].items())

                    for i in range(max_len):
                        d_theme, d_count = drivers[i] if i < len(drivers) else ("", "")
                        p_theme, p_count = (
                            pain_points[i] if i < len(pain_points) else ("", "")
                        )
                        table.add_row(d_theme, str(d_count), p_theme, str(p_count))

                    console.print(table)

            self.insights = dict(insights)

            if return_format == "dataframe":
                records = []
                for bank, data in insights.items():
                    for theme, count in data["top_drivers"].items():
                        records.append((bank, "positive", theme, count))
                    for theme, count in data["top_pain_points"].items():
                        records.append((bank, "negative", theme, count))
                return pd.DataFrame(
                    records, columns=["bank", "sentiment", "theme", "count"]
                )

            return dict(insights)

        except Exception as e:
            logger.error("Error during per-bank analysis.", exc_info=True)
            raise RuntimeError("Bank analysis failed.") from e

    def generate_summary_df(self) -> pd.DataFrame:
        """
        Generate a summary DataFrame of theme counts grouped by bank and sentiment.
        """
        try:
            exploded = self.df.explode("theme_list")
            summary = (
                exploded.groupby(["bank_name", "SENTIMENT_LABEL", "theme_list"])
                .size()
                .reset_index(name="count")
                .sort_values(
                    ["bank_name", "SENTIMENT_LABEL", "count"],
                    ascending=[True, True, False],
                )
            )
            logger.info(f"Generated summary DataFrame with {len(summary)} rows.")
            return summary
        except Exception as e:
            logger.error("Failed to generate theme summary DataFrame.", exc_info=True)
            raise RuntimeError("Summary DataFrame generation failed.") from e
