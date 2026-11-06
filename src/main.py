import json
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from fetch import fetch_articles
from generate import generate_posts

BASE = Path(__file__).resolve().parent.parent


def main():
    load_dotenv(BASE / ".env")
    articles = fetch_articles()
    print(f"Artikel lolos filter: {len(articles)}")
    if not articles:
        raise SystemExit("Tidak ada artikel, berhenti.")

    posts = generate_posts(articles[:12], n_posts=3)

    out_dir = BASE / "outputs"
    out_dir.mkdir(exist_ok=True)
    today = date.today().isoformat()

    (out_dir / f"posts-{today}.json").write_text(
        json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [f"# Weekly IG Posts - {today}\n"]
    for i, p in enumerate(posts, 1):
        md.append(f"## Post {i}\n")
        md.append(f"**Hook:** {p['hook']}\n")
        md.append(f"{p['caption']}\n")
        md.append(f"**CTA:** {p['cta']}\n")
        md.append(" ".join(p["hashtags"]) + "\n")
        md.append(f"Sumber: [{p['source_title']}]({p['source_url']}) ({p['source_name']})\n")
    (out_dir / f"posts-{today}.md").write_text("\n".join(md), encoding="utf-8")
    print("Selesai. Lihat folder outputs/")


if __name__ == "__main__":
    main()