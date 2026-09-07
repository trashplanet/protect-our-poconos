"""Build clean public routes, metadata, redirects and sitemap. No dependencies."""
import html
import importlib.util
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://protectourpoconos.com'
PAGES = {'index.html': '/', 'news.html': '/news/', 'projects.html': '/projects/',
         'faq.html': '/faq/', 'resources.html': '/resources/', 'issues.html': '/issues/', 'take-action.html': '/take-action/'}
# Existing landscape artwork, unique to each page; dimensions are native pixels.
PAGE_IMAGES = {
    'index.html': ('hero-waterfall.webp', 1672, 941, 'Waterfall surrounded by forest in the Poconos'),
    'news.html': ('misty-mountains.webp', 2172, 724, 'Misty mountain ridges and forests in the Pocono region'),
    'projects.html': ('issue-community.webp', 1672, 941, 'Illustration of the Pocono landscape and community character'),
    'issues.html': ('forest-dark.webp', 1916, 821, 'Forested Pocono mountains'),
    'resources.html': ('resources-hero.webp', 2172, 724, 'Pocono landscape accompanying community research resources'),
    'faq.html': ('faq-hero.webp', 1916, 821, 'Sunset over forested Pocono mountain ridges'),
    'take-action.html': ('take-action-hero.webp', 1916, 821, 'Pocono scenery accompanying community participation information'),
}
BREADCRUMB_NAMES = {'news.html': "News & Updates", 'projects.html': 'Local Projects',
                    'issues.html': 'The Risks', 'resources.html': 'Resources',
                    'faq.html': 'FAQ', 'take-action.html': 'Take Action'}
OUT = ROOT / '_site'


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


def build():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
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
        schema = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'Organization', '@id': BASE + '/#organization', 'name': 'Protect Our Poconos', 'url': BASE + '/', 'logo': BASE + '/assets/logo.svg'},
            {'@type': 'WebSite', '@id': BASE + '/#website', 'name': 'Protect Our Poconos', 'url': BASE + '/', 'publisher': {'@id': BASE + '/#organization'}, 'inLanguage': 'en-US'},
            {'@type': 'CollectionPage' if source in ['news.html', 'projects.html', 'resources.html'] else 'WebPage', '@id': canonical + '#webpage', 'url': canonical, 'name': title, 'description': description, 'isPartOf': {'@id': BASE + '/#website'}, 'inLanguage': 'en-US'}]}
        schema['@graph'][2]['primaryImageOfPage'] = {
            '@type': 'ImageObject', '@id': canonical + '#primaryimage',
            'url': image_url, 'contentUrl': image_url, 'width': image_width,
            'height': image_height, 'caption': image_alt}
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
            metadata += '<link rel="preload" as="image" href="/assets/hero-waterfall.webp" fetchpriority="high"/>\n'
        metadata += '<script type="application/ld+json">' + json.dumps(schema).replace('<', '\\u003c') + '</script>\n'
        page = re.sub(r'(?<![\w-])(href|src)="([^"]*)"', rewrite, page)
        page = page.replace('</head>', metadata + '</head>')
        dest = OUT / route.strip('/') / 'index.html' if route != '/' else OUT / 'index.html'
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(page)
        ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = canonical
        if source != 'index.html':
            # GitHub Pages has no custom HTTP redirect rules. Instant meta refresh
            # plus JS preserves existing filter queries and section anchors.
            (OUT / source).write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Page moved</title><link rel="canonical" href="{canonical}"><meta http-equiv="refresh" content="0;url={route}"><script>location.replace({json.dumps(route)} + location.search + location.hash);</script></head><body><a href="{route}">Continue to the page</a></body></html>')
    ET.indent(sitemap)
    ET.ElementTree(sitemap).write(OUT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: ' + BASE + '/sitemap.xml\n')
    print('Built canonical pages, legacy redirects, robots.txt and sitemap.xml in _site/')


if __name__ == '__main__':
    build()
