-- Table for Banks (lookup)
CREATE TABLE Banks (
    id            NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name          VARCHAR2(255) UNIQUE NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main Reviews table
CREATE TABLE Reviews (
    id                 NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bank_id            NUMBER NOT NULL,
    review_text        CLOB NOT NULL,
    rating             NUMBER(2,1),
    review_date        DATE,
    source             VARCHAR2(100),
    cleaned_text       CLOB,
    sentiment_label    VARCHAR2(20),
    sentiment_score    FLOAT,
    keywords           CLOB,       -- Store list as JSON-like string
    themes             CLOB,       -- Same for themes
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_bank
        FOREIGN KEY (bank_id)
        REFERENCES Banks(id)
        ON DELETE CASCADE
);
