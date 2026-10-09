# Repo contract — AEMO Dashboards (`cutout-z/aemo-dashboards`)

Read this before touching anything. This repo is the home page and the shared sidebar for the five
AEMO dashboards; it holds no data and no pipeline. The family conventions below are generated from
the `agent-contracts` repo; where this file's repo-specific rules are stricter, they win.

<!-- BEGIN agent-contracts:family -->
<!-- END agent-contracts:family -->

## Hard rules

1. **`main` is the public site.** GitHub Pages serves the repo root of `main` (branch deploy, no
   workflow). Anything committed to `main` is published, this file included. Screenshots, scratch
   and pass notes stay on their branch. Never commit a secret.
2. **`nav.js` runs on five other sites.** Every AEMO dashboard loads it from
   `https://cutout-z.github.io/aemo-dashboards/nav.js`, so a change here changes all five pages at
   once, with no PR in their repos. Before merging a `nav.js` change, check every dashboard in a real
   browser at desktop and phone widths, in both themes (see *Verify*).
3. **`nav.js` stays self-contained and harmless.** It only adds its own elements (`.aemo-*` classes,
   `#aemo-sidebar`) and the `aemo-nav-on` / `aemo-nav-open` classes on `<html>`. It never reads or
   changes a page's data, never loads other scripts, and must leave the page working if it throws.
4. **No data here.** Each dashboard's data, pipeline and schedule stay in its own repo.

## Facts

| What | Detail |
|---|---|
| Served at | `https://cutout-z.github.io/aemo-dashboards/` (GitHub Pages, `main`, root) |
| Files | `index.html` (home page), `nav.js` (shared sidebar), `README.md` |
| Dashboard list | `DASHBOARDS` in `nav.js`; the home page renders from it via `window.AEMO_NAV` |
| How pages load it | `<script src="https://cutout-z.github.io/aemo-dashboards/nav.js" data-current="<key>">` at the end of `<head>`, not `defer`/`async` |
| Keys | `historical-prices`, `negative-prices`, `generator-credit`, `renewable-generators`, `mlf-tracker`; `home` for this site |
| Layout | Fixed 232px left sidebar at 1024px and wider (pads `body`); below that, a 48px top bar and a drawer |
| Theme | Uses the family colour tokens (`--bg`, `--line-soft`, `--text`, `--accent` …) from each page, with dark fallbacks; the home page defines the same tokens inline. Home theme key: `aemo-dashboards:theme` |
| Caching | GitHub Pages caches for about 10 minutes, so a `nav.js` change can take that long to show |

## Verify

Serve a folder that mirrors the live paths (`/aemo-dashboards/` plus each dashboard under its repo
name), with each dashboard's `index.html` loading `/aemo-dashboards/nav.js`, then open every page at
1440px and 375px wide, dark and light. Check: the current page is highlighted, nothing on the page is
covered or shifted under the sidebar, charts size to the narrower width, the phone drawer opens,
closes on Escape and on the backdrop, and the console shows no errors from `nav.js`.
