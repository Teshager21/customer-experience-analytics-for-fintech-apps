## ERD of Our Database
```mermaid
erDiagram
    BANKS {
        NUMBER id PK "Primary key"
        VARCHAR name "Unique"
        TIMESTAMP created_at
    }
    REVIEWS {
        NUMBER id PK
        NUMBER bank_id FK
        CLOB review_text
        NUMBER rating
        DATE review_date
        VARCHAR source
        CLOB cleaned_text
        VARCHAR sentiment_label
        FLOAT sentiment_score
        CLOB keywords
        CLOB themes
        TIMESTAMP created_at
    }
    BANKS ||--o{ REVIEWS : contains
