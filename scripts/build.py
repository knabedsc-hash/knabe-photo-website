"""Generate the dependency-free static website for GitHub Pages."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site"
OUT.mkdir(exist_ok=True)
data = json.loads((ROOT / "content" / "achievements.json").read_text(encoding="utf-8"))

def esc(value):
    return escape(str(value))

def emphasize_authors(value):
    value = esc(value)
    return re.sub(r"(K\. Watanabe|Kenta Watanabe|渡邊健太)", r"<strong>\1</strong>", value)

def paper_anchor(paper, index):
    matches = (
        ("Stable Photoelectrochemical", "paper-photo"),
        ("Self-Closing of Cracks", "paper-cracks"),
        ("Solar water splitting over Rh", "paper-water"),
    )
    for prefix, anchor in matches:
        if paper["title"].startswith(prefix):
            return anchor
    return "paper-" + str(index + 1)

def paper_markup(paper, index):
    note = ""
    if paper.get("note"):
        note = '<p class="cover-note">' + esc(paper["note"]) + "</p>"
    return f'''<article class="paper" id="{paper_anchor(paper, index)}">
  <div class="paper-meta"><span>{esc(paper["year"])}</span><span>RESEARCH ARTICLE</span></div>
  <h3 lang="en">{esc(paper["title"])}</h3>
  <p class="authors" lang="en">{emphasize_authors(paper["authors"])}</p>
  <p class="citation" lang="en">{esc(paper["citation"])}</p>{note}
</article>'''

def records(items):
    list_items = []
    for item in items:
        lines = "".join("<p>" + emphasize_authors(re.sub(r"[ \t]+\r?\n", "\n", line).strip()) + "</p>" for line in item)
        list_items.append("<li>" + lines + "</li>")
    return '<ol class="record-list">' + "".join(list_items) + "</ol>"

def document(filename, title, description, body):
    pages = [("index.html", "研究"), ("publications.html", "論文・著書"), ("activities.html", "研究活動"), ("profile.html", "プロフィール")]
    navigation = "".join(
        f'<a href="{path}"' + (" aria-current=\"page\"" if path == filename else "") + f">{label}</a>"
        for path, label in pages
    )
    language_link = "english.html"
    return f'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light"><meta name="description" content="{esc(description)}">
  <meta property="og:type" content="website"><meta property="og:locale" content="ja_JP">
  <meta property="og:title" content="{esc(title)} | 渡邊 健太"><meta property="og:description" content="{esc(description)}">
  <title>{esc(title)} | 渡邊 健太 — Kenta Watanabe</title>
  <link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css">
</head>
<body>
  <a class="skip-link" href="#main">本文へ移動</a>
  <header class="site-header"><div class="container header-inner">
    <a class="brand" href="index.html" aria-label="渡邊健太 ホーム"><span class="brand-mark" aria-hidden="true">kw.</span><span class="brand-text">KENTA WATANABE<small>渡邊 健太 / 個人研究者サイト</small></span></a>
    <nav class="main-nav" aria-label="メインナビゲーション">{navigation}<a class="language-link" href="{language_link}">EN</a></nav>
  </div></header>
  <main id="main">{body}</main>
  <section class="contact-band" aria-label="研究者情報"><div class="container contact-inner"><div><p class="eyebrow">CONNECT</p><p>研究者情報・外部プロフィール</p></div><div class="footer-links"><a href="https://researchmap.jp/waken-photo">researchmap ↗</a><a href="https://orcid.org/0000-0003-0827-7381">ORCID ↗</a></div></div></section>
  <footer class="site-footer"><div class="container footer-inner"><span>© 2026 Kenta Watanabe</span><span>掲載情報の確認日：2026.09.10</span><a href="#main">ページ上部へ ↑</a></div></footer>
</body></html>'''

def write(filename, title, description, body):
    (OUT / filename).write_text(document(filename, title, description, body), encoding="utf-8")

papers = data["papers"]
by_prefix = lambda prefix: next(p for p in papers if p["title"].startswith(prefix))
featured = [by_prefix("3-Dimensional"), by_prefix("Self-Closing"), by_prefix("Stable Photoelectrochemical")]
home_template = (ROOT / "templates" / "home.html").read_text(encoding="utf-8")
featured_markup = "".join(paper_markup(p, papers.index(p)) for p in featured)
home = home_template.replace("{{selected_papers}}", featured_markup)
write("index.html", "光電気化学・全固体電池・光触媒の研究", "東京科学大学 物質理工学院 助教、渡邊健太の個人ウェブサイト。全固体系の光電気化学、光蓄電池、全固体電池、光触媒による水分解を研究しています。", home)

years = sorted({paper["year"] for paper in papers}, reverse=True)
year_nav = '<nav class="year-nav" aria-label="論文の発表年">' + "".join(f'<a href="#year-{year}">{year}</a>' for year in years) + "</nav>"
year_sections = "".join(
    f'<section class="year-section" id="year-{year}"><h2>{year}</h2>' + "".join(paper_markup(p, papers.index(p)) for p in papers if p["year"] == year) + "</section>"
    for year in years
)
publications = f'''<section class="page-intro container"><p class="eyebrow">PUBLICATIONS</p><h1>論文・著書</h1><p>光電気化学、全固体電池、光触媒に関する研究成果。</p></section>
<div class="container"><nav class="subnav" aria-label="業績の種類"><a href="#articles">原著論文（{len(papers)}件）</a><a href="#books">著書・解説等</a><a href="#patents">特許</a></nav></div>
<div class="container content-layout">{year_nav}<div><section id="articles"><p class="muted">太字：渡邊健太　*：責任著者（原資料の表記に基づく）</p>{year_sections}</section><section class="group-section" id="books"><p class="eyebrow">BOOKS &amp; OTHER WRITINGS</p><h2>著書・解説等</h2>{records(data["books"])}</section><section class="group-section" id="patents"><p class="eyebrow">PATENTS</p><h2>特許</h2>{records(data["patents"])}</section></div></div>'''
write("publications.html", "論文・著書", "渡邊健太の原著論文、著書・解説、特許。発表年別の研究業績一覧。", publications)

grant_items = [
    ("2026.04 — 2029.03", "科研費 基盤研究（S） / 研究分担者", "局所的イオンダイナミクスに基づく高イオン伝導体の創出"),
    ("2025.04 — 2028.03", "科研費 若手研究 / 研究代表者", "全固体電気化学系で動作するLiイオン脱挿入性p型半導体光電極の開発と動作原理解明"),
    ("2026.04 — 2028.03", "旭硝子財団 研究奨励 / 研究代表者", "全固体電気化学系で動作するLi⁺脱挿入性p型半導体光電極の開発と動作原理解明"),
    ("2026.04 — 2027.12", "加藤科学振興会 第35回研究助成金 / 研究代表者", "全固体電気化学系で機能するp型半導体光電極の開発と動作原理解明"),
    ("2026.07 — 2027.06", "東京科学大学 あすなろ研究奨励金 / 研究代表者", "全固体電気化学系で動作可能なLi⁺脱挿入性p型半導体光電極の開発と動作原理解明"),
    ("2025.09 — 2026.03", "東京科学大学 物質理工学院 研究賞助成 / 研究代表者", "走査型電子/プローブ顕微鏡を用いた全固体電池用複合体電極の微細構造と三次元的電子/イオン伝導経路の相関関係の解明"),
    ("2025.07 — 2026.03", "東京科学大学 社会変革チャレンジ賞 / 研究代表者", "新規光機能デバイスの創成を志向した全固体電気化学系で動作するLi⁺脱挿入性光電極の開発と動作原理解明"),
]
grants = '<div class="grant-grid">' + "".join(f'<article class="grant"><span class="eyebrow">{esc(period)}</span><h3>{esc(kind)}</h3><p>{esc(topic)}</p></article>' for period, kind, topic in grant_items) + "</div>"
activities = f'''<section class="page-intro container"><p class="eyebrow">ACTIVITIES</p><h1>研究活動</h1><p>学会発表、受賞、研究助成。</p></section><div class="container"><nav class="subnav" aria-label="研究活動の種類"><a href="#talks">招待講演・学会発表</a><a href="#awards">受賞</a><a href="#funding">研究助成</a></nav><section class="group-section" id="talks"><p class="eyebrow">TALKS &amp; PRESENTATIONS</p><h2>招待講演</h2>{records(data["invited"])}<details class="disclosure"><summary>国際学会発表（{len(data["international"])}件）</summary>{records(data["international"])}</details><details class="disclosure"><summary>国内学会発表（{len(data["domestic"])}件）</summary>{records(data["domestic"])}</details></section><section class="group-section" id="awards"><p class="eyebrow">AWARDS</p><h2>受賞</h2>{records(data["awards"])}</section><section class="group-section" id="funding"><p class="eyebrow">RESEARCH FUNDING</p><h2>研究助成</h2>{grants}</section></div>'''
write("activities.html", "研究活動", "渡邊健太の招待講演、国際・国内学会発表、受賞、競争的研究資金。", activities)

profile = (ROOT / "templates" / "profile.html").read_text(encoding="utf-8")
write("profile.html", "プロフィール", "渡邊健太のプロフィール。東京科学大学助教、博士（理学）。職歴、学歴、委員歴、所属学会、担当授業。", profile)
write("404.html", "ページが見つかりません", "お探しのページが見つかりませんでした。", '<section class="page-intro container"><p class="eyebrow">404</p><h1>ページが見つかりません</h1><p>上のメニューから、目的のページへお進みください。</p></section>')
(OUT / ".nojekyll").touch()
(OUT / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#102e3b"/><text x="8" y="44" fill="#92dbd1" font-family="Georgia,serif" font-size="38" letter-spacing="-4">kw.</text></svg>', encoding="utf-8")
print(f"Built 5 pages with {len(papers)} papers.")
