"""Build clean public routes, metadata, redirects, sitemap and news feed. No dependencies."""
import html
import importlib.util
import hashlib
import json
import re
import shutil
import subprocess
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://protectourpoconos.com'
BUILD_DATE = date.today().isoformat()

# Entities that ground the site's topic and geography for search and answer engines;
# sameAs resolves each to Wikipedia (and thence Wikidata). Reused across pages so the
# "Poconos means Pennsylvania" relationship is stated explicitly rather than inferred.
DATA_CENTER = {'@type': 'Thing', 'name': 'Data center', 'sameAs': 'https://en.wikipedia.org/wiki/Data_center'}
POCONOS = {'@type': 'Place', 'name': 'Pocono Mountains', 'sameAs': 'https://en.wikipedia.org/wiki/Pocono_Mountains'}
PIKE = {'@type': 'AdministrativeArea', 'name': 'Pike County, Pennsylvania', 'sameAs': 'https://en.wikipedia.org/wiki/Pike_County,_Pennsylvania'}
MONROE = {'@type': 'AdministrativeArea', 'name': 'Monroe County, Pennsylvania', 'sameAs': 'https://en.wikipedia.org/wiki/Monroe_County,_Pennsylvania'}
PENNSYLVANIA = {'@type': 'State', 'name': 'Pennsylvania', 'sameAs': 'https://en.wikipedia.org/wiki/Pennsylvania'}
ABOUT_ENTITIES = [DATA_CENTER, POCONOS, PIKE, MONROE, PENNSYLVANIA]
ORGANIZATION = {
    '@type': 'Organization', '@id': BASE + '/#organization', 'name': 'Protect Our Poconos',
    'url': BASE + '/', 'logo': BASE + '/assets/logo.svg',
    'description': 'Community information about data-center proposals, transmission projects, '
                   'and land-use decisions in the Pocono region of Pennsylvania, focused on '
                   'Pike and Monroe counties.',
    'areaServed': [PIKE, MONROE, POCONOS],
    'knowsAbout': [DATA_CENTER,
                   {'@type': 'Thing', 'name': 'Land-use planning', 'sameAs': 'https://en.wikipedia.org/wiki/Land-use_planning'},
                   {'@type': 'Thing', 'name': 'Electric power transmission', 'sameAs': 'https://en.wikipedia.org/wiki/Electric_power_transmission'}],
}
PAGES = {'index.html': '/', 'news.html': '/news/', 'projects.html': '/projects/',
         'faq.html': '/faq/', 'resources.html': '/resources/', 'issues.html': '/issues/',
         'take-action.html': '/take-action/', 'about.html': '/about/'}
# Existing landscape artwork, unique to each page; dimensions are native pixels.
PAGE_IMAGES = {
    'index.html': ('hero-waterfall.webp', 1672, 941, 'Waterfall surrounded by forest in the Poconos'),
    'news.html': ('misty-mountains.webp', 2172, 724, 'Misty mountain ridges and forests in the Pocono region'),
    'projects.html': ('issue-community.webp', 1672, 941, 'Illustration of the Pocono landscape and community character'),
    'issues.html': ('forest-dark.webp', 1916, 821, 'Forested Pocono mountains'),
    'resources.html': ('resources-hero.webp', 2172, 724, 'Pocono landscape accompanying community research resources'),
    'faq.html': ('faq-hero.webp', 1916, 821, 'Sunset over forested Pocono mountain ridges'),
    'take-action.html': ('take-action-hero.webp', 1916, 821, 'Pocono scenery accompanying community participation information'),
    'about.html': ('mountains-sunset.webp', 2172, 724, 'Sunset over the Pocono mountains'),
}
BREADCRUMB_NAMES = {'news.html': "News & Updates", 'projects.html': 'Local Projects',
                    'issues.html': 'The Risks', 'resources.html': 'Resources',
                    'faq.html': 'FAQ', 'take-action.html': 'Take Action', 'about.html': 'About'}
OUT = ROOT / '_site'


def minify_css(text):
    """Conservatively minify CSS: drop comments and collapse whitespace, leaving
    string literals and combinators intact so values like calc() are unchanged."""
    # Strip comments before protecting strings, so a quote inside a comment (e.g. "site's")
    # can't swallow the closing */ and leave the comment behind.
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    literals = []
    text = re.sub(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
                  lambda m: literals.append(m[0]) or f'\x00{len(literals) - 1}\x00', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*([{};,])\s*', r'\1', text)
    text = re.sub(r';\}', '}', text).strip()
    return re.sub(r'\x00(\d+)\x00', lambda m: literals[int(m[1])], text)


STYLESHEET = re.compile(r'[ \t]*<link\b[^>]*rel="stylesheet"[^>]*>\n?')


def inline_stylesheets(page):
    """Replace the render-blocking <link rel="stylesheet"> tags with one inline <style>.
    The page then paints without waiting on separate CSS requests. Relative url(../…)
    references are made absolute so they still resolve from the inlined position."""
    links = list(STYLESHEET.finditer(page))
    if not links:
        return page
    css = ''
    for link in links:
        href = re.search(r'href="([^"]+)"', link[0])[1]
        source = minify_css((ROOT / href.lstrip('/')).read_text())
        css += re.sub(r"url\((['\"]?)\.\./", r'url(\1/assets/', source)
    page = page[:links[0].start()] + '<style>' + css + '</style>\n' + page[links[0].end():]
    return STYLESHEET.sub('', page)


def rewrite(match):
    attribute, value = match.groups()
    url = urlsplit(html.unescape(value))
    if url.scheme or url.netloc or not url.path or url.path.startswith('/'):
        return match[0]
    path = url.path.removeprefix('./')
    path = PAGES.get(path, '/' + path)
    query = url.query
    asset = ROOT / path.lstrip('/')
    if path.startswith('/assets/') and asset.suffix in {'.css', '.js'} and asset.is_file():
        version = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        query = (query + '&' if query else '') + 'v=' + version
    return f'{attribute}="{html.escape(path + ("?" + query if query else "") + ("#" + url.fragment if url.fragment else ""), quote=True)}"'


def page_dates(source):
    """(datePublished, dateModified) for a page, from git history. Needs full history
    (the deploy checkout uses fetch-depth: 0); falls back to the build date otherwise."""
    def git(*args):
        try:
            result = subprocess.run(['git', 'log', *args, '--', source], cwd=ROOT,
                                    capture_output=True, text=True, check=True)
            return result.stdout.split()
        except (subprocess.SubprocessError, OSError):
            return []
    modified = git('-1', '--format=%cI')
    published = git('--diff-filter=A', '--format=%cI')
    latest = modified[0] if modified else BUILD_DATE
    return (published[-1] if published else latest), latest


def build_feed():
    """RSS 2.0 feed of the curated news items, for readers and freshness discovery."""
    items = json.loads((ROOT / 'assets/data/news.json').read_text())
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = 'Protect Our Poconos — News & Updates'
    ET.SubElement(channel, 'link').text = BASE + '/news/'
    ET.SubElement(channel, 'description').text = 'Curated reporting and updates on data-center proposals and land-use decisions in the Pocono region of Pennsylvania.'
    ET.SubElement(channel, 'language').text = 'en-US'
    for item in items:
        entry = ET.SubElement(channel, 'item')
        ET.SubElement(entry, 'title').text = item['title']
        ET.SubElement(entry, 'link').text = item['url']
        ET.SubElement(entry, 'description').text = item['summary']
        ET.SubElement(entry, 'source', url=BASE + '/news/').text = item['source']
        published = datetime.fromisoformat(item['date']).replace(tzinfo=timezone.utc)
        ET.SubElement(entry, 'pubDate').text = format_datetime(published)
        ET.SubElement(entry, 'guid', isPermaLink='true').text = item['url']
    ET.indent(rss)
    ET.ElementTree(rss).write(OUT / 'feed.xml', encoding='utf-8', xml_declaration=True)


def build():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
    # Every page inlines its stylesheets (see inline_stylesheets), so the copied CSS files
    # and the full Foundation build are unreferenced in the output; drop them.
    shutil.rmtree(OUT / 'assets/css')
    (OUT / 'assets/vendor/foundation.min.css').unlink()
    (OUT / '.nojekyll').touch()
    shutil.copy2(ROOT / 'llms.txt', OUT / 'llms.txt')
    (OUT / 'CNAME').write_text('protectourpoconos.com\n')
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for source, route in PAGES.items():
        page = (ROOT / source).read_text()
        title = html.unescape(re.search(r'<title>\s*(.*?)\s*</title>', page, re.S)[1])
        description = html.unescape(re.search(r'<meta content="([^"]*)" name="description"', page)[1])
        canonical = BASE + route
        image_file, image_width, image_height, image_alt = PAGE_IMAGES[source]
        image_url = BASE + '/assets/' + image_file
        published, modified = page_dates(source)
        schema = {'@context': 'https://schema.org', '@graph': [
            ORGANIZATION,
            {'@type': 'WebSite', '@id': BASE + '/#website', 'name': 'Protect Our Poconos', 'url': BASE + '/', 'publisher': {'@id': BASE + '/#organization'}, 'inLanguage': 'en-US'},
            {'@type': {'news.html': 'CollectionPage', 'projects.html': 'CollectionPage', 'resources.html': 'CollectionPage', 'about.html': 'AboutPage'}.get(source, 'WebPage'), '@id': canonical + '#webpage', 'url': canonical, 'name': title, 'description': description, 'isPartOf': {'@id': BASE + '/#website'}, 'inLanguage': 'en-US', 'datePublished': published, 'dateModified': modified, 'about': ABOUT_ENTITIES}]}
        schema['@graph'][2]['primaryImageOfPage'] = {
            '@type': 'ImageObject', '@id': canonical + '#primaryimage',
            'url': image_url, 'contentUrl': image_url, 'width': image_width,
            'height': image_height, 'caption': image_alt}
        if source == 'about.html':
            # The About page is about the organization itself.
            schema['@graph'][2]['mainEntity'] = {'@id': BASE + '/#organization'}
        if source == 'news.html':
            stories = json.loads((ROOT / 'assets/data/news.json').read_text())
            schema['@graph'][2]['mainEntity'] = {'@type': 'ItemList', 'itemListElement': [
                {'@type': 'ListItem', 'position': position, 'url': story['url'], 'name': story['title']}
                for position, story in enumerate(stories, 1)]}
        if source == 'faq.html':
            spec = importlib.util.spec_from_file_location('content', ROOT / 'scripts/sync-projects.py')
            content = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(content)
            doc = content.Document(page)
            questions = []
            for node in doc.root.descendants():
                if node.has_class('faq-item'):
                    questions.append({'@type': 'Question', 'name': node.first(tag='summary').text(),
                        'acceptedAnswer': {'@type': 'Answer', 'text': node.first(cls='faq-ans').text()}})
                elif 'data-faq-stance' in node.attrs:
                    paragraphs = [n.text() for n in node.descendants() if n.tag == 'p'][1:]
                    questions.append({'@type': 'Question', 'name': node.first(tag='h2').text(),
                        'acceptedAnswer': {'@type': 'Answer', 'text': ' '.join(paragraphs)}})
            schema['@graph'][2].update({'@type': 'FAQPage', 'mainEntity': questions})
        if route != '/':
            schema['@graph'][-1]['breadcrumb'] = {'@id': canonical + '#breadcrumb'}
            schema['@graph'].append({'@type': 'BreadcrumbList', '@id': canonical + '#breadcrumb', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': BASE + '/'},
                {'@type': 'ListItem', 'position': 2, 'name': BREADCRUMB_NAMES[source], 'item': canonical}]})
        metadata = f'<link rel="canonical" href="{canonical}"/>\n'
        metadata += '<meta name="robots" content="max-image-preview:large"/>\n'
        for prop, value in {'og:type': 'website', 'og:site_name': 'Protect Our Poconos', 'og:title': title, 'og:description': description, 'og:url': canonical, 'og:image': image_url, 'og:image:alt': image_alt, 'og:image:width': str(image_width), 'og:image:height': str(image_height), 'og:image:type': 'image/webp'}.items():
            metadata += f'<meta property="{prop}" content="{html.escape(value, quote=True)}"/>\n'
        metadata += '<meta name="twitter:card" content="summary_large_image"/>\n'
        for name, value in {'twitter:title': title, 'twitter:description': description, 'twitter:image': image_url, 'twitter:image:alt': image_alt}.items():
            metadata += f'<meta name="{name}" content="{html.escape(value, quote=True)}"/>\n'
        if source == 'index.html':
            # Preload the hero (the LCP image), matching the responsive background so
            # phones fetch only the smaller variant instead of both.
            metadata += '<link rel="preload" as="image" href="/assets/hero-waterfall.webp" media="(min-width:801px)" fetchpriority="high"/>\n'
            metadata += '<link rel="preload" as="image" href="/assets/hero-waterfall-mobile.webp" media="(max-width:800px)" fetchpriority="high"/>\n'
        if source in ('index.html', 'news.html'):
            metadata += '<link rel="alternate" type="application/rss+xml" title="Protect Our Poconos — News &amp; Updates" href="/feed.xml"/>\n'
        metadata += '<script type="application/ld+json">' + json.dumps(schema).replace('<', '\\u003c') + '</script>\n'
        page = inline_stylesheets(page)
        page = re.sub(r'(?<![\w-])(href|src)="([^"]*)"', rewrite, page)
        page = page.replace('</head>', metadata + '</head>')
        dest = OUT / route.strip('/') / 'index.html' if route != '/' else OUT / 'index.html'
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(page)
        url_node = ET.SubElement(sitemap, 'url')
        ET.SubElement(url_node, 'loc').text = canonical
        ET.SubElement(url_node, 'lastmod').text = modified[:10]
        if source != 'index.html':
            # GitHub Pages has no custom HTTP redirect rules. Instant meta refresh
            # plus JS preserves existing filter queries and section anchors.
            (OUT / source).write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Page moved</title><link rel="canonical" href="{canonical}"><meta http-equiv="refresh" content="0;url={route}"><script>location.replace({json.dumps(route)} + location.search + location.hash);</script></head><body><a href="{route}">Continue to the page</a></body></html>')
    ET.indent(sitemap)
    ET.ElementTree(sitemap).write(OUT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: ' + BASE + '/sitemap.xml\n')
    build_feed()
    notfound = ROOT / '404.html'
    if notfound.exists():
        # GitHub Pages serves /404.html for any unknown path, so its links must be
        # absolute; the shared rewrite makes them so. Keep it out of the index and sitemap.
        page = re.sub(r'(?<![\w-])(href|src)="([^"]*)"', rewrite, inline_stylesheets(notfound.read_text()))
        page = page.replace('</head>', '<meta name="robots" content="noindex"/>\n</head>')
        (OUT / '404.html').write_text(page)
    print('Built canonical pages, legacy redirects, robots.txt, sitemap.xml, feed.xml and 404 in _site/')


if __name__ == '__main__':
    build()
