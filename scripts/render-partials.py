"""Render the shared header, navigation and footer into every page. Standard library only.

The chrome that repeats on all pages lives once in partials/. Edit those files, then run
this script to write the assembled header and footer back into each committed page. Preview
and GitHub Pages keep serving the generated static HTML with no build step at request time.

    python3 scripts/render-partials.py            # update the pages in place
    python3 scripts/render-partials.py --check     # fail if any page is out of sync (CI)

Partials
    partials/site-header.html   site header: logo, mobile menu button, navigation, CTA
    partials/primary-nav.html   the navigation links, shown as the top bar on desktop and,
                                when the menu button is toggled, as the mobile menu drawer
    partials/footer.html        site footer

Only two things vary between pages, so they are the only template variables:
    {{home_href}}   the logo and footer "Home" target ("#top" on the homepage,
                    "index.html#top" elsewhere)
    {{active_*}}    " aria-current=\"page\"" on the current page's navigation link
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
    '404.html': ('index.html#top', None),
}
NAV_KEYS = ['news', 'issues', 'projects', 'resources', 'faq']

# The single site header and footer on each page; leading indentation is matched so the
# rendered block drops in exactly where the original stood.
HEADER = re.compile(r'[ \t]*<header class="site-header.*?</header>', re.S)
FOOTER = re.compile(r'[ \t]*<footer class="layout-style-170".*?</footer>', re.S)


def context(home_href, active):
    values = {'home_href': home_href}
    for key in NAV_KEYS:
        values['active_' + key] = ' aria-current="page"' if active == key else ''
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
    header = render('site-header', values).rstrip('\n')
    footer = render('footer', values).rstrip('\n')
    page, headers = HEADER.subn(lambda _: header, page, count=1)
    page, footers = FOOTER.subn(lambda _: footer, page, count=1)
    if headers != 1 or footers != 1:
        raise ValueError(f'Expected one header and one footer (found {headers} and {footers})')
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
        parser.exit(1, 'Shared header/footer is stale in ' + ', '.join(stale)
                    + '. Run python3 scripts/render-partials.py and commit the results.\n')
    print('Shared header and footer aligned.' if not stale else 'Rendered partials into: ' + ', '.join(stale))


if __name__ == '__main__':
    main()
