#!/usr/bin/env python3
"""Batch 1 sitewide edits (October 2026).

1. Byline: "José Gude MD" -> "Jose Gude MD" (author byline only; the
   character José Gude in the novels keeps his accent).
2. Navigation: add "In Progress" / "En curso" after Books / Libros.
3. Footer: add the Symposium YouTube channel link.

Idempotent: running it twice changes nothing the second time.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
YT = "https://www.youtube.com/@symposium-youtube"

BYLINE = [
    ("José Gude MD", "Jose Gude MD"),
    ("Jos&eacute; Gude MD", "Jose Gude MD"),
    ("José Gude, MD", "Jose Gude, MD"),
    ("Jos&eacute; Gude, MD", "Jose Gude, MD"),
    # book bylines and composition credits (author, not character)
    ("A Novel by José Gude", "A Novel by Jose Gude"),
    ("Una novela de José Gude", "Una novela de Jose Gude"),
    ("The Field Trilogy by Dr. José Gude", "The Field Trilogy by Dr. Jose Gude"),
    ("del Dr. José Gude — tres volúmenes", "del Dr. Jose Gude — tres volúmenes"),
    ("original composition · José Gude", "original composition · Jose Gude"),
    ("composición original · José Gude", "composición original · Jose Gude"),
    ("José Gude's own term", "Jose Gude's own term"),
    ("Término propio de José Gude", "Término propio de Jose Gude"),
    ("el término propio de José Gude", "el término propio de Jose Gude"),
    ("what José Gude calls", "what Jose Gude calls"),
    ("lo que José Gude llama", "lo que Jose Gude llama"),
    ("La Apuesta Voluntarista &nbsp;|&nbsp; José Gude", "La Apuesta Voluntarista &nbsp;|&nbsp; Jose Gude"),
]

NAV_EN = re.compile(r'(<li><a href="index\.html"[^>]*>Books</a></li>)')
NAV_ES = re.compile(r'(<li><a href="index\.html"[^>]*>Libros</a></li>)')
WIP_EN = '\n      <li><a href="works-in-progress.html">In Progress</a></li>'
WIP_ES = '\n      <li><a href="works-in-progress.html">En curso</a></li>'

FOOT_EN = re.compile(r'(<li><a href="mailto:contact@josegudemd\.com">Contact</a></li>)')
FOOT_ES = re.compile(r'(<li><a href="mailto:contact@josegudemd\.com">Contacto</a></li>)')
YT_LI = f'\n      <li><a href="{YT}" target="_blank" rel="noopener">YouTube</a></li>'


def process(path: pathlib.Path, spanish: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    for old, new in BYLINE:
        text = text.replace(old, new)
    if "works-in-progress.html" not in text:
        text = (NAV_ES if spanish else NAV_EN).sub(
            lambda m: m.group(1) + (WIP_ES if spanish else WIP_EN), text, count=1)
    footer = text.split("<footer>")[-1] if "<footer>" in text else ""
    if footer and YT not in footer:
        text = (FOOT_ES if spanish else FOOT_EN).sub(lambda m: m.group(1) + YT_LI, text, count=1)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    changed = 0
    for p in sorted(ROOT.glob("*.html")):
        changed += process(p, spanish=False)
    for p in sorted((ROOT / "es").glob("*.html")):
        changed += process(p, spanish=True)
    for p in [ROOT / "sitemap.xml", ROOT / "build_search_index.py",
              ROOT / "build_synthesis_book.py", *ROOT.glob("scripts/*.py")]:
        if p.name == "batch1_sitewide.py" or not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        n = t
        for old, new in BYLINE:
            n = n.replace(old, new)
        if n != t:
            p.write_text(n, encoding="utf-8")
            changed += 1
    print(f"files changed: {changed}")


if __name__ == "__main__":
    main()
