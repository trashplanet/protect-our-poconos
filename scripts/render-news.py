"""Regenerate News and homepage news cards from assets/data/news.json."""
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
    for source in item.get('supportingSources', []):
        assert source['url'].startswith('https://'), 'Supporting links must use HTTPS'

def e(value):
    return escape(str(value), quote=True)

def external(item, label):
    return f'<a href="{e(item["url"])}" target="_blank" rel="noopener noreferrer">{e(label)} <span aria-hidden="true">↗</span><span class="show-for-sr"> (opens in a new tab)</span></a>'

def display_date(item):
    d = date.fromisoformat(item['date'])
    return f'{d:%b} {d.day}, {d.year}'

def meta(item):
    return f'<p class="story-meta"><time datetime="{e(item["date"])}">{display_date(item)}</time> · {e(item["source"])}</p>'

def home_card(item):
    title = e(item['title'])
    topic = next(iter(item['categories']), item['source'])
    return (
        f'<a aria-label="{title} (opens in a new tab)" class="news-card home-news-row" '
        f'href="{e(item["url"])}" rel="noopener noreferrer" target="_blank">'
        '<div class="home-news-row-body">'
        f'<div class="home-news-date"><time datetime="{e(item["date"])}">{display_date(item).upper()}</time>'
        f' · {e(topic.upper())}</div>'
        f'<h3 class="home-news-title">{title}</h3>'
        '<span class="home-news-link">Read more <span aria-hidden="true">↗</span></span>'
        '</div></a>'
    )

def replace_section(text, name, content):
    pattern = rf'(<!-- {name}:START -->).*?(<!-- {name}:END -->)'
    text, count = re.subn(pattern, lambda m: m[1]+'\n'+content+'\n'+m[2], text, flags=re.S)
    assert count == 1, f'Missing or duplicate {name} markers'
    return text

def card(item, featured=False):
    classes = 'story-card featured-story' if featured else 'story-card'
    attrs = '' if featured else f' data-topics="{e(json.dumps(item["categories"]))}" data-type="{e(item["type"])}"'
    label = 'Community report · Unverified' if item['type'] == 'Community Report' else item['type']
    note = f'<p class="context-note">{e(item["contextNote"])}</p>' if item['contextNote'] else ''
    project = f'<a class="project-reference" href="projects.html#{e(item["relatedProject"])}">Current project record →</a>' if item['relatedProject'] else ''
    supporting = ''.join(external(source, source['label']) for source in item.get('supportingSources', []))
    tags = ''.join(f'<span>{e(t)}</span>' for t in item['categories'][:3])
    return f'<article class="{classes}"{attrs}><span class="story-type">{e(label)}</span>{meta(item)}<h3>{external(item,item["title"])}</h3><p class="story-summary">{e(item["summary"])}</p>{note}<div class="story-tags">{tags}</div><div class="story-links">{external(item,"Read at source")}{supporting}{project}</div></article>'

newest_first = sorted(items, key=lambda i: i['date'], reverse=True)
latest = newest_first[:3]
sections = {
    'FEATURED': '\n'.join(card(i, True) for i in latest),
    'COVERAGE': '\n'.join(card(i) for i in newest_first),
    'TOPICS': ''.join(f'<option>{e(t)}</option>' for t in sorted({t for i in items for t in i['categories']})),
    'TYPES': ''.join(f'<option>{e(t)}</option>' for t in sorted({i['type'] for i in items})),
    'SERIES': '\n'.join(f'<article><span class="series-number">0{n}</span><p class="eyebrow">{e(i["seriesPart"])}</p><h3>{external(i, i["seriesPart"])}</h3><p>{e(i["summary"])}</p>{external(i,"Read part "+str(n))}</article>' for n,i in enumerate([i for i in items if i.get('series')],1)),
    'ELSEWHERE': meta(items[-1])+f'<p>{e(items[-1]["summary"])}</p>'+external(items[-1],'Read the feature at The Verge')
}
page = ROOT / 'news.html'
text = page.read_text()
for name, content in sections.items():
    text = replace_section(text, name, content)
text = re.sub(r'Browse all \d+ selected articles', f'Browse all {len(items)} selected articles', text)
text = re.sub(r'\d+ articles · Newest first', f'{len(items)} articles · Newest first', text)
home = ROOT / 'index.html'
home_text = replace_section(home.read_text(), 'HOME_NEWS', '\n'.join(home_card(i) for i in latest))
page.write_text(text)
home.write_text(home_text)
print(f'Rendered {len(items)} articles into news.html and {len(latest)} cards into index.html')
