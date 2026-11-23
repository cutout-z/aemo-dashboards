# Verify recipe

The end-to-end check for this repo. Run it before you call a change to `nav.js` or `index.html` done,
and step 4 after the merge. It runs the real pages in headless Chromium: the home page served from your
checkout the way GitHub Pages serves it, and the five **live** dashboards with your checkout's `nav.js`
swapped in for the published one. That is what a wrong change breaks: `nav.js` runs on all five sites
the moment it reaches `main`.

Needs Python 3 with the pinned Playwright and Chromium (`pip install -r requirements-dev.txt && playwright
install chromium`) and network access to `cutout-z.github.io` and the CDNs the dashboards load.

## Steps

1. **Unit and offline smoke tests** (about 5 s, no network):

   ```bash
   python3 -m pytest -q -rfEs -p no:cacheprovider tests
   ```

   Expect `11 passed` (the count grows with the suite) and no errors. This is the merge gate; it runs
   `nav.js` against a stand-in page, never a real dashboard.

2. **End-to-end run** (about 60 s):

   ```bash
   python3 scripts/verify.py --screenshots /tmp/aemo-verify
   ```

   Expect the last line `0 failed, <n>s (home page + live dashboards with this nav.js)` and exit code 0.
   Exit 1 lists every failed check at the end; exit 2 means it couldn't run (Playwright missing, a
   dashboard unreachable), which is not a pass. `--home-only` skips the dashboards when offline; it
   proves less, so say so if you use it. A failure that also shows under `--published` (step 4, run
   before your change) is the dashboard's own, not your change's: name it as pre-existing.

   For the home page (served on a free loopback port under `/aemo-dashboards/`) and each dashboard, at
   1440 px and 375 px wide, dark and light, it checks:

   - the sidebar is built, lists Overview and the five dashboards with their live URLs in order, and
     highlights exactly the current page;
   - the sidebar's background is the page's own `--bg` (it follows the theme);
   - desktop: the sidebar is 232 px, nothing of the page paints over it, `body` is padded 232 px, and
     the page's leftmost content box starts right of it;
   - phone: the top bar shows, the drawer is closed, `body` isn't padded; the menu button opens the
     drawer over the page with focus on the current link, and Escape and the backdrop close it (the
     drawer in dark only);
   - no sideways scroll, and no chart runs past the window's right edge;
   - each dashboard ran this checkout's `nav.js` (the swap fired once), rendered its heading and drew
     at least one chart or data table (Generator Credit opens on one unit's page, `#CLRKCWF1`, since
     its landing page is a search box; it is the only dashboard with charts today, the other four
     show tables, so the chart-width check bites only there);
   - the home page shows one card per dashboard, linking to its live URL;
   - no page errors and no console errors.

3. **By eye** (about 3 minutes): open the screenshots from step 2. Check what the script can't judge:
   icons draw, labels aren't clipped or wrapped badly, the highlighted link and the text are readable
   in both themes, and the sidebar sits cleanly beside each dashboard's header. For a change to the
   home page's look, also serve it (`python3 -m http.server 9390 --bind 127.0.0.1`, then
   `http://127.0.0.1:9390/`) and try the theme toggle and hover states.

4. **After the merge** (about 60 s, from a checkout of `main`, at least 10 minutes after the merge):

   ```bash
   python3 scripts/verify.py --published
   ```

   Same checks against the deployed site, plus `published nav.js matches this checkout`. A mismatch
   right after a merge usually means Pages hasn't deployed or its cache hasn't expired: wait and rerun.
   The match check skips the cache but the pages don't, so before the 10 minutes are up the pages may
   still run the old copy.

## What it doesn't cover

- **Each dashboard's data and freshness.** The script sees that a chart or table drew, not that its
  numbers are right or current; that is each dashboard repo's own check.
- **Real phones and other browsers.** Only Chromium at a phone-sized window; Safari on iOS is untested.
- **The dashboards' own theme toggles.** The script sets `data-theme` on `<html>` directly; charts a
  dashboard draws once in the starting theme may keep the old colours, so judge chart colours by eye.
- **Pages deploy itself.** Steps 1 to 3 test your checkout; only step 4 tests what is live.
