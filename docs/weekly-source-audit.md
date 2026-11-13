# Source-freshness and development audit

Run this on Monday and Wednesday at 9 a.m. and Saturday at noon, America/New_York, for the local Protect Our Poconos site. Review the live site at https://protectourpoconos.com/ and its currently linked live pages, including https://protectourpoconos.com/projects/ and https://protectourpoconos.com/faq/. Compare what is published live with newly available evidence and the local source files. This is an editorial maintenance pass, not a publishing or redesign task. Work in the repository source files; do not edit generated `_site/` output. Do not advance dates merely because this instruction ran.

## Catch up after a missed run

At the start, read `docs/source-audit-runs.md` and compare its most recent run with every scheduled Monday, Wednesday, and Saturday slot since then. If no run is logged yet, compare slots since the November 3, 2026 schedule baseline in that file. Record any missed slots. Search for developments across the entire interval since the last completed development scan, including the most recent missed slot; do not limit searches to the current day or assume no news because a scheduled run was missed. Check whether an earlier lead became confirmed, changed, or was superseded during the gap. If the log has no completed scan yet, use the last documented site review and the available prior audit notes as the starting point, and state the uncertainty. A missed slot is recovered only when the later scan actually covers its interval. The next scheduled run performs this catch-up; the schedule itself does not establish that a sleeping computer will run the task immediately on wake.

After the run, append one concise row to `docs/source-audit-runs.md` with the actual run time, missed slots recovered, the development-scan coverage end, and separate Projects/FAQ completion status. Record a failed or partial scan as such; never advance its coverage end or page-review dates as if verification succeeded. Keep the log as audit history, not a source of project facts.

## Scope and source of truth

- Use every `article.tracker-card` in `projects.html`, including documented proposals, infrastructure, watchlist sites, and rumors. Use every article in its `.policy-grid` as a policy entry. Recount these each run; do not rely on an old total.
- `projects.html` is the source for shared project facts. `scripts/sync-projects.py` copies marked facts into `index.html`, `issues.html`, and `take-action.html`. Also inspect the surrounding unbound copy on those pages, `faq.html`, `resources.html`, and time-sensitive items in `assets/data/news.json` and `news.html`.
- Keep news history in `assets/data/news.json`; `scripts/render-news.py` writes the visible news sections. Do not create a news item merely to record a source review.
- Review every question, answer, cited link, and time-sensitive claim in `faq.html` on each run. Compare project and policy answers against the newly checked tracker records, and verify other factual answers against their linked sources and current authoritative material. Record whether the **entire FAQ page** was checked; a tracker audit alone does not complete the FAQ review.

## Look for new developments

Search official township, county, Pennsylvania state, utility, court, and other public records, plus reputable local reporting, for meaningful data-center and related-infrastructure developments in Pike County, Monroe County, and the wider Poconos/Northeast Pennsylvania region. Prioritize Smithfield Gateway, Pennsylvania Glacial Till/Tobyhanna, Pocono Manor, Shawnee–Walker, Pocono Manor transmission, Dingman Towne Center, Eagle Village/Tamiment, Lehman Township rules, Project Hazelnut, Lower Towamensing, and relevant Pennsylvania data-center policy. Include new documented proposals, filings, hearings and public-comment dates, approval or appeal changes, revised specifications, utility developments, and strong reporting worth linking. Check whether a community rumor has gained or lost documentary support. Compare each finding with the relevant live page and local source before proposing a change; name the exact page and section affected. Do not turn a lead into a confirmed project without evidence.

## Verify each entry

For each tracker card and policy article, record the entry name and what you actually checked in the final report. Follow **all** existing source links. Check the relevant current municipal agendas, minutes, zoning filings and notices; court dockets and orders; utility, regulator, and transmission-project records; and reputable local reporting. Search for newly issued official records, not only changes at previously linked URLs. Verify status, hearing dates and venue, approval stage, proposed size and other specifications, litigation, and unresolved questions. Compare each material claim with the source that supports it.

Check whether source URLs are broken, redirected, superseded, or point to a generic homepage when a specific current record is available. A successful HTTP response alone does not prove a document's contents. If a site blocks access, times out, or a record cannot be opened, report that limitation and leave its claims unverified unless another reliable source independently supports them. Do not call the entry verified or advance its date on the strength of a failed request.

Keep attribution explicit: official government, court, utility, and regulatory records; independent reporting; developer statements; community or opposition statements; and unverified rumors are different evidence classes. Treat projections, allegations, and rumors as such. When reliable sources conflict, show the conflict and flag it for follow-up; do not choose a date or outcome without support. Correct stale copy or label an unsupported development unverified. Do not change a project status without evidence.

## Dates and events

- **Source verification:** Update an entry's `Sources reviewed` `<time datetime="YYYY-MM-DD">` in `projects.html` only after its relevant sources and claims were genuinely checked. It may advance when nothing changed. Policy articles currently have no per-entry reviewed date; report their verification individually without adding a new tracking system.
- **Substantive update:** The date of a material change to a project or policy is distinct from source verification. Preserve any existing editorial update or event date; change it only when the underlying content actually changes and the date's meaning remains clear.
- **Complete tracker audit:** Advance the `Last reviewed` date in the `projects.html` hero only when **every** active tracker card and policy article was checked in this run. If any entry is incomplete, retain the previous Projects page date and say so.
- **Complete FAQ review:** Advance the separate `Last reviewed` date in the `faq.html` hero only when **every** FAQ answer and its relevant sources were checked in this run. If any answer is incomplete, retain the previous FAQ page date and say so. A completed Projects review does not authorize advancing the FAQ date, or vice versa.
- On `news.html`, the visible date and RSS `pubDate` should be the linked article’s publication date or official source’s issuance date, not the day this site found, reviewed, or updated it. Keep later verification and editorial-update dates in `contextNote`. If an official source is undated and its release date cannot be established, flag that limitation; do not silently present an audit date as a source date.
- Do not change article publication dates just because sources were checked.

Inspect all time-sensitive copy and structured dates on every run, especially `data-deadline` in `projects.html`, the meeting card in `index.html`, `take-action.html`, and news summaries/context notes. Keep the homepage meeting card on the next independently verified upcoming hearing or important date; after that date passes, replace it with the next verified item or remove its upcoming framing. Verify future meetings and deadlines against the latest official notice. Remove completed events from upcoming sections while retaining accurate historical reporting. Use retrospective wording after a date passes. A passed date does not establish that a meeting occurred, an outcome, or a new continuation date; flag pending proceedings for follow-up.

## Apply and check

Make the smallest supported edits in the existing files. When tracker facts change, run `python3 scripts/sync-projects.py`. When news metadata changes, run `python3 scripts/render-news.py` and inspect the resulting diff. Then run:

```sh
python3 scripts/sync-projects.py --check
python3 scripts/render-partials.py --check
python3 -m unittest discover -s tests
git diff --check
```

Check the final diff for unsupported factual changes and unintended date changes. Keep the work local; do not deploy as part of the audit.

## Audit report and notification

At the end of each run, record the audit date and report:

1. Projects, infrastructure, watchlist, rumor, and policy entries successfully verified (name each one).
2. Actual copy, status, link, or date changes, with affected files; explicitly say when no content corrections were needed.
3. Sources inaccessible or not independently verified, including the failed URL or record and which entry it affects.
4. Items needing manual investigation or a later official notice.
5. Expired events removed from upcoming sections or preserved as historical coverage.
6. Whether the complete tracker and policy audit finished, and whether the Projects page `Last reviewed` date advanced.
7. Whether the complete FAQ review finished, and whether the FAQ page `Last reviewed` date advanced.
8. Which scheduled slots were missed, whether their development-scan interval was recovered, and any gap still unverified.

If verification is partial, report the entries or FAQ answers not completed and leave their dates unchanged. Do not imply that a local edit has been published live.

Keep the user-facing notification focused on meaningful site-maintenance opportunities, completed local corrections, failures, or items requiring action. When there is a new development, distinguish verified facts from speculation, explain why it matters, identify the exact live page and section, and give concise coding-agent-ready instructions or replacement wording when useful. Do not repeat unchanged sections or send a routine full brief solely because the scheduled run occurred. If nothing meaningful changed, no content corrections were needed, and no action is required, keep the notification quiet; still update only source-verification dates justified by completed checks and record any partial verification accurately.
