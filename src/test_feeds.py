import feedparser

FEEDS = [
    "https://news.google.com/rss/search?q=properti+indonesia&hl=id&gl=ID&ceid=ID:id",
    "https://news.google.com/rss/search?q=harga+rumah+KPR&hl=id&gl=ID&ceid=ID:id",
    "https://www.kompas.com/properti/rss",
    "https://www.cnbcindonesia.com/rss",
]

for url in FEEDS:
    feed = feedparser.parse(url)
    print("=" * 60)
    print(url)
    print("status:", getattr(feed, "status", "tidak ada"), "| jumlah artikel:", len(feed.entries))
    for e in feed.entries[:3]:
        print("-", e.get("title"), "|", e.get("published", "tanpa tanggal"))