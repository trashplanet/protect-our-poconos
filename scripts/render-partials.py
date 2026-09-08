"""Render the shared header, navigation and footer into every page. Standard library only.

The chrome that repeats on all pages lives once in partials/. Edit those files, then run
this script to write the assembled header and footer back into each committed page. Preview
and GitHub Pages keep serving the generated static HTML with no build step at request time.

    python3 scripts/render-partials.py            # update the pages in place
    python3 scripts/render-partials.py --check     # fail if any page is out of sync (CI)

Partials
    partials/head.html          document <head>: meta, base CSS/JS links, font preloads
    partials/site-header.html   site header: logo, mobile menu button, navigation, CTA
    partials/primary-nav.html   the navigation links, shown as the top bar on desktop and,
                                when the menu button is toggled, as the mobile menu drawer
    partials/footer.html        site footer
    partials/notice.html        the shared "not ready yet" dialog

Per-page values are read back out of each page (title/description stay authored in the
HTML) or come from the PAGES table:
    {{title}} {{description}}   the page's <title> and meta description, preserved as-is
    {{page_css}} {{page_js}}    the page's own stylesheet/script, if any (e.g. news.css)
    {{home_href}}               the logo and footer "Home" target ("#top" on the homepage,
                                "index.html#top" elsewhere)
    {{active_*}}                " aria-current=\"page\"" on the current page's nav link
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTIALS = ROOT / 'partials'

# filename -> (home_href, active navigation key or None).
PAGES = {
    'index.html': ('#top', None),
    'news.html': ('index.html#top', 'news'),
    'issues.html': ('index.html#top', 'issues'),
    'projects.html': ('index.html#top', 'projects'),
    'resources.html': ('index.html#top', 'resources'),
    'faq.html': ('index.html#top', 'faq'),
    'take-action.html': ('index.html#top', None),
    'about.html': ('index.html#top', None),
    '404.html': ('index.html#top', None),
}
NAV_KEYS = ['news', 'issues', 'projects', 'resources', 'faq']

# Single shared regions on each page; leading indentation is matched so the rendered
# block drops in exactly where the original stood.
HEAD = re.compile(r'[ \t]*<head>.*?</head>', re.S)
HEADER = re.compile(r'[ \t]*<header class="site-header.*?</header>', re.S)
FOOTER = re.compile(r'[ \t]*<footer class="layout-style-170".*?</footer>', re.S)
NOTICE = re.compile(r'[ \t]*<dialog aria-labelledby="notice-title".*?</dialog>', re.S)
BASE_CSS = {'foundation-subset', 'design', 'site', 'layout', 'fonts'}
BASE_JS = {'site', 'analytics'}


def context(home_href, active):
    values = {'home_href': home_href}
    for key in NAV_KEYS:
        values['active_' + key] = ' aria-current="page"' if active == key else ''
    return values


def head_values(page):
    """Read the per-page title, description and any page-specific CSS/JS back out of the
    page, so those stay authored in the HTML while the head structure lives in the partial."""
    values = {
        'title': re.search(r'<title>\s*(.*?)\s*</title>', page, re.S)[1],
        'description': re.search(r'<meta content="([^"]*)" name="description"', page)[1],
        'page_css': '', 'page_js': '',
    }
    for name in re.findall(r'<link href="assets/css/([\w-]+)\.css" rel="stylesheet"', page):
        if name not in BASE_CSS:
            values['page_css'] = f' <link href="assets/css/{name}.css" rel="stylesheet"/>\n'
    for name in re.findall(r'src="assets/js/([\w-]+)\.js"', page):
        if name not in BASE_JS:
            values['page_js'] = f' <script defer src="assets/js/{name}.js"></script>\n'
    return values


def render(name, values):
    text = (PARTIALS / (name + '.html')).read_text()
    text = re.sub(r'\{\{>\s*([\w-]+)\s*\}\}', lambda m: render(m[1], values).rstrip('\n'), text)

    def variable(match):
        key = match[1]
        if key not in values:
            raise KeyError(f'Unknown template variable {{{{{key}}}}} in partials/{name}.html')
        return values[key]

    return re.sub(r'\{\{\s*(\w+)\s*\}\}', variable, text)


def assemble(page, home_href, active):
    values = context(home_href, active)
    head = render('head', head_values(page)).rstrip('\n')
    header = render('site-header', values).rstrip('\n')
    footer = render('footer', values).rstrip('\n')
    notice = render('notice', {}).rstrip('\n')
    page, heads = HEAD.subn(lambda _: head, page, count=1)
    page, headers = HEADER.subn(lambda _: header, page, count=1)
    page, footers = FOOTER.subn(lambda _: footer, page, count=1)
    page, notices = NOTICE.subn(lambda _: notice, page, count=1)
    if not (heads == headers == footers == notices == 1):
        raise ValueError(f'Expected one of each region (head={heads} header={headers} '
                         f'footer={footers} notice={notices})')
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='exit nonzero if any page is out of sync')
    args = parser.parse_args()
    stale = []
    for filename, (home_href, active) in PAGES.items():
        path = ROOT / filename
        before = path.read_text()
        after = assemble(before, home_href, active)
        if before != after:
            stale.append(filename)
            if not args.check:
                path.write_text(after)
    if args.check and stale:
        parser.exit(1, 'Shared page regions are stale in ' + ', '.join(stale)
                    + '. Run python3 scripts/render-partials.py and commit the results.\n')
    print('Shared page regions aligned.' if not stale else 'Rendered partials into: ' + ', '.join(stale))


if __name__ == '__main__':
    main()
