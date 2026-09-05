# Protect Our Poconos

Static homepage based on the supplied **Protect Our Poconos Dark** mockup. Original waterfall, forest, mountain, logo, and scale illustration assets are preserved. Built with HTML, Foundation for Sites 6.9.0 CSS, and a small vanilla JavaScript file. No npm install or build step required.

## Preview

From this directory:

```sh
python3 -m http.server 4173 --bind 127.0.0.1
```

Open http://localhost:4173. Stop with Ctrl+C. In GitHub Desktop, add this folder as a local repository.

## Files

- `index.html`: homepage content and semantic sections.
- `assets/css/design.css`: exact dark mockup styling extracted from the export and deduplicated. Section-prefixed selectors map back to HTML.
- `assets/css/site.css`: responsive layouts, mobile navigation, accessibility, and small visual fixes.
- `assets/js/site.js`: menu, accessible dialogs for unfinished destinations, and sharing.
- `assets/vendor/`: local Foundation CSS and its MIT license. Foundation XY grid container/cell classes are used alongside the mockup's custom column ratios.
- `.github/workflows/pages.yml`: manual GitHub Pages deployment, uploading public files only.

## GitHub Pages

In the GitHub repository, select **Settings → Pages → Build and deployment → Source: GitHub Actions**. When ready, select **Actions → Deploy static homepage to GitHub Pages → Run workflow**. Deployment is manual so pushing design changes does not automatically publish draft content. Relative asset paths work on a project Pages URL or a custom domain.

Docs: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Content still needed

Homepage copy was revised against linked public records on September 5, 2026. Smithfield figures come from the August resubmission, Lehman adoption from the November 20, 2025 minutes, and the September 9 hearing from the township August newsletter. Project/news cards now link to those records. Eagle Village remains explicitly unconfirmed. The old September 18 Pike County meeting date was removed rather than advertised as upcoming.

- Actual project and news photos: the export's seven image slots were empty; they remain clearly marked placeholders.
- Dedicated article/project pages; verified cards currently link directly to public source documents.
- A newsletter signup provider or hosted form URL; no email collection or fake success state is implemented.
- Current meeting calendar, officials directory, public-comment instructions, research library, and social/contact links.
- Privacy text should be updated when services are added. Google Fonts is currently the only external frontend dependency; Foundation and images are local.

Remaining unfinished links open an explanatory dialog. Replace their `href` and remove `data-notice` / `data-notice-title` once the destination exists. The mockup's fake search button was removed. Share uses the browser share sheet or clipboard, with a visible fallback.

## Later WordPress migration

Keep these CSS and image files. Split the header/footer into theme templates, move homepage sections to `front-page.php`, enqueue Foundation followed by the two site stylesheets, and replace project/news cards with WordPress loops. No rewrite into another frontend framework is needed.

## Checks

```sh
node --check assets/js/site.js
git diff --check
```

Check the homepage at desktop, tablet, and mobile widths, including mobile menu, keyboard focus, Escape dismissal, image loading, and anchor navigation.
