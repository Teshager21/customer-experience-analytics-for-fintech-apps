import re
import spacy

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])


def preprocess_reviews(text):
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", "", text)
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(tokens)
