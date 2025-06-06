from sklearn.feature_extraction.text import TfidfVectorizer


def extract_keywords(texts, top_k=5):
    # Clean out empty or meaningless documents
    cleaned_texts = [text for text in texts if isinstance(text, str) and text.strip()]

    if not cleaned_texts:
        return [[] for _ in texts]  # return empty keyword list for each original input

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
    feature_names = vectorizer.get_feature_names_out()

    keywords_list = []
    cleaned_index = 0

    for original in texts:
        if not isinstance(original, str) or not original.strip():
            keywords_list.append([])
        else:
            row_data = tfidf_matrix[cleaned_index].toarray().flatten()
            top_indices = row_data.argsort()[-top_k:][::-1]
            keywords = [feature_names[i] for i in top_indices if row_data[i] > 0]
            keywords_list.append(keywords)
            cleaned_index += 1

    return keywords_list
