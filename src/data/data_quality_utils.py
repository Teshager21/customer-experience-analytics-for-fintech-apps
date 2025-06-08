import asyncio
import re
from typing import Any, Dict, Optional

import emoji
import nest_asyncio
import pandas as pd
from googletrans import Translator
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from utils.emoji_map import DEFAULT_EMOJI_MAP


nest_asyncio.apply()


class DataQualityUtils:
    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        self.df = df.copy()
        self.translator = Translator()

    def clean_column_names(self):
        """
        Standardize column names: lowercase, strip spaces,
        and replace spaces with underscores.
        """
        self.df.columns = (
            self.df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)
        )
        return self.df

    def drop_redundant_columns(self):
        """
        Drops commonly redundant columns like 'unnamed: 0' or exact duplicates.
        """
        if "unnamed:_0" in self.df.columns:
            self.df = self.df.drop(columns=["unnamed:_0"])
        self.df = self.df.loc[:, ~self.df.columns.duplicated()]
        return self.df

    def clean_dataframe(self):
        """
        Run all preprocessing steps on the internal DataFrame.
        """
        self.clean_column_names()
        self.drop_redundant_columns()
        return self.df

    def columns_with_significant_missing_values(
        self, threshold: float = 5.0
    ) -> pd.DataFrame:
        missing_counts = self.df.isna().sum()
        missing_percent = (missing_counts / len(self.df)) * 100
        significant = missing_percent[missing_percent > threshold]
        return pd.DataFrame(
            {
                "#missing_values": missing_counts[significant.index],
                "percentage": significant.apply(lambda x: f"{x:.2f}%"),
            }
        ).sort_values(by="#missing_values", ascending=False)

    def check_duplicates(self):
        """
        Return the number of duplicate rows in the DataFrame.
        """
        return self.df.duplicated().sum()

    def find_invalid_values(self, additional_invalids=None) -> dict:
        """
        Identifies and summarizes invalid values in object columns.
        """
        if additional_invalids is None:
            additional_invalids = ["NA", "null", "NULL", "-", "N/A"]

        invalid_summary = {}
        for col in self.df.select_dtypes(include="object").columns:
            mask = self.df[col].astype(str).str.strip().isin(["", *additional_invalids])
            count = mask.sum()
            if count > 0:
                invalid_summary[col] = {
                    "count": count,
                    "examples": self.df.loc[mask, col].head(5),
                }
        return invalid_summary

    def summary(self) -> pd.DataFrame:
        """
        Provide a concise summary of missing data in the entire DataFrame.
        """
        missing_counts = self.df.isna().sum()
        missing_percent = (missing_counts / len(self.df)) * 100
        return pd.DataFrame(
            {
                "#missing_values": missing_counts,
                "percentage": missing_percent.map(lambda x: f"{x:.2f}%"),
            }
        ).sort_values(by="#missing_values", ascending=False)

    def count_duplicates(self) -> int:
        """
        Returns the number of duplicate rows in the DataFrame.
        """
        return self.df.duplicated().sum()

    def convert_columns_to_datetime(
        self, columns: Optional[list[str]] = None, errors: str = "coerce"
    ) -> pd.DataFrame:
        if columns is None:
            columns = [
                col
                for col in self.df.columns
                if "date" in col.lower() or "time" in col.lower()
            ]

        for col in columns:
            if col in self.df.columns:
                original_non_null = self.df[col].notna().sum()

                # Ensure strings and strip whitespaces
                self.df[col] = self.df[col].astype(str).str.strip()

                # Replace known bad values
                self.df[col] = self.df[col].replace(
                    ["", "nan", "null", "None", "NaT", "N/A"], pd.NA
                )

                # Convert datetime (handles timezone-aware strings too)
                self.df[col] = pd.to_datetime(self.df[col], errors=errors, utc=True)

                converted = self.df[col].notna().sum()
                print(
                    f"[{col}] Converted: {converted}/{original_non_null} "
                    f"({original_non_null - converted} became NaT)"
                )
            else:
                print(f"Warning: Column '{col}' not found.")
        return self.df

    def drop_empty_columns(self) -> pd.DataFrame:
        """
        Drops columns that are completely empty (i.e., all values are NaN).
        Returns the updated DataFrame and prints a summary of removed columns.
        """
        empty_cols = self.df.columns[self.df.isna().all()].tolist()
        if empty_cols:
            print(f"[INFO] Dropping {len(empty_cols)} empty column(s): {empty_cols}")
            self.df.drop(columns=empty_cols, inplace=True)
        else:
            print("[INFO] No completely empty columns found.")
        return self.df

    def drop_columns(self, columns: list[str]) -> pd.DataFrame:
        """
        Drops the specified column(s) from the DataFrame if they exist.

        Args:
            columns (list[str]): A list of column names to drop.

        Returns:
            pd.DataFrame: The updated DataFrame.
        """
        missing_cols = [col for col in columns if col not in self.df.columns]
        existing_cols = [col for col in columns if col in self.df.columns]

        if existing_cols:
            self.df.drop(columns=existing_cols, inplace=True)
            print(f"[INFO] Dropped columns: {existing_cols}")

        if missing_cols:
            print(
                f"[WARNING] These columns were not found and could not be dropped: "
                f"{missing_cols}"
            )

        return self.df

    def rename_columns(self, rename_map: dict[str, str]) -> pd.DataFrame:
        """
        Renames columns in the DataFrame based on a provided dictionary.

        Args:
            rename_map (dict): A dictionary where keys are current column names
                            and values are the new column names.

        Returns:
            pd.DataFrame: The updated DataFrame with renamed columns.
        """
        missing_cols = [col for col in rename_map if col not in self.df.columns]
        if missing_cols:
            print(
                f"[WARNING] These columns were not found and cannot be "
                f"renamed: {missing_cols}"
            )

        rename_applied = {k: v for k, v in rename_map.items() if k in self.df.columns}
        self.df.rename(columns=rename_applied, inplace=True)

        print(f"[INFO] Renamed columns: {rename_applied}")
        return self.df

    def rename_and_prioritize_columns(self, rename_map: dict[str, str]) -> pd.DataFrame:
        """
        Renames columns based on rename_map and ensures the renamed columns
        appear first in the given order.
        Remaining columns retain their original order.

        Args:
            rename_map (dict): Keys are original column names,
            values are desired new names.

        Returns:
            pd.DataFrame: DataFrame with renamed and reordered columns.
        """
        # Validate and rename only existing columns
        valid_renames = {k: v for k, v in rename_map.items() if k in self.df.columns}
        missing = [k for k in rename_map if k not in self.df.columns]

        if missing:
            print(f"[WARNING] These columns were not found and skipped: {missing}")
        if valid_renames:
            self.df.rename(columns=valid_renames, inplace=True)
            print(f"[INFO] Renamed columns: {valid_renames}")

        # Get the renamed column names in the same order as in the original rename_map
        renamed_columns_order = [
            valid_renames[k] for k in rename_map if k in valid_renames
        ]

        # Reorder: renamed columns first, rest in original
        # order (excluding renamed ones)
        rest = [col for col in self.df.columns if col not in renamed_columns_order]
        self.df = self.df[renamed_columns_order + rest]

        return self.df

    def display_duplicates(self, keep: str = "first") -> pd.DataFrame:
        """
        Returns all duplicated rows in the DataFrame.

        Args:
            keep (str): Determines which duplicates to mark as True.
                        Options: 'first', 'last', False.
                        Default is 'first'.

        Returns:
            pd.DataFrame: DataFrame of duplicated rows.
        """
        duplicates = self.df[self.df.duplicated(keep=keep)]
        print(f"[INFO] Found {len(duplicates)} duplicated row(s).")
        return duplicates

    def drop_duplicates(
        self, keep: str = "first", inplace: bool = True
    ) -> pd.DataFrame:
        """
        Drops duplicated rows from the DataFrame.

        Args:
            keep (str): Determines which duplicates to keep.
                        Options: 'first', 'last', False.
                        Default is 'first'.
            inplace (bool): Whether to drop duplicates in place. If False,
                            returns a new DataFrame without modifying internal state.

        Returns:
            pd.DataFrame: Updated DataFrame with duplicates removed.
        """
        before = len(self.df)
        if inplace:
            self.df.drop_duplicates(keep=keep, inplace=True)
            after = len(self.df)
            print(f"[INFO] Dropped {before - after} duplicate row(s).")
            return self.df
        else:
            df_cleaned = self.df.drop_duplicates(keep=keep)
            print(
                f"[INFO] Dropped {before - len(df_cleaned)} "
                f"duplicate row(s) (non-inplace)."
            )
            return df_cleaned

    def drop_rows_with_missing_in_columns(self, columns: list[str]) -> pd.DataFrame:
        """
        Drops rows from the DataFrame where any value is missing (NaN)
        in the specified columns.

        Args:
            columns (list[str]): List of column names to check for missing values.

        Returns:
            pd.DataFrame: The updated DataFrame with specified rows dropped.
        """
        if not columns:
            print("[WARNING] No columns provided. No rows dropped.")
            return self.df

        missing_cols = [col for col in columns if col not in self.df.columns]
        if missing_cols:
            print(
                f"[WARNING] The following columns were not found "
                f"and ignored: {missing_cols}"
            )
            columns = [col for col in columns if col in self.df.columns]

        if not columns:
            print("[ERROR] None of the provided columns are valid. Aborting operation.")
            return self.df

        before_count = len(self.df)
        self.df.dropna(subset=columns, inplace=True)
        after_count = len(self.df)
        dropped = before_count - after_count
        print(
            f"[INFO] Dropped {dropped} row(s) with missing values in columns: {columns}"
        )
        return self.df

    def filter_english_text(self, text_column: str) -> pd.DataFrame:
        """
        Filters the DataFrame to keep only rows where the text in
        `text_column` is detected as English.

        Args:
            text_column (str): Name of the column containing text to detect language.

        Returns:
            pd.DataFrame: Filtered DataFrame with only English text rows.
        """
        if text_column not in self.df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame.")

        def is_english(text):
            try:
                return detect(text) == "en"
            except LangDetectException:
                return False

        mask = self.df[text_column].astype(str).apply(is_english)
        filtered_df = self.df.loc[mask].copy()
        dropped_count = len(self.df) - len(filtered_df)
        print(
            f"[INFO] Dropped {dropped_count} non-English rows "
            f"from '{text_column}' column."
        )
        self.df = filtered_df
        return self.df

    def replace_emojis_with_text(
        self, text_column: str, emoji_map: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Replaces emojis in the specified text column with
        sentiment-rich text equivalents.

        Args:
            text_column (str): Name of the column containing text with emojis.
            emoji_map (dict, optional): Mapping of emojis to replacement words.
                                        Defaults to common sentiment emojis.

        Returns:
            pd.DataFrame: DataFrame with emojis replaced in the specified column.
        """
        if text_column not in self.df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame.")

        if emoji_map is None:
            emoji_map = DEFAULT_EMOJI_MAP

        emoji_map_safe: Dict[str, str] = emoji_map  # Ensures mypy compliance

        def replace_emojis(text: Any) -> Any:
            if not isinstance(text, str):
                return text
            for emj, repl in emoji_map_safe.items():
                text = text.replace(emj, repl)
            text = emoji.replace_emoji(text, replace="")
            text = re.sub(r"\s+", " ", text).strip()
            return text

        self.df[text_column] = self.df[text_column].apply(replace_emojis)
        print(
            f"[INFO] Replaced emojis with text equivalents in '{text_column}' column."
        )
        return self.df

    async def translate_to_english(self, text):
        try:
            lang = detect(text)
        except LangDetectException:
            return text

        if lang != "en":
            try:
                translated = await self.translator.translate(text, src=lang, dest="en")
                return translated.text
            except Exception as e:
                print(f"[WARN] Translation failed: {e}")
                return text
        else:
            return text

    async def translate_non_english_text(self, text_column):
        if text_column not in self.df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame.")

        # Apply async function row-wise (needs some trick)
        import nest_asyncio

        nest_asyncio.apply()

        async def apply_async():
            return await asyncio.gather(
                *[self.translate_to_english(str(t)) for t in self.df[text_column]]
            )

        translations = asyncio.run(apply_async())
        self.df[text_column] = translations
        return self.df
