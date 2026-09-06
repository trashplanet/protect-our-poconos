# Protect Our Poconos

Static site based on the supplied **Protect Our Poconos Dark** mockup. Original waterfall, forest, mountain, logo, and scale illustration assets are preserved. Built with HTML, Foundation for Sites 6.9.0 CSS, and a small vanilla JavaScript file. No npm install or build step required.

## Preview

From this directory:

```sh
python3 -m http.server 4173 --bind 127.0.0.1
```

Open http://localhost:4173. Stop with Ctrl+C. In GitHub Desktop, add this folder as a local repository.

## Files

- `index.html`: homepage content and semantic sections.
- `news.html`: curated news, featured stories, sourced dates, WVIA series and an outside case study.
- `assets/data/news.json`: news metadata, summaries, source URLs and visible context notes.
- `scripts/render-news.py`: dependency-free authoring helper that updates the committed static news sections.
- `assets/css/news.css` and `assets/js/news.js`: responsive news layout, topic/type/search filters and progressive browsing.
- `projects.html`: seven project / infrastructure / watchlist entries, category legend, local policy context and source links.
- `assets/css/projects.css`: tracker layouts and responsive card styles.
- `assets/js/projects.js`: category/county filters, sorting, shareable filter URLs and direct project links.
- `assets/css/design.css`: exact dark mockup styling extracted from the export and deduplicated. Section-prefixed selectors map back to HTML.
- `assets/css/site.css`: responsive layouts, mobile navigation, accessibility, and small visual fixes.
- `assets/js/site.js`: menu, accessible dialogs for unfinished destinations, and sharing.
- `assets/vendor/`: local Foundation CSS and its MIT license. Foundation XY grid container/cell classes are used alongside the mockup's custom column ratios.
- `.github/workflows/pages.yml`: automatic GitHub Pages deployment, uploading public files only.

## GitHub Pages

In the GitHub repository, select **Settings → Pages → Build and deployment → Source: GitHub Actions**. When ready, select **Actions → Deploy static site to GitHub Pages → Run workflow**. Pushes to main deploy automatically; manual runs remain available. Relative asset paths work on a project Pages URL or a custom domain.

Docs: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Content still needed

Homepage copy was revised against linked public records on September 5, 2026. Smithfield figures come from the August resubmission, Lehman adoption from the November 20, 2025 minutes, and the September 9 hearing from the township August newsletter. Project/news cards now link to those records. Eagle Village remains explicitly unconfirmed. The old September 18 Pike County meeting date was removed rather than advertised as upcoming.

- Actual project photography: homepage cards reuse the supplied illustration and regional landscapes with clear captions. News cards are text-only and open source links in new tabs.
- Dedicated article/project pages; verified cards currently link directly to public source documents.
- A newsletter signup provider or hosted form URL; no email collection or fake success state is implemented.
- Current meeting calendar, officials directory, public-comment instructions, research library, and social/contact links.
- Privacy text should be updated when services are added. Google Fonts is currently the only external frontend dependency; Foundation and images are local.

Remaining unfinished links open an explanatory dialog. Replace their `href` and remove `data-notice` / `data-notice-title` once the destination exists. The mockup's fake search button was removed. Share opens a not-configured notice until a public sharing destination is provided; it does not share the current preview or GitHub URL.

## Later WordPress migration

Keep these CSS and image files. Split the header/footer into theme templates, move homepage sections to `front-page.php`, enqueue Foundation followed by the two site stylesheets, and replace project/news cards with WordPress loops. No rewrite into another frontend framework is needed.

## Checks

```sh
node --check assets/js/site.js
git diff --check
```

Check the homepage at desktop, tablet, and mobile widths, including mobile menu, keyboard focus, Escape dismissal, image loading, and anchor navigation.

## Maintaining the project tracker

Edit card content directly in `projects.html`; no build step or browser-rendered data feed is required. Each `article.tracker-card` has a stable project `id`, `data-category`, space-separated `data-county`, numeric `data-rank`, and optional ISO `data-deadline`. Update visible card text, stat values, milestone details and source links together. Run `python3 scripts/sync-projects.py` after tracker edits. Homepage project references and homepage/tracker project counts are generated from the tracker cards.

`Most relevant` preserves editorial order, `Next deadline` brings future dated milestones forward, and `Project name` sorts alphabetically. Past deadlines are not silently presented as open actions. Reviewed dates are editorial dates, not automatically changed to today. No background monitoring is implemented.

Source links live in each card's `project-sources` list. Prefer two or three useful links, identifying official/government records, applicant filings, utility statements, reporting and community/opposition material separately. MonroeCountyPA.com is independent media, not a county government website. Historical documents establish history, not current ownership or a data-center application. A township ordinance does not prove a site-specific project.

Project imagery reuses supplied illustrations and landscapes; captions explicitly distinguish them from site photos or project renderings. Replace the image and caption together when actual authorized site photography is available.

`Share a tip` intentionally displays a not-open-yet notice, per the owner's request. Replace its href and remove the two `data-notice` attributes once a real contact destination is provided.

Validated at 1440, 1024, 768, 390 and 320 pixels: no overflow/broken images; category/county combinations; empty/reset states; sorting; URL restoration; project deep links; homepage navigation; mobile menu; tip notice; native details with JavaScript disabled.

## Maintaining news

Edit `assets/data/news.json`, then run `python3 scripts/render-news.py` and commit both the dataset and `news.html`. This is an authoring helper only: preview and GitHub Pages serve the already-generated HTML with no build or runtime data service. Every article remains available without JavaScript.

Keep `title`, `source`, ISO `date`, `type`, `categories`, `relatedProject` (tracker ID or null), `summary`, `contextNote`, and `url` together. Source types are distinct from topics. The first three dataset entries are the featured stories; WVIA entries carry `series` and `seriesPart`. The final entry supplies the elsewhere feature. Update the introductory article total if adding or removing entries. Keep summaries concise and preserve the visible stale-plan, proposed-legislation and unverified-community context notes. Article links open at their publishers in new tabs; access or subscriptions are controlled by those publishers.

Meeting dates and their sources are edited directly in `news.html`. The reviewed date is editorial, not automatically refreshed. Dates that have elapsed are labeled as past using the America/New_York timezone; their outcomes require a source check. Tip submissions remain explicitly unavailable.

News checks: `python3 scripts/render-news.py`, `node --check assets/js/news.js`, and `git diff --check`. Verify filters, empty/reset, six-at-a-time browsing, URL restoration, no-JavaScript access and mobile navigation. Updates navigation and the homepage View all updates button now link to `news.html`.

## Homepage / tracker consistency

`projects.html` is the canonical source for the shared project content. After editing it, run:

```sh
python3 scripts/sync-projects.py
python3 scripts/sync-projects.py --check
python3 -m unittest discover -s tests
```

The dependency-free sync updates explicitly marked homepage project titles, locations, summaries, status labels, image URLs/captions, project links, Lehman policy copy, Smithfield scale figures and the Smithfield hearing date/source. It computes homepage totals and tracker category counts from the actual tracker cards. It preserves static HTML, existing page layouts and no-JavaScript access.

`data-project-source` marks a visible canonical fact in the tracker. `data-project-text`, `data-project-href` and `data-project-src` mark generated references; optional `data-project-format` supplies surrounding text. Edit the source, not a generated reference. Missing sources fail visibly instead of silently retaining stale content. The homepage remains a selected overview, not a second copy of all seven tracker entries.

GitHub runs a consistency check on pushes and pull requests. Manual Pages deployment also runs the sync before staging, so published shared references come from the current tracker. These checks synchronize the reviewed content; they do not discover new filings, verify sources or reassess editorial claims. Homepage issue explanations, historical news headlines and imagery presentation still need editorial review when a proposal fundamentally changes.

## Explore the issues

`issues.html` adapts the supplied Design (15) issues page, using Foundation and shared navigation/dialog behavior. `assets/css/issues.css` contains the scoped export styles and mobile overrides. The six `assets/issue-*.png` images are supplied illustrations, clearly labeled rather than presented as project photography. No export runtime or additional frontend dependency is loaded.

The six stable deep links are `issues.html#i-forests`, `#i-water`, `#i-power`, `#i-noise`, `#i-community` and `#i-jobs`; the health section is `#health`. Each section includes source or related-project/reporting links. Edit explanatory content directly in `issues.html`; shared project figures and marked local-context summaries are populated by `python3 scripts/sync-projects.py`. Pages deployment includes this page and regenerates its bindings.

Homepage concern cards and The Risks / About the Issue / Key Concerns links now open the issues page. What’s Happening and Local Projects open the tracker; Updates opens news. The meeting action links to the news calendar. Destinations without a completed equivalent, including signup, contacts and the full research library, retain their existing behavior. The source review clarifies cooling-system differences and keeps general health evidence separate from site-specific exposure.

Validated at 1440, 1024, 768, 390 and 320 pixels, including images, mobile navigation, deep links and no-JavaScript content. `python3 -m unittest discover -s tests` also checks internal destinations and all six homepage issue links.

The homepage hero event card now highlights the September 9, 2026 Smithfield Gateway conditional-use hearing at 6 PM, J.T. Lambert Intermediate School. Its project title, date and township-notice URL sync from the tracker. The compact copy fits within the original card dimensions.

## Take Action / Your Voice Matters

`take-action.html` adapts Design (16), with the supplied `assets/take-action-hero.png`, scoped `assets/css/action.css`, and shared navigation and dialogs. Sections include current hearings (`#attention`), ways to help (`#help`), public office contacts (`#contacts`), public-comment guidance (`#comment`), and meeting preparation (`#attend`). Homepage actions and Take Action navigation across all pages now lead here.

The Smithfield hearing date and official notice link are generated from the tracker by `python3 scripts/sync-projects.py`, including the date used by `assets/js/action.js` to label past events. The continuation date, venue, participation guidance, office records and editorial review dates remain manually maintained against official sources. Past-date labels do not establish an outcome or reschedule a hearing; update the cards after checking current notices.

Contact links use official government websites, public office email addresses and click-to-call phone links. Signup, sharing and tips remain not configured and open explanatory dialogs. There is no form submission, email sending or data collection. All content and ordinary links remain available without JavaScript.

Verified at 1440, 1024, 768, 390 and 320 pixels, including deep links, active navigation, placeholder dialogs, external targets and past-event labeling with a simulated later date. Static link tests cover all five pages; the sync regression also checks the Take Action event date.


## Public URLs, search metadata and analytics

Production domain: https://protectourpoconos.com/. Edit the existing root HTML files as before; **do not edit `_site/`**. Run:

```sh
python3 scripts/sync-projects.py
python3 scripts/build-site.py
python3 -m unittest discover -s tests
python3 -m http.server 4174 --directory _site
```

The production build generates `/`, `/news/`, `/projects/`, `/issues/`, and `/take-action/`, rewrites internal links/assets, and creates static redirects for old `.html` links, preserving queries and anchors when JavaScript is enabled. GitHub Pages does not provide custom HTTP 301 rules, so these use immediate meta refresh plus JavaScript. Root HTML files remain authoring previews; use port 4174 for the actual published layout and URLs.

`scripts/build-site.py` owns the route registry, canonical domain, social preview metadata, WebSite/Organization/page/breadcrumb structured data, robots.txt and XML sitemap. Add future pages to its `PAGES` registry. Every Pages deployment rebuilds these files. Submit **https://protectourpoconos.com/sitemap.xml** to Search Console after deployment. Last-modified dates are deliberately omitted rather than reporting inaccurate build dates. Schema describes the actual site and does not promise special search or AI results.

Google Analytics 4 measurement ID `G-XR259KZ2L9` is loaded by `assets/js/analytics.js` only on the public domain (including www). Local and GitHub-hostname previews do not send analytics. This is a Google tag, not a Google Tag Manager container. The privacy notice on each page describes analytics cookies, collected usage/device/referrer information, and Google Fonts. Keep those notices accurate when changing tracking. Email signup and tip forms remain unavailable.

Pushes to main now publish the site, including subtitle edits made through GitHub.


## Resources and agentic browsing

Edit `resources.html` for the Research and Sources page, with its scoped styles in `assets/css/resources.css`. Its shared header/footer come from the homepage; keep those shells consistent. Township records use native `details`/`summary` disclosures, so the links are available without JavaScript. Prefer specific official documents over homepage links, and label meeting minutes as minutes rather than implying they are an ordinance's full text. Tip submissions remain unavailable.

`llms.txt` is the concise public site guide. Update its page list when adding or removing canonical pages; the build publishes it alongside the sitemap. The standard-library tests check these links. Google Fonts use `display=optional` to avoid late font swaps moving content; on slow first visits the browser may retain the fallback font until a later navigation. This does not add WebMCP or change site features.

For an optional independent audit (no project dependency): `npx lighthouse https://protectourpoconos.com/ --chrome-flags="--headless" --output=json --output-path=/tmp/poconos-lighthouse.json`. Agentic Browsing evaluates applicable audits; record the actual result and CLS, rather than assuming a fixed score on every device or run.

## Image delivery

Pages use WebP copies of the supplied raster assets; original PNGs remain available for editing. Keep WebP variants updated when replacing artwork (current encoding: Pillow WebP quality 82, method 6). Content images have dimensions and lazy loading; the homepage hero is preloaded. The inline head script establishes the JavaScript-enabled menu state before first paint, preventing a late mobile navigation collapse. Do not move it back into the deferred script alone.

GitHub Pages controls HTTP cache lifetimes; CSS/JS content versions invalidate changed files but do not change the host's cache policy. Performance results should be compared using a fresh public-site audit, not a local uncompressed development server.

### FAQ and section navigation

Edit `faq.html` for questions and answers. The build generates FAQPage structured data from native details answers and the visible stance section, alongside the sitemap and breadcrumb graph. No separate schema copy needs maintenance. Shared jump offsets measure the header and any sticky topic bar once, without extra section margins.
