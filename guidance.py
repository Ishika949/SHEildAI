import re

GUIDANCE_TOPICS = {
    "Women's Safety Rules": {
        "title": "Women's Safety Rules",
        "introduction": "",
        "points": [
            "Stay aware of your surroundings.",
            "Keep emergency contacts easily accessible.",
            "Inform a trusted person when travelling alone.",
            "Avoid sharing personal information with strangers.",
            "Move to a safe and populated place if you feel unsafe.",
            "Report serious safety concerns to the appropriate authorities.",
        ],
        "ordered": True,
        "keywords": [
            "safety",
            "rules",
            "aware",
            "surroundings",
            "contact",
            "travel",
            "strangers",
        ],
    },
    "Legal Rights in India": {
        "title": "Legal Rights in India",
        "introduction": (
            "Indian law provides various protections against offences and unfair "
            "treatment of women."
        ),
        "points": [
            "Protection against sexual harassment",
            "Protection against stalking",
            "Protection against certain forms of assault",
            "Protection against cruelty and certain marriage-related offences",
            "Protection under the Bharatiya Nyaya Sanhita, 2023",
        ],
        "note": (
            "This information is provided for educational awareness and is not "
            "legal advice."
        ),
        "keywords": [
            "rights",
            "law",
            "legal",
            "harassment",
            "stalking",
            "assault",
            "cruelty",
            "Bharatiya Nyaya Sanhita",
        ],
    },
    "Constitutional Rights": {
        "title": "Constitutional Rights",
        "introduction": "",
        "points": [
            "Article 14 – Equality before law.",
            "Article 15 – Prohibits discrimination on grounds including sex.",
            "Article 15(3) – Special provisions can be made for women and children.",
            "Article 16 – Equal opportunity in public employment.",
            "Article 21 – Right to life and personal liberty.",
            "Article 39(d) – Equal pay for equal work.",
            "Article 42 – Humane working conditions and maternity relief.",
        ],
        "note": (
            "These provisions support equality, dignity and protection of women."
        ),
        "ordered": False,
        "keywords": [
            "constitution",
            "constitutional",
            "rights",
            "article",
            "equality",
            "discrimination",
            "employment",
            "maternity",
        ],
    },
    "What To Do in an Unsafe Situation": {
        "title": "What To Do in an Unsafe Situation",
        "introduction": "",
        "points": [
            "Move towards a safe and populated place.",
            "Contact a trusted family member, friend or teacher.",
            "Seek emergency help if there is immediate danger.",
            "Clearly explain your situation to someone you trust.",
            "Avoid confronting someone who may be dangerous.",
            "Report the incident to the appropriate authority when appropriate.",
        ],
        "ordered": True,
        "warning": (
            "If you are in immediate danger, focus on reaching a safe place "
            "and getting help."
        ),
        "keywords": [
            "unsafe",
            "scared",
            "danger",
            "followed",
            "threat",
            "help",
            "emergency",
            "call",
            "police",
            "number",
            "helpline",
            "SOS",
        ],
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
