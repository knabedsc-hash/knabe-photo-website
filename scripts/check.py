"""Static-site validation for the generated public output."""
from pathlib import Path

site = Path(__file__).resolve().parents[1] / "site"
japanese_pages = ["index.html", "publications.html", "activities.html", "profile.html", "gallery.html", "links.html", "404.html"]
english_pages = ["index.html", "publications.html", "activities.html", "profile.html", "gallery.html", "links.html", "404.html"]
for page in japanese_pages:
    content = (site / page).read_text(encoding="utf-8")
    assert '<main id="main">' in content, page
    assert "渡邊 健太" in content, page
    assert 'href="style.css"' in content, page
for page in english_pages:
    content = (site / "en" / page).read_text(encoding="utf-8")
    assert '<main id="main">' in content, page
    assert "Kenta Watanabe" in content, page
    assert 'href="../style.css"' in content, page
assert (site / "style.css").stat().st_size > 1000
assert "Relationship Between Contact Resistance" in (site / "publications.html").read_text(encoding="utf-8")
jp_publications = (site / "publications.html").read_text(encoding="utf-8")
en_publications = (site / "en" / "publications.html").read_text(encoding="utf-8")
assert "太字：渡邊健太" not in jp_publications
assert "Bold: Kenta Watanabe" not in en_publications
assert jp_publications.count('class="record-authors"') == 9
assert en_publications.count('class="record-authors"') == 9
assert "Related Websites" in (site / "en" / "links.html").read_text(encoding="utf-8")
assert "Hirayama Laboratory" in (site / "en" / "links.html").read_text(encoding="utf-8")
assert "研究室・センター" in (site / "links.html").read_text(encoding="utf-8")
assert "学会" in (site / "links.html").read_text(encoding="utf-8")
assert "Laboratories &amp; Centers" in (site / "en" / "links.html").read_text(encoding="utf-8")
assert "Academic Societies" in (site / "en" / "links.html").read_text(encoding="utf-8")
assert "電気化学会" in (site / "links.html").read_text(encoding="utf-8")
assert "The Solid State Ionics Society of Japan" in (site / "en" / "links.html").read_text(encoding="utf-8")
assert "https://www.ssi-j.org/" in (site / "en" / "links.html").read_text(encoding="utf-8")
assert "https://catsj.jp/en" in (site / "en" / "links.html").read_text(encoding="utf-8")
assert "水分解" in (site / "gallery.html").read_text(encoding="utf-8")
assert "Research Video" in (site / "en" / "gallery.html").read_text(encoding="utf-8")
jp_profile = (site / "profile.html").read_text(encoding="utf-8")
en_profile = (site / "en" / "profile.html").read_text(encoding="utf-8")
assert jp_profile.index("2026年度 3・4Q") < jp_profile.index("2025年度 3・4Q")
assert en_profile.index("2026, 3–4Q") < en_profile.index("2025, 3–4Q")
assert (site / "gallery.html").read_text(encoding="utf-8").count('class="cover-credit"') == 13
assert (site / "en" / "gallery.html").read_text(encoding="utf-8").count('class="cover-credit"') == 13
assert "CC BY-NC 4.0" in (site / "gallery.html").read_text(encoding="utf-8")
assert (site / "gallery.html").read_text(encoding="utf-8").count("CC BY 4.0") == 2
assert len(list((site / "media" / "covers").glob("*.webp"))) == 13
assert (site / "media" / "videos" / "rhcrox-agtao3.mp4").is_file()
print("Static site validation passed.")