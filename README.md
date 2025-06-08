
# Sentiment and Thematic Analysis Pipeline

## Overview

This project provides a comprehensive pipeline for sentiment and thematic analysis on textual review data. It includes data preprocessing, emoji removal, language translation, sentiment analysis using DistilBERT, keyword extraction, and theme clustering.

---

## 🛠️ Installation

Clone the repository and initialize the environment with all dependencies and models:

```bash
git clone https://github.com/your-org/your-project.git
cd your-project
make init
```

---

## ▶️ Usage

Run the full sentiment and thematic analysis pipeline on your data:

```bash
make run-sentiment-pipeline
```

This will:

- Load and preprocess data (including emoji removal and text normalization)
- Translate non-English text to English
- Perform sentiment analysis
- Extract keywords
- Assign themes based on keyword clustering
- Save results to `data/outputs/sentiment_theme_output.csv`

---

## 🕸️ Scraping (Optional)

If your workflow requires scraping review data:

```bash
make scrape
```

---

## 🧪 Testing & Formatting

Ensure code quality and correctness with:

```bash
make test
make format
```

- `make test` runs the test suite.
- `make format` auto-formats the code using Black and isort.

---

## 📁 Project Structure

- `data/`: Contains raw, processed, and output datasets.
- `data/text_cleaning.py`: Text preprocessing and emoji removal methods.
- `models/`: Sentiment analysis models.
- `features/`: Keyword extraction and theme clustering logic.
- `Makefile`: Automates common tasks (`init`, `test`, `format`, `scrape`, `run-sentiment-pipeline`).

---

## 🚀 Quick Start

1. Clone repo and initialize:

    ```bash
    git clone <repo-url>
    cd your-project
    make init
    ```

2. Run the pipeline:

    ```bash
    make run-sentiment-pipeline
    ```

3. Check results in:

    ```
    data/outputs/sentiment_theme_output.csv
    ```

---

## 📝 Notes

- The pipeline expects input CSV with a `review` column.
- Emoji removal is done in preprocessing to improve analysis quality.
- Non-English texts are translated automatically.
- Sentiment analysis uses DistilBERT with fallback for errors.
- Keyword extraction and theme assignment help uncover key topics.

---

## 🧑‍💻 Contact

For questions or contributions, please open an issue or reach out to the maintainers.

---
