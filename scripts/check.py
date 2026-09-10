"""Small static-site validation for the generated public output."""
from pathlib import Path

site = Path(__file__).resolve().parents[1] / "site"
pages = ["index.html", "publications.html", "activities.html", "profile.html", "404.html"]
for page in pages:
    content = (site / page).read_text(encoding="utf-8")
    assert '<main id="main">' in content, page
    assert "渡邊 健太" in content, page
    assert 'href="style.css"' in content, page
assert (site / "style.css").stat().st_size > 1000
assert "3-Dimensional Conductive Pathways" in (site / "publications.html").read_text(encoding="utf-8")
print("Static site validation passed.")
