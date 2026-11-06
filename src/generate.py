import json
import os
from pathlib import Path

import groq
from groq import Groq

from validate import validate_posts

BASE = Path(__file__).resolve().parent.parent
MAX_ATTEMPTS = 3
MAX_TOKENS = 6000


def _format_articles(articles: list[dict]) -> str:
    return "\n".join(
        f"{i}. {a['title']} | sumber: {a['source']} | tanggal: {a['published']} | url: {a['url']}"
        for i, a in enumerate(articles, 1)
    )


def generate_posts(articles: list[dict], n_posts: int = 3) -> list[dict]:
    system = (BASE / "prompts" / "system.txt").read_text(encoding="utf-8")
    user = (BASE / "prompts" / "user.txt").read_text(encoding="utf-8")
    user = user.replace("{{N_POSTS}}", str(n_posts)).replace(
        "{{ARTICLES}}", _format_articles(articles)
    )
    user += f"\n\nPENTING: daftar \"posts\" HARUS berisi tepat {n_posts} objek."

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    print(f"Model dipakai: {model}")

    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.5,
                max_completion_tokens=MAX_TOKENS,
                reasoning_effort="low",
                response_format={"type": "json_object"},
            )
        except groq.BadRequestError as e:
            print(f"[Percobaan {attempt}] API error 400: {e}")
            continue

        choice = resp.choices[0]
        print(f"[Percobaan {attempt}] finish_reason={choice.finish_reason}")

        try:
            posts = json.loads(choice.message.content or "")["posts"]
            errors = validate_posts(posts, n_posts)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            posts, errors = [], [f"JSON tidak valid: {e}"]

        if not errors:
            print(f"Validasi lolos ({len(posts)} post).")
            return posts

        print("Validasi gagal:")
        for e in errors:
            print("  -", e)
        messages.append({"role": "assistant", "content": choice.message.content or ""})
        messages.append({"role": "user", "content":
            "Hasilmu belum memenuhi syarat:\n- " + "\n- ".join(errors) +
            "\nPerbaiki dan kirim ulang JSON lengkap."})

    raise SystemExit("Gagal menghasilkan output valid setelah beberapa percobaan.")