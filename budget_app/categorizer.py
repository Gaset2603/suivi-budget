from __future__ import annotations

import re
import unicodedata

STOPWORDS = {
    "le", "la", "les", "de", "du", "des", "au", "aux", "et", "en", "un", "une",
    "pour", "sur", "par", "avec", "sans", "est", "que", "qui", "dans", "ce",
    "cet", "cette", "son", "sa", "ses", "mon", "ma", "mes", "carte",
    "the", "a", "an", "of", "to", "in", "on", "for", "and",
}


def normalize(text) -> str:
    text = unicodedata.normalize("NFD", str(text).lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def auto_categorize(db, label: str):
    norm = normalize(label)
    if not norm:
        return None
    best_id, best_score = None, 0
    for cat in db.get_categories():
        score = 0
        for kw in cat.keywords_list():
            kn = normalize(kw)
            if kn and re.search(r"\b" + re.escape(kn) + r"\b", norm):
                score += 1 + len(kn.split())
        if score > best_score:
            best_score, best_id = score, cat.id
    return best_id


def learn(db, label: str, category_id: int):
    cat = db.get_category(category_id)
    if cat is None:
        raise ValueError("catégorie inconnue")
    keywords = {normalize(k) for k in cat.keywords_list()}
    for token in normalize(label).split():
        if len(token) >= 4 and token not in STOPWORDS:
            keywords.add(token)
    db.set_category_keywords(category_id, ",".join(sorted(keywords)))
