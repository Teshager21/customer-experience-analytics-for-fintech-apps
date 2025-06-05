import numpy as np
import pandas as pd
import pytest

from data.data_quality_utils import (
    DataQualityUtils,
)  # Adjust import to your actual module


@pytest.fixture
def sample_df():
    data = {
        "Name": ["Alice", "Bob", "Charlie", "Alice", "Alice"],
        "Age": [25, 30, np.nan, 25, 25],
        "Join Date": ["2021-01-01", "2021-02-15", "not_a_date", None, "2021-01-01"],
        "Unnamed:_0": [1, 2, 3, 4, 1],
        "Text": ["Hello 😀", "Bonjour", "Hola 😜", None, "Hello 😀"],
        "EmptyCol": [None, None, None, None, None],
        "Duplicates": ["dup", "dup", "unique", "dup", "dup"],
        "LangText": [
            "This is English",
            "Ceci est français",
            "Este es español",
            "English too",
            "This is English",
        ],
    }
    df = pd.DataFrame(data)
    return df


def test_init_with_invalid_type():
    with pytest.raises(TypeError):
        DataQualityUtils("not a dataframe")


def test_clean_column_names(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    assert all(col.islower() for col in dqu.df.columns)
    assert all(" " not in col for col in dqu.df.columns)


def test_drop_redundant_columns(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    df_cleaned = dqu.drop_redundant_columns()
    assert "unnamed:_0" not in df_cleaned.columns


def test_clean_dataframe(sample_df):
    dqu = DataQualityUtils(sample_df)
    df_cleaned = dqu.clean_dataframe()
    assert "unnamed:_0" not in df_cleaned.columns
    assert all(col.islower() for col in df_cleaned.columns)


def test_columns_with_significant_missing_values(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_dataframe()
    result = dqu.columns_with_significant_missing_values(threshold=10)
    assert "age" in result.index


def test_check_duplicates(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    count = dqu.check_duplicates()
    assert count == 1


def test_find_invalid_values(sample_df):
    df = sample_df.copy()
    df.loc[0, "Text"] = "NA"
    dqu = DataQualityUtils(df)
    dqu.clean_column_names()
    invalids = dqu.find_invalid_values()
    assert "text" in invalids
    assert invalids["text"]["count"] >= 1


def test_summary(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    summary = dqu.summary()
    assert "#missing_values" in summary.columns
    assert "age" in summary.index


def test_convert_columns_to_datetime(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    df = dqu.convert_columns_to_datetime(columns=["join_date"])
    assert pd.api.types.is_datetime64_any_dtype(df["join_date"])


def test_drop_empty_columns(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    df = dqu.drop_empty_columns()
    assert "emptycol" not in df.columns


def test_drop_columns(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    df = dqu.drop_columns(["age", "non_existent_col"])
    assert "age" not in df.columns


def test_rename_columns(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    df = dqu.rename_columns({"age": "years_old", "non_existent": "foo"})
    assert "years_old" in df.columns
    assert "age" not in df.columns


def test_rename_and_prioritize_columns(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    df = dqu.rename_and_prioritize_columns({"age": "years_old", "name": "full_name"})
    cols = list(df.columns)
    assert cols[0] == "years_old"
    assert cols[1] == "full_name"


def test_display_duplicates(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    duplicates = dqu.display_duplicates()
    assert not duplicates.empty


def test_drop_duplicates(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    before = len(dqu.df)
    dqu.drop_duplicates()
    after = len(dqu.df)
    assert after < before


def test_drop_rows_with_missing_in_columns(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    before = len(dqu.df)
    dqu.drop_rows_with_missing_in_columns(["age"])
    after = len(dqu.df)
    assert after < before


def test_filter_english_text(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    df_filtered = dqu.filter_english_text("langtext")
    # All entries in 'langtext' should be strings after filtering
    assert all(isinstance(x, str) for x in df_filtered["langtext"])


def test_replace_emojis_with_text(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()
    df = dqu.replace_emojis_with_text("text")
    replaced = df["text"].iloc[0]
    # Emoji should be replaced with words, no emojis remaining
    assert "😀" not in replaced
    assert "happy" in replaced


@pytest.mark.asyncio
async def test_translate_to_english():
    from data.data_quality_utils import DataQualityUtils

    df = pd.DataFrame({"text": ["Bonjour", "Hello", "Hola"]})
    dqu = DataQualityUtils(df)
    dqu.clean_column_names()

    # Directly test the async method with known text
    translated_1 = await dqu.translate_to_english("Bonjour")
    translated_2 = await dqu.translate_to_english("Hello")
    translated_3 = await dqu.translate_to_english("Hola")

    assert isinstance(translated_1, str)
    assert isinstance(translated_2, str)
    assert isinstance(translated_3, str)
    # "Hello" should remain "Hello"
    assert translated_2 == "Hello"


@pytest.mark.asyncio
async def test_translate_non_english_text(sample_df):
    dqu = DataQualityUtils(sample_df)
    dqu.clean_column_names()

    # For this test, patch the translate_to_english to simulate translation
    async def fake_translate(text):
        return "translated" if text != "Hello" else text

    dqu.translate_to_english = fake_translate  # monkeypatch

    df = await dqu.translate_non_english_text("text")
    assert isinstance(df, pd.DataFrame)
    # The translated column should exist
    assert "text" in df.columns


if __name__ == "__main__":
    pytest.main()
