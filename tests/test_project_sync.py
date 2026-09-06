"""Regression checks for real tracker changes and stale-homepage detection."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/sync-projects.py'
spec = importlib.util.spec_from_file_location('sync_projects', SCRIPT)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

class ProjectSyncTests(unittest.TestCase):
    def setUp(self):
        self.tracker = (ROOT / 'projects.html').read_text()
        self.home = (ROOT / 'index.html').read_text()

    def render(self, tracker):
        return sync.synchronize(self.home, sync.values_from(sync.Document(tracker)))

    def test_title_and_source_escaping(self):
        changed = self.tracker.replace('Smithfield Gateway Data Center', 'Updated &amp; Reviewed Proposal')
        result = self.render(changed)
        self.assertIn('Updated &amp; Reviewed Proposal', result)
        self.assertNotIn('Updated &amp;amp;', result)

    def test_figures_and_date_follow_tracker(self):
        changed = self.tracker.replace('250,000', '275,000').replace('data-deadline="2026-09-09"', 'data-deadline="2026-10-14"')
        result = self.render(changed)
        self.assertIn('275,000 SQ FT', result)
        self.assertIn('275,000 sq ft', result)
        self.assertIn('OCT 14, 2026 · SMITHFIELD', result)
        action = sync.synchronize((ROOT / 'take-action.html').read_text(), sync.values_from(sync.Document(changed)))
        self.assertIn('data-event-date="2026-10-14"', action)
        self.assertNotIn('data-event-date="2026-09-09"', action)

    def test_categories_change_derived_totals(self):
        changed = self.tracker.replace('data-category="rumors"', 'data-category="data-centers"')
        values = sync.values_from(sync.Document(changed))
        self.assertEqual(values['counts.data-centers'], '4')
        self.assertEqual(values['counts.other'], '3')
        self.assertEqual(values['counts.rumors'], '0')
        self.assertEqual(values['counts.all'], '7')

    def test_missing_project_fails(self):
        changed = self.tracker.replace('id="shawnee-walker"', 'id="renamed-project"')
        with self.assertRaises(KeyError):
            self.render(changed)

    def test_check_detects_stale_file_then_sync_repairs_it(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'scripts').mkdir()
            script = root / 'scripts/sync-projects.py'
            script.write_text(SCRIPT.read_text())
            (root / 'projects.html').write_text(self.tracker)
            (root / 'issues.html').write_text((ROOT / 'issues.html').read_text())
            (root / 'take-action.html').write_text((ROOT / 'take-action.html').read_text())
            (root / 'index.html').write_text(self.home.replace('250,000 SQ FT', '999,000 SQ FT'))
            def run(*args):
                return subprocess.run(['python3', str(script), *args], capture_output=True, text=True)
            self.assertEqual(run('--check').returncode, 1)
            self.assertEqual(run().returncode, 0)
            self.assertEqual(run('--check').returncode, 0)
            once = (root / 'index.html').read_text()
            self.assertEqual(run().returncode, 0)
            self.assertEqual((root / 'index.html').read_text(), once)

if __name__ == '__main__':
    unittest.main()
