# 📄 Project Architecture: Customer Experience Analytics for Fintech Apps

## 🎯 Objective
Scrape, analyze, and visualize customer reviews from the Google Play Store for three Ethiopian bank apps (CBE, BOA, Dashen) to derive insights into customer satisfaction, feature requests, and pain points.

---

## 🧱 Architecture Overview

```
                    ┌────────────────────┐
                    │  Google Play Store │
                    └─────────┬──────────┘
                              │ (Scraper)
                              ▼
                  ┌─────────────────────────┐
                  │ Raw Reviews Collection  │
                  │  (data/raw/*.json/csv)  │
                  └─────────┬───────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ Preprocessing & Cleaning              │
        │ - Remove duplicates, normalize dates  │
        │ - Handle missing values               │
        │ Output: data/processed/cleaned_reviews.csv │
        └────────────────┬──────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────────┐
    │ Sentiment & Thematic Analysis                  │
    │ - VADER or DistilBERT                         │
    │ - TF-IDF, spaCy, or topic modeling            │
    │ Output: sentiment_scores.csv, themes.csv      │
    └────────────────┬──────────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────────────┐
        │ Oracle/Postgres Database Storage         │
        │ - Create schema                          │
        │ - Insert cleaned reviews and analysis    │
        └────────────────┬─────────────────────────┘
                         │
                         ▼
             ┌───────────────────────────────┐
             │ Visualizations & Reporting    │
             │ - Bar charts, Word clouds     │
             │ - Summary statistics          │
             │ Output: figures/, reports/    │
             └──────────────┬────────────────┘
                            ▼
              ┌──────────────────────────────┐
              │ Business Insights            │
              │ - Drivers & Pain Points      │
              │ - Recommendations            │
              └──────────────────────────────┘
```

---

## 🧾 Module Responsibilities

| Module               | Responsibility                                                  |
|----------------------|------------------------------------------------------------------|
| `src/data/`          | Scraping and initial preprocessing of reviews.                  |
| `src/features/`      | Sentiment scoring, keyword extraction, topic modeling.          |
| `src/models/`        | (Optional) Modeling or clustering logic.                        |
| `src/visualization/` | Plots and graphical summaries.                                  |
| `src/utils/`         | Shared helper functions (e.g., for date parsing, I/O).          |
| `tests/`             | Unit and integration tests for major components.                |
| `config/`            | Environment-specific configurations for reproducibility.        |
| `Dockerfile`         | Containerized build and deployment.                             |
| `Makefile`           | Task runner to streamline common commands.                      |

---

## 📦 Data Flow

```
google-play-scraper → raw/ → cleaned → processed/ → sentiment & themes → visualizations + DB → report.md/pdf
```

---

## ✅ Extensibility Suggestions

- Integrate Streamlit or Dash for interactive insights.
- Add Kafka or Airflow for real-time or scheduled pipelines.
- Enhance database layer with REST API to serve filtered queries.
