"""Regenerate news sections after editing assets/data/news.json. Standard library only."""
import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
items = json.loads((ROOT / 'assets/data/news.json').read_text())
assert len({item['id'] for item in items}) == len(items), 'Story IDs must be unique'
for item in items:
    date.fromisoformat(item['date'])
    assert item['url'].startswith('https://'), 'Source links must use HTTPS'

def e(value):
    return escape(str(value), quote=True)

def external(item, label):
    return f'<a href="{e(item["url"])}" target="_blank" rel="noopener noreferrer">{e(label)} <span aria-hidden="true">↗</span><span class="show-for-sr"> (opens in a new tab)</span></a>'

def meta(item):
    d = date.fromisoformat(item['date'])
    return f'<p class="story-meta"><time datetime="{e(item["date"])}">{d.strftime("%b")} {d.day}, {d.year}</time> · {e(item["source"])}</p>'

def card(item, featured=False):
    classes = 'story-card featured-story' if featured else 'story-card'
    attrs = '' if featured else f' data-topics="{e(json.dumps(item["categories"]))}" data-type="{e(item["type"])}"'
    label = 'Community report · Unverified' if item['type'] == 'Community Report' else item['type']
    note = f'<p class="context-note">{e(item["contextNote"])}</p>' if item['contextNote'] else ''
    project = f'<a class="project-reference" href="projects.html#{e(item["relatedProject"])}">Current project record →</a>' if item['relatedProject'] else ''
    tags = ''.join(f'<span>{e(t)}</span>' for t in item['categories'][:3])
    return f'<article class="{classes}"{attrs}><span class="story-type">{e(label)}</span>{meta(item)}<h3>{external(item,item["title"])}</h3><p class="story-summary">{e(item["summary"])}</p>{note}<div class="story-tags">{tags}</div><div class="story-links">{external(item,"Read at source")}{project}</div></article>'

sections = {
    'FEATURED': '\n'.join(card(i, True) for i in items[:3]),
    'COVERAGE': '\n'.join(card(i) for i in sorted(items, key=lambda i: i['date'], reverse=True)),
    'TOPICS': ''.join(f'<option>{e(t)}</option>' for t in sorted({t for i in items for t in i['categories']})),
    'SERIES': '\n'.join(f'<article><span class="series-number">0{n}</span><p class="eyebrow">{e(i["seriesPart"])}</p><h3>{external(i, i["seriesPart"])}</h3><p>{e(i["summary"])}</p>{external(i,"Read part "+str(n))}</article>' for n,i in enumerate([i for i in items if i.get('series')],1)),
    'ELSEWHERE': meta(items[-1])+f'<p>{e(items[-1]["summary"])}</p>'+external(items[-1],'Read the feature at The Verge')
}
page = ROOT / 'news.html'
text = page.read_text()
for name, content in sections.items():
    pattern = rf'(<!-- {name}:START -->).*?(<!-- {name}:END -->)'
    text, count = re.subn(pattern, lambda m: m[1]+'\n'+content+'\n'+m[2], text, flags=re.S)
    assert count == 1, f'Missing or duplicate {name} markers'
page.write_text(text)
print(f'Rendered {len(items)} articles into news.html')
