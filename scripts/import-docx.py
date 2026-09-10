"""One-time import of local references. Requires python-docx; never publishes originals."""
from pathlib import Path
import json
import re
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
paragraphs = [p.text.strip() for p in Document(ROOT / '業績リスト.docx').paragraphs if p.text.strip()]

def section(start, end):
    return paragraphs[paragraphs.index(start) + 1:paragraphs.index(end)]

def records(lines):
    result = []
    for line in lines:
        if re.match(r'^[･・]', line) or line.startswith('野田琢磨,'):
            result.append([re.sub(r'^[･・]\s*', '', line)])
        elif result:
            result[-1].append(line)
    return result

papers = []
for lines in records(section('査読付原著論文', '総説・解説')):
    authors, title, *tail = lines
    citation = ' '.join(tail)
    year = re.search(r'20\d{2}', citation).group()
    award = citation[citation.index('(selected'):].strip() if '(selected' in citation else ''
    citation = re.sub(r'\s*IF\s*=\s*(?:[\d.]+|N/A)', '', citation.split('(selected')[0]).strip()
    papers.append(dict(authors=authors.rstrip(' ,'), title=title.strip('“” "'), citation=citation, year=year, note=award, url=''))

data = {
    'updated': '2026-09-10',
    'papers': papers,
    'books': records(section('著書', '国際会議プロシーディングス')),
    'patents': records(section('特許', '＜受賞＞')),
    'awards': records(section('＜受賞＞', '＜資金＞')),
    'invited': records(section('招待講演', '国際学会')),
    'international': records(section('国際学会', '国内学会')),
    'domestic': records(section('国内学会', '＜担当授業＞')),
}
# Invited talks also occur in the international section of the reference.
data['international'] = [r for r in data['international'] if '(Featured Speaker)' not in r[0] and '(Keynote)' not in r[0]]
(ROOT / 'content' / 'achievements.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print({k: len(v) for k, v in data.items() if isinstance(v, list)})
