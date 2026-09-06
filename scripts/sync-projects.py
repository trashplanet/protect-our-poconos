"""Sync static project references from projects.html; no third-party dependencies.

Run after editing the tracker. --check exits nonzero for stale generated content.
Bindings explicitly mark shared text/links/images; surrounding page design is untouched.
"""
import argparse
from collections import Counter
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())

class Node:
    def __init__(self, tag='', attrs=(), start=0, inner=0):
        self.tag, self.attrs = tag, dict(attrs)
        self.start, self.inner, self.end = start, inner, inner
        self.children = []
        self.parts = []

    def text(self):
        return re.sub(r'\s+', ' ', ''.join(p.text() if isinstance(p, Node) else p for p in self.parts)).strip()

    def has_class(self, name):
        return name in self.attrs.get('class', '').split()

    def descendants(self):
        for child in self.children:
            yield child
            yield from child.descendants()

    def first(self, *, tag=None, cls=None):
        return next(n for n in self.descendants() if (not tag or n.tag == tag) and (not cls or n.has_class(cls)))

class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.lines = [0]
        self.lines.extend(m.end() for m in re.finditer('\n', source))
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.position()
        node = Node(tag, attrs, start, start + len(self.get_starttag_text()))
        self.stack[-1].children.append(node)
        self.stack[-1].parts.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack[-1].tag != tag:
            raise ValueError(f'Unexpected closing tag {tag}; check HTML nesting')
        self.stack.pop().end = self.position()

    def handle_data(self, data):
        self.stack[-1].parts.append(data)


def values_from(tracker):
    values = {}
    cards = [n for n in tracker.root.descendants() if n.has_class('tracker-card')]
    counts = Counter(n.attrs['data-category'] for n in cards)
    counts.update({'all': len(cards), 'watched': counts['watchlist'] + counts['rumors'],
                   'other': len(cards) - counts['data-centers']})
    for category in ['all', 'data-centers', 'infrastructure', 'watchlist', 'rumors', 'watched', 'other']:
        values['counts.' + category] = str(counts[category])
    values['counts.breakdown'] = f"{counts['infrastructure']} transmission projects and {counts['watched']} watchlist / rumor sites"
    policy_grid = tracker.root.first(cls='policy-grid')
    values['counts.policies'] = str(sum(n.tag == 'article' for n in policy_grid.children))
    for card in cards:
        key = card.attrs['id']
        fields = {'title': card.first(tag='h2').text(),
                  'summary': card.first(cls='project-summary').text(),
                  'location': card.first(cls='project-location').text(),
                  'status': ' · '.join(n.text() for n in card.descendants() if n.has_class('status')),
                  'image': card.first(tag='img').attrs['src'],
                  'caption': card.first(cls='tracker-card-image').first(tag='span').text(),
                  'url': 'projects.html#' + key}
        deadline = card.attrs.get('data-deadline')
        if deadline:
            d = date.fromisoformat(deadline)
            fields['deadline-iso'] = deadline
            fields['deadline-month'] = d.strftime('%b').upper()
            fields['deadline-day'] = str(d.day)
            fields['deadline-year'] = str(d.year)
            fields['deadline-label'] = f'{d.strftime("%b").upper()} {d.day}, {d.year}'
        milestone = card.first(cls='project-milestone')
        links = [n for n in milestone.descendants() if n.tag == 'a']
        if links:
            fields['milestone-source'] = links[0].attrs['href']
        values.update({key + '.' + field: value for field, value in fields.items()})
    for node in tracker.root.descendants():
        if 'data-project-source' in node.attrs:
            key = node.attrs['data-project-source']
            if key in values:
                raise ValueError(f'Duplicate project source: {key}')
            values[key] = node.text()
    return values


def synchronize(source, values):
    document = Document(source)
    edits = []
    for node in document.root.descendants():
        if 'data-project-text' in node.attrs:
            value = values[node.attrs['data-project-text']]
            value = node.attrs.get('data-project-format', '{}').format(value)
            # Preserve indentation so running the sync repeatedly produces no changes.
            old = source[node.inner:node.end]
            leading = re.match(r'\s*', old)[0]
            trailing = re.search(r'\s*$', old)[0] if old.strip() else ''
            edits.append((node.inner, node.end, leading + escape(value) + trailing))
        for binding, attr in [('href', 'href'), ('src', 'src'), ('date', 'data-event-date')]:
            key = node.attrs.get('data-project-' + binding)
            if key:
                old = source[node.start:node.inner]
                new, count = re.subn(r'(?<![\w-])' + attr + r'="[^"]*"', lambda _: f'{attr}="{escape(values[key], quote=True)}"', old)
                if count != 1:
                    raise ValueError(f'Missing {attr} on a bound element')
                edits.append((node.start, node.inner, new))
    for start, end, new in sorted(edits, reverse=True):
        source = source[:start] + new + source[end:]
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    values = values_from(Document((ROOT / 'projects.html').read_text()))
    stale = []
    for filename in ['index.html', 'projects.html', 'issues.html', 'take-action.html']:
        path = ROOT / filename
        before = path.read_text()
        after = synchronize(before, values)
        if before != after:
            stale.append(filename)
            if not args.check:
                path.write_text(after)
    if args.check and stale:
        parser.exit(1, 'Project content is stale in ' + ', '.join(stale) + '. Run python3 scripts/sync-projects.py and commit the results.\n')
    print('Project content aligned.' if not stale else 'Synchronized: ' + ', '.join(stale))

if __name__ == '__main__':
    main()
