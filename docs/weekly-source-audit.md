# Weekly source-freshness audit

Run this once a week for the local Protect Our Poconos site, including the two public pages at https://protectourpoconos.com/projects/ and https://protectourpoconos.com/faq/. This is an editorial maintenance pass, not a publishing or redesign task. Work in the repository source files; do not edit generated `_site/` output. Do not advance dates merely because this instruction ran.

## Scope and source of truth

- Use every `article.tracker-card` in `projects.html`, including documented proposals, infrastructure, watchlist sites, and rumors. Use every article in its `.policy-grid` as a policy entry. Recount these each run; do not rely on an old total.
- `projects.html` is the source for shared project facts. `scripts/sync-projects.py` copies marked facts into `index.html`, `issues.html`, and `take-action.html`. Also inspect the surrounding unbound copy on those pages, `faq.html`, `resources.html`, and time-sensitive items in `assets/data/news.json` and `news.html`.
- Keep news history in `assets/data/news.json`; `scripts/render-news.py` writes the visible news sections. Do not create a news item merely to record a source review.
- Review every question, answer, cited link, and time-sensitive claim in `faq.html` each week. Compare project and policy answers against the newly checked tracker records, and verify other factual answers against their linked sources and current authoritative material. Record whether the **entire FAQ page** was checked; a tracker audit alone does not complete the FAQ review.

## Verify each entry

For each tracker card and policy article, record the entry name and what you actually checked in the final report. Follow **all** existing source links. Check the relevant current municipal agendas, minutes, zoning filings and notices; court dockets and orders; utility, regulator, and transmission-project records; and reputable local reporting. Search for newly issued official records, not only changes at previously linked URLs. Verify status, hearing dates and venue, approval stage, proposed size and other specifications, litigation, and unresolved questions. Compare each material claim with the source that supports it.

Check whether source URLs are broken, redirected, superseded, or point to a generic homepage when a specific current record is available. A successful HTTP response alone does not prove a document's contents. If a site blocks access, times out, or a record cannot be opened, report that limitation and leave its claims unverified unless another reliable source independently supports them. Do not call the entry verified or advance its date on the strength of a failed request.

Keep attribution explicit: official government, court, utility, and regulatory records; independent reporting; developer statements; community or opposition statements; and unverified rumors are different evidence classes. Treat projections, allegations, and rumors as such. When reliable sources conflict, show the conflict and flag it for follow-up; do not choose a date or outcome without support. Correct stale copy or label an unsupported development unverified. Do not change a project status without evidence.

## Dates and events

- **Source verification:** Update an entry's `Sources reviewed` `<time datetime="YYYY-MM-DD">` in `projects.html` only after its relevant sources and claims were genuinely checked. It may advance when nothing changed. Policy articles currently have no per-entry reviewed date; report their verification individually without adding a new tracking system.
- **Substantive update:** The date of a material change to a project or policy is distinct from source verification. Preserve any existing editorial update or event date; change it only when the underlying content actually changes and the date's meaning remains clear.
- **Complete tracker audit:** Advance the `Last reviewed` date in the `projects.html` hero only when **every** active tracker card and policy article was checked in this run. If any entry is incomplete, retain the previous Projects page date and say so.
- **Complete FAQ review:** Advance the separate `Last reviewed` date in the `faq.html` hero only when **every** FAQ answer and its relevant sources were checked in this run. If any answer is incomplete, retain the previous FAQ page date and say so. A completed Projects review does not authorize advancing the FAQ date, or vice versa.
- Do not change article publication dates just because sources were checked.

Inspect all time-sensitive copy and structured dates on every run, especially `data-deadline` in `projects.html`, the meeting card in `index.html`, `take-action.html`, and news summaries/context notes. Verify future meetings and deadlines against the latest official notice. Remove completed events from upcoming sections while retaining accurate historical reporting. Use retrospective wording after a date passes. A passed date does not establish that a meeting occurred, an outcome, or a new continuation date; flag pending proceedings for follow-up.

## Apply and check

Make the smallest supported edits in the existing files. When tracker facts change, run `python3 scripts/sync-projects.py`. When news metadata changes, run `python3 scripts/render-news.py` and inspect the resulting diff. Then run:

```sh
python3 scripts/sync-projects.py --check
python3 scripts/render-partials.py --check
python3 -m unittest discover -s tests
git diff --check
```

Check the final diff for unsupported factual changes and unintended date changes. Keep the work local; do not deploy as part of the audit.

## Weekly report

Report the audit date, then:

1. Projects, infrastructure, watchlist, rumor, and policy entries successfully verified (name each one).
2. Actual copy, status, link, or date changes, with affected files; explicitly say when no content corrections were needed.
3. Sources inaccessible or not independently verified, including the failed URL or record and which entry it affects.
4. Items needing manual investigation or a later official notice.
5. Expired events removed from upcoming sections or preserved as historical coverage.
6. Whether the complete tracker and policy audit finished, and whether the Projects page `Last reviewed` date advanced.
7. Whether the complete FAQ review finished, and whether the FAQ page `Last reviewed` date advanced.

If verification is partial, report the entries or FAQ answers not completed and leave their dates unchanged. Do not imply that a local edit has been published live.
