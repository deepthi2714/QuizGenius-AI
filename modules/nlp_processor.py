"""NLP preprocessing with NLTK (falls back to plain Python if NLTK data is unavailable)."""
import re
from collections import Counter

try:
    import nltk
except ImportError:  # pragma: no cover
    nltk = None

FALLBACK_STOPWORDS = set(
    """a about above after again all also am an and any are as at be because been before being below between both
    but by can could did do does doing down during each few for from further had has have having he her here hers
    him his how i if in into is it its itself just me more most my no nor not now of off on once only or other our
    out over own same she should so some such than that the their them then there these they this those through to
    too under until up very was we were what when where which while who whom why will with would you your""".split()
)
_READY = None


def _ensure_nltk():
    global _READY
    if _READY is not None:
        return _READY
    if nltk is None:
        _READY = False
        return False
    ok = True
    for pkg, path in [("punkt", "tokenizers/punkt"), ("punkt_tab", "tokenizers/punkt_tab"), ("stopwords", "corpora/stopwords")]:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                ok = False
    _READY = ok
    return ok


def _stopwords():
    if _ensure_nltk():
        try:
            from nltk.corpus import stopwords
            return set(stopwords.words("english"))
        except Exception:
            pass
    return FALLBACK_STOPWORDS


def split_sentences(text: str):
    if _ensure_nltk():
        try:
            return [s.strip() for s in nltk.sent_tokenize(text) if s.strip()]
        except Exception:
            pass
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def tokenize_words(text: str):
    return re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text)


def preprocess(text: str, top_k: int = 12) -> dict:
    """Clean text, tokenize sentences, remove stop words and rank keywords by frequency."""
    text = re.sub(r"\s+", " ", text or "").strip()
    sentences = split_sentences(text)
    stops = _stopwords()
    words = [w.lower() for w in tokenize_words(text)]
    content = [w for w in words if w not in stops and len(w) > 3]
    keywords = [w for w, _ in Counter(content).most_common(top_k)]
    return {
        "cleaned_text": " ".join(sentences),
        "sentences": sentences,
        "keywords": keywords,
        "word_count": len(words),
    }
