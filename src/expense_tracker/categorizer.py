import re
from difflib import SequenceMatcher


CATEGORIES = [
    "Mad",
    "Transport",
    "Bolig",
    "Underholdning",
    "Kosmetik og personlig pleje",
    "Shopping",
    "Abonnementer",
    "Andet",
]


KEYWORDS = {
    "Mad": [
        "netto",
        "rema",
        "rema 1000",
        "føtex",
        "bilka",
        "lidl",
        "meny",
        "coop",
        "restaurant",
        "cafe",
        "pizza",
        "burger",
    ],
    "Transport": [
        "dsb",
        "rejsekort",
        "movia",
        "metro",
        "taxi",
        "uber",
        "bolt",
        "parking",
        "benzin",
    ],
    "Bolig": [
        "rent",
        "husleje",
        "electricity",
        "water",
        "heating",
        "internet",
    ],
    "Underholdning": [
        "cinema",
        "biograf",
        "netflix",
        "steam",
        "playstation",
        "xbox",
        "concert",
        "museum",
        "tivoli",
    ],
    "Kosmetik og personlig pleje": [
        "matas",
        "sephora",
        "normal",
        "makeup",
        "cosmetics",
        "shampoo",
        "haircut",
        "frisør",
        "skincare",
    ],
    "Shopping": [
        "h&m",
        "zara",
        "zalando",
        "magasin",
        "ikea",
        "jysk",
        "amazon",
        "asos",
    ],
    "Abonnementer": [
        "spotify",
        "hbo",
        "disney+",
        "apple music",
        "youtube premium",
        "adobe",
        "icloud",
        "subscription",
        "abonnement",
    ],
}


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9æøå+& ]+", " ", text)
    return re.sub(r"\s+", " ", text)


def suggest_category(description):
    normalized = normalize(description)

    if not normalized:
        return "Andet"

    best_category = "Andet"
    best_score = 0

    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            candidate = normalize(keyword)

            if candidate in normalized:
                return category

            score = SequenceMatcher(None, normalized, candidate).ratio()
            if score > best_score:
                best_category = category
                best_score = score

    if best_score >= 0.72:
        return best_category

    return "Andet"
