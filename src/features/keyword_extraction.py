from sklearn.feature_extraction.text import TfidfVectorizer


def extract_keywords(texts, top_k=5):
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    keywords_list = []
    for row in tfidf_matrix:
        row_data = row.toarray().flatten()
        top_indices = row_data.argsort()[-top_k:][::-1]
        keywords = [feature_names[i] for i in top_indices if row_data[i] > 0]
        keywords_list.append(keywords)

    return keywords_list
