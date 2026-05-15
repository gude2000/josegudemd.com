#!/usr/bin/env python3
"""
Build a static JSON search index of all site pages.
Output: assets/data/search-index-en.json  and  assets/data/search-index-es.json
The index contains, per page: url, title, eyebrow, description, snippet (first ~600 chars of <main>).
The runtime search loads the file once and does substring + word matching client-side.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "assets" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Pages we don't want indexed (redirect stubs, raw widget assets, drafts, etc.)
EXCLUDES = {
    "404.html",
}


def strip_html(html: str) -> str:
    """Remove HTML tags + collapse whitespace."""
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = (text
            .replace("&mdash;", "—").replace("&middot;", "·")
            .replace("&amp;", "&").replace("&nbsp;", " ")
            .replace("&quot;", '"').replace("&apos;", "'")
            .replace("&lt;", "<").replace("&gt;", ">"))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_meta(html: str):
    """Pull <title>, <meta description>, hero <h1>, eyebrow, and the first ~600 chars of <main>."""
    title_m = re.search(r"<title>(.*?)</title>", html, re.S)
    title = strip_html(title_m.group(1)) if title_m else ""
    title = title.replace(" — José Gude MD", "").replace(" &mdash; José Gude MD", "").strip()

    desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
    desc = desc_m.group(1).replace("&mdash;", "—") if desc_m else ""

    eyebrow_m = re.search(r'<p class="eyebrow"[^>]*>(.*?)</p>', html, re.S)
    eyebrow = strip_html(eyebrow_m.group(1)) if eyebrow_m else ""

    # extract <main> for snippet
    main_m = re.search(r"<main[^>]*>(.*?)</main>", html, re.S)
    main_text = strip_html(main_m.group(1)) if main_m else strip_html(html)
    snippet = main_text[:600]

    return title, desc, eyebrow, snippet


def is_redirect_stub(html: str) -> bool:
    return bool(re.search(r'<meta\s+http-equiv="refresh"', html, re.I))


def build_index(directory: Path, url_prefix: str = ""):
    entries = []
    for p in sorted(directory.glob("*.html")):
        if p.name in EXCLUDES:
            continue
        html = p.read_text(encoding="utf-8", errors="ignore")
        if is_redirect_stub(html):
            continue
        # skip the assets/* internal pages (widgets that have no nav)
        if "<nav class=\"nav\">" not in html:
            continue
        title, desc, eyebrow, snippet = extract_meta(html)
        if not title:
            continue
        entries.append({
            "u": url_prefix + p.name,
            "t": title,
            "e": eyebrow,
            "d": desc,
            "s": snippet,
        })
    return entries


def main():
    en_entries = build_index(ROOT, "")
    es_entries = build_index(ROOT / "es", "es/")

    en_path = DATA_DIR / "search-index-en.json"
    es_path = DATA_DIR / "search-index-es.json"

    en_path.write_text(json.dumps(en_entries, ensure_ascii=False, separators=(",", ":")),
                       encoding="utf-8")
    es_path.write_text(json.dumps(es_entries, ensure_ascii=False, separators=(",", ":")),
                       encoding="utf-8")

    print(f"EN index: {len(en_entries)} pages, {en_path.stat().st_size/1024:.1f} KB → {en_path}")
    print(f"ES index: {len(es_entries)} pages, {es_path.stat().st_size/1024:.1f} KB → {es_path}")


if __name__ == "__main__":
    main()
