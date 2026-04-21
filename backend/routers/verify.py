from fastapi import APIRouter
import feedparser
import urllib.parse
from sentence_transformers import SentenceTransformer, util
from urllib.parse import urlparse

router = APIRouter()

model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔥 Trusted domains
TRUSTED_SOURCES = [
    "bbc.com",
    "reuters.com",
    "nytimes.com",
    "theguardian.com",
    "cnn.com"
]


def extract_real_domain(title):
    parts = title.split(" - ")
    if len(parts) > 1:
        return parts[-1].lower()
    return "unknown"


@router.post("/verify")
async def verify_news(data: dict):
    text = data.get("text")

    if not text:
        return {"error": "No input text"}

    # 🔹 STEP 1: Clean query
    query = urllib.parse.quote(text[:120])
    url = f"https://news.google.com/rss/search?q={query}"

    try:
        feed = feedparser.parse(url)
        articles = feed.entries[:8]
    except:
        return {
            "verification_status": "Error",
            "confidence": 0,
            "sources": []
        }

    if not articles:
        return {
            "verification_status": "No Data",
            "confidence": 0,
            "sources": []
        }

    # 🔹 STEP 2: Embeddings
    input_emb = model.encode(text, convert_to_tensor=True)

    results = []
    trusted_count = 0

    for article in articles:
        title = article.title
        link = article.link

        emb = model.encode(title, convert_to_tensor=True)
        similarity = util.cos_sim(input_emb, emb).item()

        domain = extract_real_domain(title)

        # 🔥 Credibility scoring
        if any(t in domain for t in TRUSTED_SOURCES):
            credibility = 1
        elif domain in ["msn", "yahoo", "google"]:
            credibility = 0.6
        else:
            credibility = 0.4

        if credibility == 1:
            trusted_count += 1

        results.append({
            "title": title,
            "url": link,
            "similarity": similarity,
            "domain": domain,
            "credibility": credibility
        })

    # 🔹 STEP 3: Sort by similarity
    results.sort(key=lambda x: x["similarity"], reverse=True)
    top = results[:5]

    # 🔹 STEP 4: Compute scores
    avg_similarity = sum(r["similarity"] for r in top) / len(top)
    avg_credibility = sum(r["credibility"] for r in top) / len(top)
    agreement = sum(1 for r in top if r["similarity"] > 0.5) / len(top)

    # 🔥 FINAL SCORE
    final_score = (
        0.5 * avg_similarity +
        0.3 * avg_credibility +
        0.2 * agreement
    )

    # 🔹 STEP 5: Decision
    if final_score > 0.6:
        status = "Likely Real"
    elif final_score < 0.45:
        status = "Suspicious"
    else:
        status = "Uncertain"

    # 🔹 STEP 6: Explanation
    explanation = []

    if avg_similarity > 0.6:
        explanation.append("Strong match with existing news coverage")

    if agreement > 0.5:
        explanation.append("Multiple sources report similar claims")

    if avg_credibility > 0.7:
        explanation.append("Covered by high-credibility sources")

    if avg_credibility < 0.5:
        explanation.append("Sources have low or mixed credibility")

    if not explanation:
        explanation.append("Insufficient reliable evidence found")
    return {
        "verification_status": status,
        "confidence": round(final_score, 2),
        "metrics": {
            "similarity": round(avg_similarity, 2),
            "credibility": round(avg_credibility, 2),
            "agreement": round(agreement, 2)
        },
        "explanation": explanation,
        "sources": top
    }