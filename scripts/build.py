"""Generate the dependency-free bilingual static website for GitHub Pages."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site"
EN_OUT = OUT / "en"
OUT.mkdir(exist_ok=True)
EN_OUT.mkdir(exist_ok=True)
data = json.loads((ROOT / "content" / "achievements.json").read_text(encoding="utf-8"))
last_updated = data["updated"].replace("-", ".")


def esc(value):
    return escape(str(value))


def emphasize_authors(value):
    value = esc(value)
    return re.sub(r"(K\. Watanabe|Kenta Watanabe|渡邊健太)", r"<strong>\1</strong>", value)


def paper_anchor(paper, index):
    matches = (
        ("Relationship Between Contact Resistance", "paper-contact-resistance"),
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


def japanese_document(filename, title, description, body):
    pages = [("index.html", "研究"), ("publications.html", "論文・著書"), ("activities.html", "研究活動"), ("profile.html", "プロフィール"), ("gallery.html", "ギャラリー"), ("links.html", "関連サイト")]
    navigation = "".join(
        f'<a href="{path}"' + (" aria-current=\"page\"" if path == filename else "") + f">{label}</a>"
        for path, label in pages
    )
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
    <nav class="main-nav" aria-label="メインナビゲーション">{navigation}<a class="language-link" href="en/index.html">EN</a></nav>
  </div></header>
  <main id="main">{body}</main>
  <section class="contact-band" aria-label="研究者情報"><div class="container contact-inner"><div><p class="eyebrow">CONNECT</p><p>研究者情報・外部プロフィール</p></div><div class="footer-links"><a href="https://researchmap.jp/waken-photo" target="_blank" rel="noopener noreferrer">researchmap ↗</a><a href="https://orcid.org/0000-0003-0827-7381" target="_blank" rel="noopener noreferrer">ORCID ↗</a></div></div></section>
  <footer class="site-footer"><div class="container footer-inner"><span>© 2026 Kenta Watanabe</span><span>掲載情報の確認日：{last_updated}</span><a href="#main">ページ上部へ ↑</a></div></footer>
</body></html>'''


def english_document(filename, title, description, body):
    pages = [("index.html", "Research"), ("publications.html", "Publications"), ("activities.html", "Activities"), ("profile.html", "Profile"), ("gallery.html", "Gallery"), ("links.html", "Links")]
    navigation = "".join(
        f'<a href="{path}"' + (" aria-current=\"page\"" if path == filename else "") + f">{label}</a>"
        for path, label in pages
    )
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light"><meta name="description" content="{esc(description)}">
  <meta property="og:type" content="website"><meta property="og:locale" content="en_US">
  <meta property="og:title" content="{esc(title)} | Kenta Watanabe"><meta property="og:description" content="{esc(description)}">
  <title>{esc(title)} | Kenta Watanabe</title>
  <link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../style.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header"><div class="container header-inner">
    <a class="brand" href="index.html" aria-label="Kenta Watanabe home"><span class="brand-mark" aria-hidden="true">kw.</span><span class="brand-text">KENTA WATANABE<small>Personal Academic Website</small></span></a>
    <nav class="main-nav" aria-label="Primary navigation">{navigation}<a class="language-link" href="../{filename}">日本語</a></nav>
  </div></header>
  <main id="main">{body}</main>
  <section class="contact-band" aria-label="Researcher profiles"><div class="container contact-inner"><div><p class="eyebrow">CONNECT</p><p>Researcher profiles</p></div><div class="footer-links"><a href="https://researchmap.jp/waken-photo?lang=en" target="_blank" rel="noopener noreferrer">researchmap ↗</a><a href="https://orcid.org/0000-0003-0827-7381" target="_blank" rel="noopener noreferrer">ORCID ↗</a></div></div></section>
  <footer class="site-footer"><div class="container footer-inner"><span>© 2026 Kenta Watanabe</span><span>Information verified: September 14, 2026</span><a href="#main">Back to top ↑</a></div></footer>
</body></html>'''


def write_jp(filename, title, description, body):
    (OUT / filename).write_text(japanese_document(filename, title, description, body), encoding="utf-8")


def write_en(filename, title, description, body):
    (EN_OUT / filename).write_text(english_document(filename, title, description, body), encoding="utf-8")


papers = data["papers"]
by_prefix = lambda prefix: next(paper for paper in papers if paper["title"].startswith(prefix))
featured = [
    by_prefix("Relationship Between Contact Resistance"),
    by_prefix("3-Dimensional"),
    by_prefix("Self-Closing"),
    by_prefix("Stable Photoelectrochemical"),
    by_prefix("Solar water splitting over Rh"),
]
featured_markup = "".join(paper_markup(paper, papers.index(paper)) for paper in featured)

home_template = (ROOT / "templates" / "home.html").read_text(encoding="utf-8")
write_jp("index.html", "光電気化学・全固体電池・光触媒の研究", "東京科学大学 物質理工学院 助教、渡邊健太の個人ウェブサイト。全固体系の光電気化学、光蓄電池、全固体電池、光触媒による水分解を研究しています。", home_template.replace("{{selected_papers}}", featured_markup))

en_home = f'''<section class="hero container"><div class="hero-copy">
  <p class="eyebrow">KENTA WATANABE · RESEARCH</p><h1>Exploring energy<br>at the intersection<br>of <span>light and ions.</span></h1>
  <p class="hero-description">I study photoelectrochemical phenomena at solid interfaces and develop materials for solar-energy conversion and storage.</p>
  <div class="identity"><strong>Kenta Watanabe <span>Ph.D.</span></strong><p>Assistant Professor, School of Materials and Chemical Technology<br>Institute of Science Tokyo</p></div>
  <div class="actions"><a class="button" href="#research">Research <span aria-hidden="true">↓</span></a><a class="text-link" href="profile.html">Profile <span aria-hidden="true">↗</span></a></div>
</div><aside class="research-note"><div class="note-top"><span>RESEARCH FOCUS</span><span>01—03</span></div><p class="note-title">Light.<br><em>Ions.</em><br>Interfaces.</p><div class="note-rule"></div><p class="note-caption">Photoelectrochemistry · solid-state ionics · photocatalysis</p></aside></section>
<section class="research-section" id="research"><div class="container"><div class="section-heading"><div><p class="eyebrow">RESEARCH AREAS</p><h2>Research</h2></div></div><div class="research-grid">
<article><span class="topic-number">01 / PHOTOELECTROCHEMISTRY</span><h3>Solid-State Photoelectrochemistry and Photo-Rechargeable Batteries</h3><p>I investigate photoelectrochemical reactions at semiconductor/solid-electrolyte interfaces and light-driven lithium-ion (de)intercalation for solar-energy conversion and storage.</p></article>
<article><span class="topic-number">02 / SOLID-STATE BATTERIES</span><h3>Interfaces and Microstructures in All-Solid-State Batteries</h3><p>I study how composite-electrode microstructures and solid-electrolyte mechanical properties affect battery operation through operando microscopy and interface analysis.</p></article>
<article><span class="topic-number">03 / PHOTOCATALYSIS</span><h3>Water-Splitting Photocatalysts and Artificial Photosynthesis</h3><p>I develop metal-oxide photocatalysts that produce hydrogen and oxygen from water using sunlight, including band-structure-controlled materials and photocatalyst-electrolysis hybrid systems.</p></article>
</div></div></section>
<section class="container section"><div class="section-heading"><div><p class="eyebrow">SELECTED PUBLICATIONS</p><h2>Selected Publications</h2></div><a class="text-link" href="publications.html">All publications <span aria-hidden="true">↗</span></a></div>{featured_markup}</section>
<section class="container section recent-section"><div><p class="eyebrow">RECENT ACTIVITIES</p><h2>Recent Activities</h2><a class="text-link" href="activities.html">View activities <span aria-hidden="true">↗</span></a></div><div class="news-list">
<article><time datetime="2026-09">2026.09</time><div><span class="tag">PUBLICATION</span><h3>Paper accepted by Batteries &amp; Supercaps</h3><p>Contact resistance and mechanical properties in microstructure-controlled composite electrodes for all-solid-state batteries.</p></div></article>
<article><time datetime="2026-07">2026.07</time><div><span class="tag">RESEARCH FUNDING</span><h3>Institute of Science Tokyo Asunaro Research Grant</h3><p>Development and operating principles of a lithium-ion-deintercalating p-type semiconductor photoelectrode for all-solid-state electrochemical systems.</p></div></article>
<article><time datetime="2025-12-12">2025.12.12</time><div><span class="tag">INVITED TALK</span><h3>Materials Research Meeting 2025</h3><p>Photoelectrochemical Reactions in All-Solid-State Systems toward Solar Energy Conversion and Storage</p></div></article>
</div></section>'''
write_en("index.html", "Research", "Kenta Watanabe is an Assistant Professor at the Institute of Science Tokyo researching photoelectrochemistry, all-solid-state batteries, and photocatalysts.", en_home)

years = sorted({paper["year"] for paper in papers}, reverse=True)
year_nav = '<nav class="year-nav" aria-label="Publication years">' + "".join(f'<a href="#year-{year}">{year}</a>' for year in years) + "</nav>"
year_sections = "".join(f'<section class="year-section" id="year-{year}"><h2>{year}</h2>' + "".join(paper_markup(paper, papers.index(paper)) for paper in papers if paper["year"] == year) + "</section>" for year in years)

jp_publications = f'''<section class="page-intro container"><p class="eyebrow">PUBLICATIONS</p><h1>論文・著書</h1><p>光電気化学、全固体電池、光触媒に関する研究成果。</p></section><div class="container"><nav class="subnav" aria-label="業績の種類"><a href="#articles">原著論文（{len(papers)}件）</a><a href="#books">著書・解説等</a><a href="#patents">特許</a></nav></div><div class="container content-layout">{year_nav}<div><section id="articles"><p class="muted">太字：渡邊健太　*：責任著者（原資料の表記に基づく）</p>{year_sections}</section><section class="group-section" id="books"><p class="eyebrow">BOOKS &amp; OTHER WRITINGS</p><h2>著書・解説等</h2>{records(data["books"])}</section><section class="group-section" id="patents"><p class="eyebrow">PATENTS</p><h2>特許</h2>{records(data["patents"])}</section></div></div>'''
write_jp("publications.html", "論文・著書", "渡邊健太の原著論文、著書・解説、特許。発表年別の研究業績一覧。", jp_publications)

en_publications = f'''<section class="page-intro container"><p class="eyebrow">PUBLICATIONS</p><h1>Publications</h1><p>Research outputs in photoelectrochemistry, all-solid-state batteries, and photocatalysis.</p></section><div class="container"><nav class="subnav" aria-label="Publication types"><a href="#articles">Research articles ({len(papers)})</a><a href="#books">Books and other writings</a><a href="#patents">Patents</a></nav></div><div class="container content-layout">{year_nav}<div><section id="articles"><p class="muted">Bold: Kenta Watanabe. *: corresponding author, as shown in the source record.</p>{year_sections}</section><section class="group-section" id="books"><p class="eyebrow">BOOKS &amp; OTHER WRITINGS</p><h2>Books and Other Writings</h2>{records(data["books"])}</section><section class="group-section" id="patents"><p class="eyebrow">PATENTS</p><h2>Patents</h2>{records(data["patents"])}</section></div></div>'''
write_en("publications.html", "Publications", "Research articles, books, other writings, and patents by Kenta Watanabe.", en_publications)

jp_grant_items = [("2026.04 — 2029.03", "科研費 基盤研究（S） / 研究分担者", "局所的イオンダイナミクスに基づく高イオン伝導体の創出"), ("2025.04 — 2028.03", "科研費 若手研究 / 研究代表者", "全固体電気化学系で動作するLiイオン脱挿入性p型半導体光電極の開発と動作原理解明"), ("2026.04 — 2028.03", "旭硝子財団 研究奨励 / 研究代表者", "全固体電気化学系で動作するLi⁺脱挿入性p型半導体光電極の開発と動作原理解明"), ("2026.04 — 2027.12", "加藤科学振興会 第35回研究助成金 / 研究代表者", "全固体電気化学系で機能するp型半導体光電極の開発と動作原理解明"), ("2026.07 — 2027.06", "東京科学大学 あすなろ研究奨励金 / 研究代表者", "全固体電気化学系で動作可能なLi⁺脱挿入性p型半導体光電極の開発と動作原理解明"), ("2025.09 — 2026.03", "東京科学大学 物質理工学院 研究賞助成 / 研究代表者", "走査型電子/プローブ顕微鏡を用いた全固体電池用複合体電極の微細構造と三次元的電子/イオン伝導経路の相関関係の解明"), ("2025.07 — 2026.03", "東京科学大学 社会変革チャレンジ賞 / 研究代表者", "新規光機能デバイスの創成を志向した全固体電気化学系で動作するLi⁺脱挿入性光電極の開発と動作原理解明")]
en_grant_items = [("2026.04 — 2029.03", "JSPS KAKENHI Grant-in-Aid for Scientific Research (S) / Co-Investigator", "Creation of high ionic conductors based on local ion dynamics"), ("2025.04 — 2028.03", "JSPS KAKENHI Early-Career Scientists / Principal Investigator", "p-Type semiconductor photoelectrodes for all-solid-state electrochemical systems"), ("2026.04 — 2028.03", "Asahi Glass Foundation Research Grant / Principal Investigator", "p-Type semiconductor photoelectrodes for all-solid-state electrochemical systems"), ("2026.04 — 2027.12", "Kato Foundation Research Grant / Principal Investigator", "p-Type semiconductor photoelectrodes for all-solid-state electrochemical systems"), ("2026.07 — 2027.06", "Institute of Science Tokyo Asunaro Research Grant / Principal Investigator", "Lithium-ion-deintercalating photoelectrodes for all-solid-state electrochemical systems"), ("2025.09 — 2026.03", "Institute of Science Tokyo Research Award Grant / Principal Investigator", "Microstructure and three-dimensional conduction pathways in composite electrodes"), ("2025.07 — 2026.03", "Institute of Science Tokyo Social Transformation Challenge Award / Principal Investigator", "Lithium-ion-deintercalating photoelectrodes for all-solid-state electrochemical systems")]

def grant_grid(items):
    return '<div class="grant-grid">' + "".join(f'<article class="grant"><span class="eyebrow">{esc(period)}</span><h3>{esc(kind)}</h3><p>{esc(topic)}</p></article>' for period, kind, topic in items) + "</div>"

jp_activities = f'''<section class="page-intro container"><p class="eyebrow">ACTIVITIES</p><h1>研究活動</h1><p>学会発表、受賞、研究助成。</p></section><div class="container"><nav class="subnav" aria-label="研究活動の種類"><a href="#talks">招待講演・学会発表</a><a href="#awards">受賞</a><a href="#funding">研究助成</a></nav><section class="group-section" id="talks"><p class="eyebrow">TALKS &amp; PRESENTATIONS</p><h2>招待講演</h2>{records(data["invited"])}<details class="disclosure"><summary>国際学会発表（{len(data["international"])}件）</summary>{records(data["international"])}</details><details class="disclosure"><summary>国内学会発表（{len(data["domestic"])}件）</summary>{records(data["domestic"])}</details></section><section class="group-section" id="awards"><p class="eyebrow">AWARDS</p><h2>受賞</h2>{records(data["awards"])}</section><section class="group-section" id="funding"><p class="eyebrow">RESEARCH FUNDING</p><h2>研究助成</h2>{grant_grid(jp_grant_items)}</section></div>'''
write_jp("activities.html", "研究活動", "渡邊健太の招待講演、国際・国内学会発表、受賞、競争的研究資金。", jp_activities)

en_activities = f'''<section class="page-intro container"><p class="eyebrow">ACTIVITIES</p><h1>Activities</h1><p>Conference presentations, awards, and research funding.</p></section><div class="container"><nav class="subnav" aria-label="Activity types"><a href="#talks">Talks and presentations</a><a href="#awards">Awards</a><a href="#funding">Research funding</a></nav><section class="group-section" id="talks"><p class="eyebrow">TALKS &amp; PRESENTATIONS</p><h2>Invited Talks</h2>{records(data["invited"])}<details class="disclosure"><summary>International Conference Presentations ({len(data["international"])})</summary>{records(data["international"])}</details><details class="disclosure"><summary>Domestic Conference Presentations ({len(data["domestic"])})</summary>{records(data["domestic"])}</details></section><section class="group-section" id="awards"><p class="eyebrow">AWARDS</p><h2>Awards</h2>{records(data["awards"])}</section><section class="group-section" id="funding"><p class="eyebrow">RESEARCH FUNDING</p><h2>Research Funding</h2>{grant_grid(en_grant_items)}</section></div>'''
write_en("activities.html", "Activities", "Conference presentations, awards, and research funding of Kenta Watanabe.", en_activities)

teaching_jp = "".join(f'''<div><dt>{esc(course["term"].replace(",", "年度", 1).replace(",", "・"))}</dt><dd><h3>{esc(course["name"])}（{esc(course["code"])}）</h3><p lang="en">{esc(course["english"])}</p><p class="muted">{esc(course["affiliation"])}</p></dd></div>''' for course in data["teaching"])
jp_profile_template = (ROOT / "templates" / "profile.html").read_text(encoding="utf-8")
write_jp("profile.html", "プロフィール", "渡邊健太のプロフィール。東京科学大学助教、博士（理学）。職歴、学歴、委員歴、所属学会、担当授業。", jp_profile_template.replace("{{teaching}}", teaching_jp))

def english_affiliation(value):
    translations = {
        "東京科学大学 物質理工学院 応用化学系": "School of Materials and Chemical Technology, Institute of Science Tokyo",
        "東京工業大学 物質理工学院 応用化学系": "School of Materials and Chemical Technology, Tokyo Institute of Technology",
    }
    return translations.get(value, value)

def teaching_term_en(term):
    parts = [part.strip() for part in term.split(",")]
    return parts[0] + ", " + "–".join(parts[1:])

teaching_en = "".join(f'''<div><dt>{esc(teaching_term_en(course["term"]))}</dt><dd><h3>{esc(course["english"])} ({esc(course["code"])})</h3><p class="muted">{english_affiliation(course["affiliation"])}</p></dd></div>''' for course in data["teaching"])
en_profile = f'''<section class="page-intro container"><p class="eyebrow">PROFILE</p><h1>Profile</h1><p>Kenta Watanabe, Ph.D.</p></section><div class="container profile-layout"><aside class="profile-card"><p class="eyebrow">KENTA WATANABE</p><h2>Kenta Watanabe</h2><p>Ph.D. in Science<br>Assistant Professor<br>School of Materials and Chemical Technology<br>Institute of Science Tokyo</p><dl><dt>Researcher Number</dt><dd>00977209</dd><dt>ORCID</dt><dd><a href="https://orcid.org/0000-0003-0827-7381" target="_blank" rel="noopener noreferrer">0000-0003-0827-7381 ↗</a></dd></dl><a class="text-link" href="https://researchmap.jp/waken-photo?lang=en" target="_blank" rel="noopener noreferrer">researchmap ↗</a></aside><div>
<section class="profile-section"><p class="eyebrow">APPOINTMENTS</p><h2>Appointments</h2><dl class="timeline"><div><dt>Oct. 2024 — Present</dt><dd><h3>Assistant Professor, Institute of Science Tokyo</h3><p>Department of Chemical Science and Engineering, School of Materials and Chemical Technology</p></dd></div><div><dt>Jan. 2023 — Sep. 2024</dt><dd><h3>Assistant Professor, Tokyo Institute of Technology</h3><p>Department of Chemical Science and Engineering, School of Materials and Chemical Technology</p></dd></div><div><dt>Apr. 2021 — Dec. 2022</dt><dd><h3>Postdoctoral Researcher, National Institute of Advanced Industrial Science and Technology</h3><p>Global Zero Emission Research Center</p></dd></div></dl></section>
<section class="profile-section"><p class="eyebrow">EDUCATION</p><h2>Education</h2><dl class="timeline"><div><dt>Apr. 2018 — Mar. 2021</dt><dd><h3>Tokyo University of Science, Doctoral Program</h3><p>Department of Chemistry, Graduate School of Science<br>Ph.D. in Science, March 18, 2021</p></dd></div><div><dt>Apr. 2016 — Mar. 2018</dt><dd><h3>Tokyo University of Science, Master’s Program</h3><p>Department of Chemistry, Graduate School of Science<br>M.S. in Science, March 19, 2018</p></dd></div><div><dt>Apr. 2012 — Mar. 2016</dt><dd><h3>Tokyo University of Science</h3><p>Department of Applied Chemistry, Faculty of Science Division I</p></dd></div><div><dt>Apr. 2009 — Mar. 2012</dt><dd><h3>Taki Senior High School</h3></dd></div></dl></section>
<section class="profile-section"><p class="eyebrow">SERVICE</p><h2>Service and Professional Memberships</h2><dl class="timeline compact"><div><dt>Apr. 2025 — Present</dt><dd>Secretary, Editorial Committee of the Catalysis Society of Japan</dd></div><div><dt>Sep. 2023 — Present</dt><dd>Committee Member, Battery Technology Committee of The Electrochemical Society of Japan</dd></div><div><dt>Apr. 2018 — Present</dt><dd>Committee Member, Young Researchers Association of the Catalysis Society of Japan</dd></div></dl><p>The Solid State Ionics Society of Japan / The Electrochemical Society of Japan / Chemical Society of Japan / Catalysis Society of Japan / Japanese Photochemistry Association</p></section>
<section class="profile-section"><p class="eyebrow">TEACHING</p><h2>Teaching</h2><dl class="timeline compact">{teaching_en}</dl></section>
</div></div>'''
write_en("profile.html", "Profile", "Profile, appointments, education, service, and teaching of Kenta Watanabe.", en_profile)

resource_sites = [("東京科学大学 平山研究室", "Hirayama Laboratory, Institute of Science Tokyo", "http://www.hirayama-cap.mct.isct.ac.jp/", "http://www.hirayama-cap.mct.isct.ac.jp/en/", "全固体電池と固体イオニクスに関する研究室", "Research group on all-solid-state batteries and solid-state ionics"), ("東京科学大学 全固体電池研究センター", "All-Solid-State Battery Research Center, Institute of Science Tokyo", "http://www.assb.iir.isct.ac.jp/", "http://www.assb.iir.isct.ac.jp/en/", "全固体電池の研究拠点", "Research center for all-solid-state batteries"), ("東京理科大学 工藤研究室", "Kudo Laboratory, Tokyo University of Science", "https://www.rs.kagu.tus.ac.jp/kudolab/", "https://www.rs.kagu.tus.ac.jp/kudolab/en/index.html", "光触媒・人工光合成に関する研究室", "Research group on photocatalysis and artificial photosynthesis"), ("産業技術総合研究所 ゼロエミッション国際共同研究センター", "Global Zero Emission Research Center, AIST", "https://www.gzr.aist.go.jp/?lang=ja", "https://www.gzr.aist.go.jp/en/", "ゼロエミッション技術の研究拠点", "Research center for zero-emission technologies")]

def resource_cards(language):
    cards = []
    for jp_name, en_name, jp_url, en_url, jp_description, en_description in resource_sites:
        name, url, description = (jp_name, jp_url, jp_description) if language == "jp" else (en_name, en_url, en_description)
        cards.append(f'''<article class="resource-card"><p class="eyebrow">RELATED WEBSITE</p><h2>{esc(name)}</h2><p>{esc(description)}</p><a class="text-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer">Visit website <span aria-hidden="true">↗</span></a></article>''')
    return '<div class="link-grid">' + "".join(cards) + "</div>"

jp_links = f'''<section class="page-intro container"><p class="eyebrow">RELATED WEBSITES</p><h1>関連サイト</h1><p>所属・研究に関係する研究室と研究センターのウェブサイト。</p></section><section class="container section links-section">{resource_cards("jp")}</section>'''
write_jp("links.html", "関連サイト", "渡邊健太の所属・研究に関係する研究室と研究センターのウェブサイト。", jp_links)

en_links = f'''<section class="page-intro container"><p class="eyebrow">RELATED WEBSITES</p><h1>Related Websites</h1><p>Laboratories and research centers connected with my appointments and research.</p></section><section class="container section links-section">{resource_cards("en")}</section>'''
write_en("links.html", "Related Websites", "Laboratories and research centers connected with Kenta Watanabe’s appointments and research.", en_links)

cover_images = [
    ("2019ACSSustainChemEng", "2019", "ACS Sustainable Chemistry & Engineering", "Supplementary cover", "K. Watanabe et al., ACS Sustainable Chemistry & Engineering 2019, 7, 9881–9887.", "https://doi.org/10.1021/acssuschemeng.9b00513", "© 2019 American Chemical Society."),
    ("2020ChemMater", "2020", "Chemistry of Materials", "Supplementary cover", "K. Watanabe et al., Chemistry of Materials 2020, 32, 10524–10537.", "https://doi.org/10.1021/acs.chemmater.0c03461", "© 2020 American Chemical Society."),
    ("2020ChemSci", "2020", "Chemical Science", "Outside front cover", "K. Watanabe et al., Chemical Science 2020, 11, 2330–2334.", "https://doi.org/10.1039/C9SC05909A", "© 2020 Royal Society of Chemistry."),
    ("2021ChemComm", "2021", "Chemical Communications", "Outside back cover", "K. Watanabe et al., Chemical Communications 2021, 57, 323–326.", "https://doi.org/10.1039/D0CC07371G", "© 2021 Royal Society of Chemistry."),
    ("2023AdvEnergyMater", "2023", "Advanced Energy Materials", "Journal cover", "H. Zhou et al., Advanced Energy Materials 2023, 13, 2370183.", "https://doi.org/10.1002/aenm.202370183", "© 2023 Wiley-VCH GmbH."),
    ("2023BatteriesSupercaps", "2023", "Batteries & Supercaps", "Front cover", "Y. Yamada et al., Batteries & Supercaps 2023, 6, e202300412.", "https://doi.org/10.1002/batt.202300412", "© 2023 Wiley-VCH GmbH."),
    ("2024AdvMaterInterfaces", "2024", "Advanced Materials Interfaces", "Front cover", "J. Nakayama et al., Advanced Materials Interfaces 2024, 11, 2470014.", "https://doi.org/10.1002/admi.202470014", "© 2024 The Authors. Published by Wiley-VCH GmbH. Licensed under CC BY-NC 4.0.", "https://creativecommons.org/licenses/by-nc/4.0/"),
    ("2024ChemSci", "2024", "Chemical Science", "Inside front cover", "K. Watanabe et al., Chemical Science 2024, 15, 16025–16033.", "https://doi.org/10.1039/D4SC03978E", "© 2024 The Authors. Published by the Royal Society of Chemistry. Licensed under CC BY 4.0.", "https://creativecommons.org/licenses/by/4.0/"),
    ("2024NanoLett", "2024", "Nano Letters", "Supplementary cover", "K. Watanabe et al., Nano Letters 2024, 24, 1916–1922.", "https://doi.org/10.1021/acs.nanolett.3c03982", "© 2024 American Chemical Society."),
    ("2024SustainEnergyFuels", "2024", "Sustainable Energy & Fuels", "Inside front cover", "K. Watanabe et al., Sustainable Energy & Fuels 2024, 8, 1236–1244.", "https://doi.org/10.1039/D3SE01636F", "© 2024 The Authors. Published by the Royal Society of Chemistry. Licensed under CC BY 4.0.", "https://creativecommons.org/licenses/by/4.0/"),
    ("2025ACSApplEnergyMater", "2025", "ACS Applied Energy Materials", "Supplementary cover", "K. Watanabe et al., ACS Applied Energy Materials 2025, 8, 2260.", "https://doi.org/10.1021/acsaem.4c02838", "© 2025 American Chemical Society."),
    ("2025BatteriesSupercaps", "2025", "Batteries & Supercaps", "Front cover", "K. Watanabe et al., Batteries & Supercaps 2025, 8, e202580601.", "https://doi.org/10.1002/batt.202580601", "© 2025 Wiley-VCH GmbH."),
    ("2026BatteriesSupercaps", "2026", "Batteries & Supercaps", "Front cover", "B. Y. Kang et al., Batteries & Supercaps 2026, 9, e70378.", "https://doi.org/10.1002/batt.70378", "© 2026 Wiley-VCH GmbH."),
]

cover_images.sort(key=lambda cover: int(cover[1]), reverse=True)


def gallery_cards(language):
    prefix = "" if language == "jp" else "../"
    cards = []
    for cover in cover_images:
        stem, year, journal, cover_type, citation, doi, credit, *license_url = cover
        labels = {"Supplementary cover": "サプリメンタリーカバー", "Outside front cover": "表紙（Outside front cover）", "Outside back cover": "裏表紙（Outside back cover）", "Journal cover": "ジャーナルカバー", "Front cover": "表紙（Front cover）", "Inside front cover": "表紙（Inside front cover）"}
        kind = labels[cover_type] if language == "jp" else cover_type
        credit_html = esc(credit)
        if license_url:
            license_name = "CC BY-NC 4.0" if "by-nc" in license_url[0] else "CC BY 4.0"
            credit_html = credit_html.replace(license_name, f'<a href="{esc(license_url[0])}" target="_blank" rel="license noopener noreferrer">{license_name}</a>')
        heading = "出典・著作権" if language == "jp" else "Source & copyright"
        cards.append(f"""<article class="gallery-card"><div class="gallery-image-frame"><img src="{prefix}media/covers/{stem}.webp" alt="{esc(year + ' ' + journal + ' cover image')}" width="900" height="1200" loading="lazy"></div><div class="gallery-card-copy"><p class="eyebrow">{esc(year)} · {esc(kind.upper() if language == 'en' else kind)}</p><h2>{esc(journal)}</h2><div class="cover-credit"><p class="cover-credit-heading">{heading}</p><p class="cover-citation"><a href="{esc(doi)}" target="_blank" rel="noopener noreferrer">{esc(citation)} <span aria-hidden="true">↗</span></a></p><p class="cover-copyright">{credit_html}</p></div></div></article>""")
    return '<div class="gallery-grid">' + "".join(cards) + "</div>"


jp_gallery = f"""<section class="page-intro container"><p class="eyebrow">GALLERY</p><h1>ギャラリー</h1><p>採択論文のカバーピクチャーと、研究に関する動画。</p></section><div class="container"><nav class="subnav" aria-label="ギャラリーの種類"><a href="#covers">カバーピクチャー</a><a href="#video">研究動画</a></nav><section class="gallery-section" id="covers"><div class="section-heading"><div><p class="eyebrow">JOURNAL COVERS</p><h2>カバーピクチャー</h2></div></div>{gallery_cards("jp")}</section><section class="gallery-section video-section" id="video"><div class="section-heading"><div><p class="eyebrow">RESEARCH VIDEO</p><h2>研究動画</h2></div></div><article class="video-gallery-card"><div class="video-gallery-copy"><p class="eyebrow">WATER SPLITTING</p><h3>Rh<sub>0.5</sub>Cr<sub>1.5</sub>O<sub>3</sub>/AgTaO<sub>3</sub>を用いた紫外光照射下での水分解</h3><p>紫外光照射下における光触媒水分解の様子。</p></div><video class="gallery-video" controls preload="metadata"><source src="media/videos/rhcrox-agtao3.mp4" type="video/mp4">お使いのブラウザは動画再生に対応していません。</video></article></section></div>"""
write_jp("gallery.html", "ギャラリー", "渡邊健太の採択論文カバーピクチャーと研究動画。", jp_gallery)

en_gallery = f"""<section class="page-intro container"><p class="eyebrow">GALLERY</p><h1>Gallery</h1><p>Journal cover images and research videos.</p></section><div class="container"><nav class="subnav" aria-label="Gallery categories"><a href="#covers">Journal covers</a><a href="#video">Research video</a></nav><section class="gallery-section" id="covers"><div class="section-heading"><div><p class="eyebrow">JOURNAL COVERS</p><h2>Cover Images</h2></div></div>{gallery_cards("en")}</section><section class="gallery-section video-section" id="video"><div class="section-heading"><div><p class="eyebrow">RESEARCH VIDEO</p><h2>Research Video</h2></div></div><article class="video-gallery-card"><div class="video-gallery-copy"><p class="eyebrow">WATER SPLITTING</p><h3>Water splitting over Rh<sub>0.5</sub>Cr<sub>1.5</sub>O<sub>3</sub>/AgTaO<sub>3</sub> under ultraviolet irradiation</h3><p>Photocatalytic water splitting under ultraviolet irradiation.</p></div><video class="gallery-video" controls preload="metadata"><source src="../media/videos/rhcrox-agtao3.mp4" type="video/mp4">Your browser does not support video playback.</video></article></section></div>"""
write_en("gallery.html", "Gallery", "Journal cover images and a research video by Kenta Watanabe.", en_gallery)

write_jp("404.html", "ページが見つかりません", "お探しのページが見つかりませんでした。", '<section class="page-intro container"><p class="eyebrow">404</p><h1>ページが見つかりません</h1><p>上のメニューから、目的のページへお進みください。</p></section>')
write_en("404.html", "Page Not Found", "The requested page could not be found.", '<section class="page-intro container"><p class="eyebrow">404</p><h1>Page Not Found</h1><p>Please use the menu to find the page you need.</p></section>')

(OUT / "english.html").write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0; url=en/index.html"><link rel="canonical" href="en/index.html"><title>Kenta Watanabe | Research</title></head><body><p>The English site has moved to <a href="en/index.html">en/index.html</a>.</p></body></html>''', encoding="utf-8")
(OUT / ".nojekyll").touch()
(OUT / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#102e3b"/><text x="8" y="44" fill="#92dbd1" font-family="Georgia,serif" font-size="38" letter-spacing="-4">kw.</text></svg>', encoding="utf-8")
print(f"Built 6 Japanese and 7 English pages with {len(papers)} papers.")