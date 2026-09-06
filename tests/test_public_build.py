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

    def test_routes_metadata_and_internal_targets(self):
        for route in build.PAGES.values():
            page = (build.OUT / route.strip('/') / 'index.html').read_text()
            self.assertEqual(page.count('rel="canonical"'), 1)
            self.assertIn(f'href="{build.BASE}{route}"', page)
            self.assertEqual(page.count('src="/assets/js/analytics.js?v='), 1)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page)[1])
            self.assertEqual(schema['@graph'][2]['url'], build.BASE + route)
            nav = re.search(r'<nav\b.*?</nav>', page, re.S)[0]
            self.assertEqual(nav.count("What's Happening"), 1)
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

    def test_sitemap_and_redirects(self):
        locs = [n.text for n in ET.parse(build.OUT / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertEqual(set(locs), {build.BASE + p for p in build.PAGES.values()})
        for source, route in build.PAGES.items():
            if source != 'index.html':
                stub = (build.OUT / source).read_text()
                self.assertIn('location.search + location.hash', stub)
                self.assertIn(f'content="0;url={route}"', stub)
        self.assertIn(build.BASE + '/sitemap.xml', (build.OUT / 'robots.txt').read_text())
