"""Check local page links and anchors without adding a browser dependency."""
import importlib.util
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('project_sync', ROOT / 'scripts/sync-projects.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)
PAGES = ['index.html', 'projects.html', 'news.html', 'issues.html']

class SiteLinksTests(unittest.TestCase):
    def test_local_links_and_assets(self):
        docs = {name: list(sync.Document((ROOT / name).read_text()).root.descendants()) for name in PAGES}
        for name, nodes in docs.items():
            ids = [n.attrs['id'] for n in nodes if 'id' in n.attrs]
            self.assertEqual(len(ids), len(set(ids)), name + ': duplicate IDs')
            for node in nodes:
                if node.tag == 'img':
                    self.assertTrue((ROOT / node.attrs['src']).is_file(), node.attrs['src'])
                if node.tag != 'a' or 'href' not in node.attrs or 'data-share' in node.attrs:
                    continue
                url = urlsplit(node.attrs['href'])
                if url.scheme or url.netloc:
                    continue
                target = unquote(url.path) or name
                self.assertTrue((ROOT / target).is_file(), name + ': ' + target)
                if url.fragment and target in docs:
                    self.assertTrue(any(n.attrs.get('id') == url.fragment for n in docs[target]), name + ': ' + node.attrs['href'])

    def test_home_issue_cards_link_to_all_six_sections(self):
        nodes = sync.Document((ROOT / 'index.html').read_text()).root.descendants()
        targets = {n.attrs['href'] for n in nodes if n.has_class('risks-style-84')}
        self.assertEqual(targets, {'issues.html#i-' + topic for topic in ['forests','water','power','noise','community','jobs']})
