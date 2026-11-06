import re

REQUIRED = ["topic", "source_title", "source_name", "source_url",
            "fact_basis", "hook", "caption", "cta", "hashtags"]
FORBIDDEN = ["link bio", "website kami", "portal kami", "anda", "judul", "artikel ini", "berita ini"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")


def validate_post(p: dict) -> list[str]:
    errs = []
    missing = [k for k in REQUIRED if not p.get(k)]
    if missing:
        return [f"field kosong/hilang: {missing}"]

    if len(p["hook"].split()) > 12:
        errs.append("hook lebih dari 12 kata")
    n_words = len(p["caption"].split())
    if not 50 <= n_words <= 110:
        errs.append(f"caption {n_words} kata (target 60-100)")
    if not isinstance(p["hashtags"], list) or not 5 <= len(p["hashtags"]) <= 8:
        errs.append("jumlah hashtag harus 5-8")
    elif not all(h.startswith("#") and " " not in h for h in p["hashtags"]):
        errs.append("format hashtag salah")
    if len(EMOJI.findall(p["caption"])) > 3:
        errs.append("emoji lebih dari 3")

    text = (p["caption"] + " " + p["cta"]).lower()
    for w in FORBIDDEN:
        if re.search(rf"\b{re.escape(w)}\b", text):
            errs.append(f"mengandung frasa terlarang: '{w}'")
    return errs


def validate_posts(posts: list[dict], n_expected: int) -> list[str]:
    errs = []
    if len(posts) != n_expected:
        errs.append(f"jumlah post {len(posts)}, seharusnya {n_expected}")
    if len({p.get("topic") for p in posts}) < len(posts):
        errs.append("ada topik yang sama antar post")
    if len({p.get("source_url") for p in posts}) < len(posts):
        errs.append("ada sumber berita yang sama antar post")
    for i, p in enumerate(posts, 1):
        errs += [f"post {i}: {e}" for e in validate_post(p)]
    return errs