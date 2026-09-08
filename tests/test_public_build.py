"""Validate the published artifact, not just the authoring pages."""
import importlib.util
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build-site.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class PublicBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build.build()

    def test_css_foundation_subset_and_minification(self):
        for route in build.PAGES.values():
            page = (build.OUT / route.strip('/') / 'index.html').read_text()
            # CSS is inlined (no render-blocking stylesheet links); the subset ships in it.
            self.assertNotIn('rel="stylesheet"', page)
            self.assertIn('<style>', page)
            self.assertIn('.grid-container', page)
            self.assertNotIn('vendor/foundation.min.css', page)
        subset = (build.OUT / 'assets/css/foundation-subset.css').read_text()
        self.assertIn('.grid-container', subset)
        self.assertIn('.button{', subset)
        for dropped in ['.reveal', '.dropdown', '.accordion', '.small-6', '.grid-margin']:
            self.assertNotIn(dropped, subset)
        for name in ['design', 'resources']:
            built = (build.OUT / f'assets/css/{name}.css').read_text()
            self.assertNotIn('/*', built)
            self.assertLess(len(built), len((build.ROOT / f'assets/css/{name}.css').read_text()))

    def test_routes_metadata_and_internal_targets(self):
        for route in build.PAGES.values():
            page = (build.OUT / route.strip('/') / 'index.html').read_text()
            self.assertEqual(page.count('rel="canonical"'), 1)
            self.assertNotIn('fonts.googleapis.com', page)
            self.assertIn('href="/assets/fonts/newsreader-normal.woff2"', page)
            self.assertIn('/assets/fonts/public-sans-normal.woff2', page)  # inlined @font-face url
            self.assertIn(f'href="{build.BASE}{route}"', page)
            self.assertEqual(page.count('src="/assets/js/analytics.js?v='), 1)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page)[1])
            self.assertEqual(schema['@graph'][2]['url'], build.BASE + route)
            nav = re.search(r'<nav\b.*?</nav>', page, re.S)[0]
            self.assertEqual(nav.count("News &amp; Updates"), 1)
            self.assertNotRegex(nav, r'>\s*Updates\s*<')
            self.assertIn('href="/news/"', nav)
            for target in re.findall(r'(?<![\w-])(?:href|src)="([^"]+)"', page):
                url = urlsplit(target)
                if not url.path.startswith('/') or url.netloc:
                    continue
                dest = build.OUT / url.path.lstrip('/')
                if dest.is_dir():
                    dest /= 'index.html'
                self.assertTrue(dest.is_file(), target)
                if url.fragment and dest.suffix == '.html':
                    self.assertIn(f'id="{url.fragment}"', dest.read_text())

    def test_page_images_and_breadcrumbs(self):
        images = set()
        for source, route in build.PAGES.items():
            page = (build.OUT / route.strip('/') / 'index.html').read_text()
            self.assertIn('name="robots" content="max-image-preview:large"', page)
            image = re.search(r'property="og:image" content="([^"]+)"', page)[1]
            self.assertNotIn(image, images)
            images.add(image)
            self.assertTrue(image.startswith(build.BASE + '/assets/'))
            self.assertTrue((build.OUT / urlsplit(image).path.lstrip('/')).is_file())
            width = int(re.search(r'property="og:image:width" content="(\d+)"', page)[1])
            height = int(re.search(r'property="og:image:height" content="(\d+)"', page)[1])
            self.assertGreaterEqual(width, 1200)
            self.assertGreater(width, height)
            graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page)[1])['@graph']
            self.assertEqual(graph[2]['primaryImageOfPage']['url'], image)
            crumbs = [node for node in graph if node['@type'] == 'BreadcrumbList']
            self.assertEqual(len(crumbs), int(route != '/'))
            if crumbs:
                self.assertEqual(crumbs[0]['itemListElement'], [
                    {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': build.BASE + '/'},
                    {'@type': 'ListItem', 'position': 2, 'name': build.BREADCRUMB_NAMES[source], 'item': build.BASE + route}])

    def graph(self, page):
        return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page)[1])['@graph']

    def test_freshness_dates_and_news_feed(self):
        from datetime import datetime
        for route in build.PAGES.values():
            webpage = self.graph((build.OUT / route.strip('/') / 'index.html').read_text())[2]
            for key in ('datePublished', 'dateModified'):
                datetime.fromisoformat(webpage[key])  # raises if not a valid ISO date
        ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        urls = list(ET.parse(build.OUT / 'sitemap.xml').iter(ns + 'url'))
        self.assertEqual(len(urls), len(build.PAGES))
        for url in urls:
            self.assertRegex(url.find(ns + 'lastmod').text, r'^\d{4}-\d{2}-\d{2}$')
        stories = json.loads((build.ROOT / 'assets/data/news.json').read_text())
        feed = ET.parse(build.OUT / 'feed.xml').getroot()
        self.assertEqual(len(feed.findall('./channel/item')), len(stories))
        self.assertIn('application/rss+xml', (build.OUT / 'news/index.html').read_text())

    def test_entity_grounding(self):
        graph = self.graph((build.OUT / 'index.html').read_text())
        org = graph[0]
        self.assertEqual(org['@type'], 'Organization')
        self.assertTrue(any('Pennsylvania' in area['name'] for area in org['areaServed']))
        self.assertTrue(org.get('knowsAbout') and org.get('description'))
        about = {entity['name']: entity['sameAs'] for entity in graph[2]['about']}
        self.assertIn('Pennsylvania', about)
        self.assertIn('Data center', about)
        for target in about.values():
            self.assertTrue(target.startswith('https://en.wikipedia.org/'))
        news_page = self.graph((build.OUT / 'news/index.html').read_text())[2]
        self.assertEqual(news_page['mainEntity']['@type'], 'ItemList')
        self.assertTrue(news_page['mainEntity']['itemListElement'])

    def test_custom_404(self):
        page = (build.OUT / '404.html').read_text()
        self.assertIn('content="noindex"', page)
        self.assertIn('class="site-header', page)
        self.assertIn('notfound-hero', page)
        self.assertNotIn('rel="stylesheet"', page)  # CSS inlined here too
        self.assertIn('<style>', page)
        self.assertNotIn('href="assets/', page)
        self.assertNotIn('src="./assets', page)
        # the 404 hero reuses the interior-page treatment (serif heading, forest background)
        site_css = (build.OUT / 'assets/css/site.css').read_text()
        self.assertIn('.notfound-hero', site_css)
        self.assertIn('Newsreader', site_css)
        self.assertIn('forest-dark.webp', site_css)

    def test_sitemap_and_redirects(self):
        locs = [n.text for n in ET.parse(build.OUT / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertEqual(set(locs), {build.BASE + p for p in build.PAGES.values()})
        for source, route in build.PAGES.items():
            if source != 'index.html':
                stub = (build.OUT / source).read_text()
                self.assertIn('location.search + location.hash', stub)
                self.assertIn(f'content="0;url={route}"', stub)
        self.assertIn(build.BASE + '/sitemap.xml', (build.OUT / 'robots.txt').read_text())

    def test_resources_and_agent_guide(self):
        guide = (build.OUT / 'llms.txt').read_text()
        self.assertTrue(guide.startswith('# Protect Our Poconos\n'))
        for route in build.PAGES.values():
            self.assertIn('(' + build.BASE + route + ')', guide)
        page = (build.OUT / 'resources/index.html').read_text()
        for marker in ['{{', '<sc-for', '<sc-if', 'support.js', 'doc-page.js']:
            self.assertNotIn(marker, page)
        self.assertEqual(page.count('<details '), 3)
        self.assertIn('Tip submissions are not available yet', page)
        self.assertIn('id="glossary"', page)

    def test_faq_schema_and_navigation(self):
        page = (build.OUT / 'faq/index.html').read_text()
        graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page)[1])['@graph']
        faq = graph[2]
        self.assertEqual(faq['@type'], 'FAQPage')
        self.assertEqual(len(faq['mainEntity']), 26)
        self.assertEqual(page.count('<details '), 25)
        # No em-dashes in the visible copy (ignore the inlined <style>, whose Foundation
        # base includes a cite:before em-dash that never renders without a <cite>).
        self.assertNotIn('—', re.sub(r'<style>.*?</style>', '', page, flags=re.S))
        for question in faq['mainEntity']:
            self.assertTrue(question['acceptedAnswer']['text'])
        for route in build.PAGES.values():
            html = (build.OUT / route.strip('/') / 'index.html').read_text()
            self.assertIn('href="/faq/"', html)
            self.assertRegex(html, r'class="top-style-11[^"]*" href="/take-action/"')
        issues = (build.OUT / 'issues/index.html').read_text()
        self.assertNotIn('class="issue-design-3"', issues)
        self.assertIn('BreadcrumbList', issues)
