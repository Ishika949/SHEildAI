import re

GUIDANCE_TOPICS = {
    "Personal safety planning": {
        "title": "Plan for the things you can control",
        "introduction": "Practical steps can help you think through a situation before it happens.",
        "points": [
            "Share your plans with someone you trust when it feels appropriate.",
            "Keep a charged phone and important contacts accessible.",
            "Prefer places where you can reach other people or ask staff for help.",
            "If you feel at risk, prioritize getting to a safer place over collecting evidence.",
        ],
        "keywords": ["plan", "prepare", "trusted person", "phone", "contact", "public place"],
    },
    "Basic rights": {
        "title": "Know where to find reliable information",
        "introduction": "In India, the Constitution includes protections related to equality and personal liberty. The right process depends on the circumstances.",
        "points": [
            "Article 14 concerns equality before the law.",
            "Article 15 addresses discrimination, including discrimination on grounds of sex.",
            "Article 21 protects life and personal liberty.",
            "For a real situation, confirm current rules with an official source or local support organization.",
        ],
        "keywords": ["rights", "law", "legal", "constitution", "article", "discrimination"],
    },
    "When something feels unsafe": {
        "title": "Focus on immediate support",
        "introduction": "Use your judgment and choose steps that fit your circumstances.",
        "points": [
            "Move toward a populated place if you can do so safely.",
            "Contact a trusted person and explain where you are.",
            "Avoid confronting someone who may pose a danger.",
            "Contact local emergency services when there is immediate danger.",
        ],
        "keywords": ["unsafe", "scared", "danger", "followed", "threat", "help"],
    },
    "Emergency help": {
        "title": "Use local, current emergency guidance",
        "introduction": "Use the emergency number and services available in your area.",
        "points": [
            "If you are in India, 112 is the national emergency number. Check official sources for current details.",
            "Save contacts you trust on your own device.",
        ],
        "keywords": ["emergency", "call", "police", "number", "helpline", "SOS"],
    },
}

STOP_WORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "can",
    "do",
    "for",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "should",
    "the",
    "to",
    "what",
    "when",
    "where",
    "with",
}


def _terms(text):
    return {
        term
        for term in re.findall(r"[a-z0-9]+", text.lower())
        if len(term) > 1 and term not in STOP_WORDS
    }


def search_guidance(query, limit=2):
    query_terms = _terms(query)
    if not query_terms:
        return []
    matches = []
    for topic_name, topic in GUIDANCE_TOPICS.items():
        title_terms = _terms(topic["title"])
        keyword_terms = _terms(" ".join(topic["keywords"]))
        content_terms = _terms(" ".join([topic_name, topic["introduction"], *topic["points"]]))
        score = (
            3 * len(query_terms & keyword_terms)
            + 2 * len(query_terms & title_terms)
            + len(query_terms & content_terms)
        )
        if score:
            matches.append((score, topic_name, topic))
    matches.sort(key=lambda match: (-match[0], match[1]))
    if not matches:
        return []
    minimum_score = max(1, matches[0][0] // 2)
    return [
        {"topic": topic_name, **topic}
        for score, topic_name, topic in matches
        if score >= minimum_score
    ][:limit]
