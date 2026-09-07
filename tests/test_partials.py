"""The shared header/footer partials must stay rendered into every page."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('render_partials', ROOT / 'scripts/render-partials.py')
partials = importlib.util.module_from_spec(spec)
spec.loader.exec_module(partials)


class PartialsTests(unittest.TestCase):
    def test_pages_match_rendered_partials(self):
        stale = []
        for filename, (home_href, active) in partials.PAGES.items():
            source = (ROOT / filename).read_text()
            if source != partials.assemble(source, home_href, active):
                stale.append(filename)
        self.assertEqual(stale, [], 'Run python3 scripts/render-partials.py and commit the results.')

    def test_active_navigation_and_home_target_per_page(self):
        for filename, (home_href, active) in partials.PAGES.items():
            page = (ROOT / filename).read_text()
            self.assertIn(f'class="top-style-4" href="{home_href}"', page, filename)
            self.assertEqual(page.count('aria-current="page"'), 1 if active else 0, filename)
            if active:
                self.assertIn(f'href="{active}.html" aria-current="page"', page, filename)

    def test_rendering_is_idempotent(self):
        for filename, (home_href, active) in partials.PAGES.items():
            once = partials.assemble((ROOT / filename).read_text(), home_href, active)
            self.assertEqual(once, partials.assemble(once, home_href, active), filename)


if __name__ == '__main__':
    unittest.main()
