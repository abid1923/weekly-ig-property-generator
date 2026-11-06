import re
from datetime import datetime, timedelta, timezone

import feedparser

FEEDS = [
    {"name": "Google News - properti",
     "url": "https://news.google.com/rss/search?q=properti+indonesia&hl=id&gl=ID&ceid=ID:id",
     "needs_filter": False},
    {"name": "Google News - KPR",
     "url": "https://news.google.com/rss/search?q=harga+rumah+KPR&hl=id&gl=ID&ceid=ID:id",
     "needs_filter": False},
    {"name": "Google News - apartemen & hunian",
     "url": "https://news.google.com/rss/search?q=apartemen+hunian+perumahan&hl=id&gl=ID&ceid=ID:id",
     "needs_filter": False},
    {"name": "CNBC Indonesia",
     "url": "https://www.cnbcindonesia.com/rss",
     "needs_filter": True},
]

KEYWORDS = ["properti", "rumah", "kpr", "hunian", "apartemen", "perumahan",
            "tanah", "developer", "bi rate", "suku bunga", "subsidi", "fldp"]

MAX_AGE_DAYS = 7


def _normalize(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())[:60]


def _clean_title(entry) -> tuple[str, str]:
    """Google News menulis judul 'Judul - Sumber'. Pisahkan keduanya."""
    title = entry.get("title", "").strip()
    source = entry.get("source", {}).get("title", "") if entry.get("source") else ""
    if source and title.endswith(f" - {source}"):
        title = title[: -len(source) - 3].strip()
    elif " - " in title:
        title, source = title.rsplit(" - ", 1)
    return title.strip(), (source or "unknown").strip()


def fetch_articles(max_age_days: int = MAX_AGE_DAYS) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    seen, articles = set(), []

    for f in FEEDS:
        try:
            feed = feedparser.parse(f["url"])
        except Exception as e:
            print(f"[WARN] gagal parse {f['name']}: {e}")
            continue
        if getattr(feed, "status", 200) != 200 or not feed.entries:
            print(f"[WARN] {f['name']} kosong/error (status {getattr(feed, 'status', '?')})")
            continue

        for e in feed.entries:
            if not e.get("published_parsed"):
                continue
            published = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
            if published < cutoff:
                continue

            title, source = _clean_title(e)
            if not title:
                continue
            if f["needs_filter"] and not any(k in title.lower() for k in KEYWORDS):
                continue

            key = _normalize(title)
            if key in seen:
                continue
            seen.add(key)

            articles.append({
                "title": title,
                "source": source,
                "url": e.get("link", ""),
                "published": published.strftime("%Y-%m-%d"),
            })

    articles.sort(key=lambda a: a["published"], reverse=True)
    return articles


if __name__ == "__main__":
    for a in fetch_articles()[:10]:
        print(a["published"], "|", a["source"], "|", a["title"])