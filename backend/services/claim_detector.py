import re

FACT_KEYWORDS = ["according to", "report", "data shows", "research"]
CLAIM_KEYWORDS = ["said", "claimed", "warned", "accused", "stated"]
OPINION_KEYWORDS = ["suggests", "appears", "likely", "believed"]
DATA_PATTERN = r"\d+%|\d+\s?(million|billion|thousand)?"

def classify_sentence(sentence: str):
    s = sentence.lower()

    if re.search(DATA_PATTERN, s):
        return "DATA"

    if any(k in s for k in CLAIM_KEYWORDS):
        return "CLAIM"

    if any(k in s for k in FACT_KEYWORDS):
        return "FACT"

    if any(k in s for k in OPINION_KEYWORDS):
        return "OPINION"

    return "FACT"


def analyze_text_structure(text: str):
    sentences = re.split(r'(?<=[.!?]) +', text)

    results = []
    counts = {"FACT": 0, "CLAIM": 0, "OPINION": 0, "DATA": 0}

    for s in sentences:
        label = classify_sentence(s)
        counts[label] += 1
        results.append({
            "sentence": s,
            "type": label
        })

    return {
        "breakdown": counts,
        "sentences": results
    }