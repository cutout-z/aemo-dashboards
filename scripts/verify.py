#!/usr/bin/env python3
"""End-to-end check of this checkout: the home page served the way Pages serves it, and the five live
dashboards running this checkout's nav.js in place of the published one.

Usage: python3 scripts/verify.py [--home-only | --published]

--published checks the deployed site instead, after a merge: the published nav.js must equal this
checkout's, and every page runs the published files.

Exits 0 when every check passes, 1 when any fails (each failure is printed), 2 when it can't run
(Playwright missing, a live dashboard unreachable). Needs Playwright with Chromium
(requirements-dev.txt) and, unless --home-only, network access to cutout-z.github.io.
See docs/verify.md for what each check means and what this doesn't cover.
"""

import argparse
import contextlib
import functools
import http.server
import os
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = "https://cutout-z.github.io/"
LIVE_NAV = PAGES + "aemo-dashboards/nav.js"
SIDEBAR_W = 232
DESKTOP, PHONE = (1440, 900), (375, 812)
# repo -> sidebar label, in sidebar order; must match DASHBOARDS in nav.js (checked below).
# The generator credit landing page is a search box; its charts draw on a unit's page (#<DUID>).
OPEN_AT = {"aemo-generator-credit-dashboard": "#CLRKCWF1"}
DASHBOARDS = {
    "aemo-historical-prices": "Historical Prices",
    "aemo-negative-prices": "Negative Prices",
    "aemo-generator-credit-dashboard": "Generator Credit",
    "aemo-renewable-generator-dashboard": "Renewable Generators",
    "aemo-mlf-tracker": "MLF Tracker",
}
EXPECTED_LINKS = [["Overview", PAGES + "aemo-dashboards/"]] + [[label, PAGES + repo + "/"] for repo, label in DASHBOARDS.items()]

failures = []
SHOTS = None  # a folder for one screenshot per view (--screenshots), for the by-eye pass


def shoot(page, where):
    if SHOTS:
        page.screenshot(path=str(SHOTS / (where.replace(" ", "_") + ".png")))


def check(ok, what):
    print(("  ok    " if ok else "  FAIL  ") + what)
    if not ok:
        failures.append(what)
    return ok


@contextlib.contextmanager
def serve():
    """Serve a folder holding /aemo-dashboards/ -> this checkout, on a free loopback port."""
    with tempfile.TemporaryDirectory() as tmp:
        os.symlink(ROOT, Path(tmp) / "aemo-dashboards")

        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass

        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Quiet, directory=tmp))
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        try:
            yield f"http://127.0.0.1:{port}/aemo-dashboards/"
        finally:
            httpd.shutdown()


def watch(page):
    log = {"errors": [], "nav_errors": [], "nav_status": []}
    page.on("pageerror", lambda e: log["errors"].append(f"{e}"))
    page.on("console", lambda m: log["errors"].append(m.text) if m.type == "error" else None)
    page.on("response", lambda r: log["nav_status"].append(r.status) if r.url.split("?")[0].endswith("/nav.js") else None)
    return log


SIDEBAR_STATE = """() => {
  const side = document.getElementById('aemo-sidebar');
  const cur = side ? [...side.querySelectorAll('[aria-current=page]')].map(e => e.textContent.trim()) : null;
  const links = side ? [...side.querySelectorAll('.aemo-nav-link')].map(e => [e.textContent.trim(), e.href]) : [];
  const probe = document.createElement('div');
  probe.style.background = 'var(--bg, #0a0a0a)';
  document.body.appendChild(probe);
  const pageBg = getComputedStyle(probe).backgroundColor;
  probe.remove();
  const bar = document.querySelector('.aemo-topbar');
  // the topmost element at a point inside the sidebar: anything of the page's painted over it shows here
  const hit = document.elementFromPoint(116, Math.round(innerHeight / 2));
  return {
    sidebar: !!side, current: cur, links,
    sidebarVisible: !!side && getComputedStyle(side).visibility === 'visible' && side.getBoundingClientRect().right > 0,
    sidebarWidth: side ? Math.round(side.getBoundingClientRect().width) : 0,
    sidebarOnTop: !!side && side.contains(hit),
    sidebarBg: side ? getComputedStyle(side).backgroundColor : null, pageBg,
    padLeft: getComputedStyle(document.body).paddingLeft,
    topbar: !!bar && getComputedStyle(bar).display !== 'none',
    theme: document.documentElement.getAttribute('data-theme'),
    hScroll: document.documentElement.scrollWidth - innerWidth,
  };
}"""

# The page's own content: the leftmost visible box of real content, and the drawn charts and tables.
CONTENT_STATE = """() => {
  const skip = el => el.closest('#aemo-sidebar, .aemo-topbar, .aemo-scrim');
  let left = Infinity, n = 0;
  for (const el of document.body.querySelectorAll('h1, h2, p, table, canvas, svg, .js-plotly-plot')) {
    if (skip(el)) continue;
    const r = el.getBoundingClientRect();
    // off-screen helpers (measuring boxes, screen-reader text parked at -10000px) are not content
    if (r.width < 1 || r.height < 1 || r.right <= 0 || getComputedStyle(el).visibility === 'hidden') continue;
    left = Math.min(left, r.left); n++;
  }
  const big = el => { const r = el.getBoundingClientRect(); return r.width >= 200 && r.height >= 80; };
  const drawn = [...document.querySelectorAll('canvas, svg, .js-plotly-plot')].filter(e => !skip(e) && big(e));
  const charts = drawn.length;
  // charts sized to the width left beside the sidebar: none runs past the window's right edge
  const chartRight = drawn.length ? Math.round(Math.max(...drawn.map(e => e.getBoundingClientRect().right)) - innerWidth) : 0;
  const tables = [...document.querySelectorAll('table')].filter(t => !skip(t) && t.querySelectorAll('tbody tr').length >= 3).length;
  return { left: Math.round(left), boxes: n, charts, tables, chartRight, h1: (document.querySelector('h1') || {}).innerText || '' };
}"""


def check_sidebar(st, width, current, where):
    check(st["sidebar"], f"{where}: sidebar built")
    check(st["links"] == EXPECTED_LINKS, f"{where}: sidebar lists Overview + the five dashboards, live URLs, in order")
    check(st["current"] == [current], f"{where}: '{current}' is the one highlighted link (got {st['current']})")
    check(st["sidebarBg"] == st["pageBg"], f"{where}: sidebar background follows the page's --bg ({st['sidebarBg']} vs {st['pageBg']})")
    if width >= 1024:
        check(st["sidebarVisible"] and st["sidebarWidth"] == SIDEBAR_W, f"{where}: sidebar visible, {SIDEBAR_W}px wide")
        check(st["sidebarOnTop"], f"{where}: nothing of the page paints over the sidebar")
        check(st["padLeft"] == f"{SIDEBAR_W}px" and not st["topbar"], f"{where}: body padded {SIDEBAR_W}px, no top bar (got {st['padLeft']})")
    else:
        check(st["topbar"] and not st["sidebarVisible"], f"{where}: top bar shown, drawer closed")
        check(st["padLeft"] == "0px", f"{where}: body not padded (got {st['padLeft']})")
    check(st["hScroll"] <= 1, f"{where}: no sideways scroll ({st['hScroll']}px wider than the window)")


def check_drawer(page, current, where):
    toggle = page.locator(".aemo-topbar button")
    if not check(toggle.count() == 1 and toggle.is_visible(), f"{where}: menu button shown"):
        return
    toggle.click()
    page.wait_for_timeout(300)  # the 0.2s slide-in
    st = page.evaluate(SIDEBAR_STATE)
    check(st["sidebarVisible"] and st["sidebarOnTop"], f"{where}: drawer opens over the page")
    check(page.evaluate("document.activeElement && document.activeElement.innerText.trim()") == current,
          f"{where}: focus lands on the current page's link")
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    check(not page.evaluate(SIDEBAR_STATE)["sidebarVisible"], f"{where}: Escape closes the drawer")
    toggle.click()
    page.wait_for_timeout(300)
    page.mouse.click(page.viewport_size["width"] - 10, page.viewport_size["height"] // 2)
    page.wait_for_timeout(300)
    check(not page.evaluate(SIDEBAR_STATE)["sidebarVisible"], f"{where}: tapping the backdrop closes the drawer")


def check_home(browser, url):
    print(f"\nHome page at {url}")
    for theme in ("dark", "light"):
        for width, height in (DESKTOP, PHONE):
            where = f"home {width}px {theme}"
            ctx = browser.new_context(viewport={"width": width, "height": height}, service_workers="block")
            page = ctx.new_page()
            log = watch(page)
            page.goto(f"{url}?theme={theme}", wait_until="networkidle")
            st = page.evaluate(SIDEBAR_STATE)
            check(log["nav_status"] == [200], f"{where}: nav.js loaded (statuses {log['nav_status']})")
            check(st["theme"] == theme, f"{where}: theme is {theme}")
            check_sidebar(st, width, "Overview", where)
            cards = page.eval_on_selector_all("#sections .card-title", "els => els.map(e => [e.innerText, e.href])")
            check(cards == EXPECTED_LINKS[1:], f"{where}: one card per dashboard, linking to its live URL")
            if width < 1024 and theme == "dark":
                check_drawer(page, "Overview", where)
            check(not log["errors"], f"{where}: no page or console errors {log['errors'] or ''}")
            shoot(page, where)
            ctx.close()


def check_dashboard(browser, repo, label, nav_js):
    """nav_js: the bytes to serve in place of the published nav.js; None runs the published one."""
    url = PAGES + repo + "/" + OPEN_AT.get(repo, "")
    print(f"\n{label}: live page {url}, " + ("with this checkout's nav.js" if nav_js else "as published"))
    for width, height in (DESKTOP, PHONE):
        for theme in ("dark", "light"):
            where = f"{repo} {width}px {theme}"
            ctx = browser.new_context(viewport={"width": width, "height": height}, service_workers="block")
            if nav_js:
                ctx.route(LIVE_NAV + "*", lambda route: route.fulfill(status=200, body=nav_js, content_type="application/javascript"))
            page = ctx.new_page()
            log = watch(page)
            try:
                resp = page.goto(url, wait_until="networkidle", timeout=60000)
            except Exception as exc:  # a network problem, not a failed check
                print(f"  cannot load {url}: {exc}")
                sys.exit(2)
            if not resp or resp.status != 200:
                print(f"  cannot load {url}: HTTP {resp.status if resp else '?'}")
                sys.exit(2)
            page.wait_for_timeout(1500)  # charts draw after their data arrives
            # The dashboards switch theme with the data-theme attribute on <html>; nav.js reads the tokens live.
            page.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
            st = page.evaluate(SIDEBAR_STATE)
            check(log["nav_status"] == [200], f"{where}: page loaded nav.js once (statuses {log['nav_status']})")
            check_sidebar(st, width, label, where)
            c = page.evaluate(CONTENT_STATE)
            check(c["boxes"] > 0 and c["h1"].strip(), f"{where}: page content rendered (h1 '{c['h1'].strip()[:40]}')")
            check(c["charts"] + c["tables"] > 0, f"{where}: a chart or data table drew ({c['charts']} charts, {c['tables']} tables)")
            check(c["chartRight"] <= 1, f"{where}: charts fit the window ({c['chartRight']}px past its right edge)")
            if width >= 1024:
                check(c["left"] >= SIDEBAR_W, f"{where}: content starts right of the sidebar (leftmost box at {c['left']}px)")
            if width < 1024 and theme == "dark":
                check_drawer(page, label, where)
            check(not log["errors"], f"{where}: no page or console errors {log['errors'] or ''}")
            shoot(page, where)
            ctx.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--home-only", action="store_true", help="skip the five live dashboards (no network needed)")
    mode.add_argument("--published", action="store_true", help="check the deployed site, after a merge")
    ap.add_argument("--screenshots", metavar="DIR", type=Path, help="save a screenshot of every view in DIR")
    args = ap.parse_args()
    global SHOTS
    if args.screenshots:
        SHOTS = args.screenshots
        SHOTS.mkdir(parents=True, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright missing: pip install -r requirements-dev.txt && playwright install chromium")
        return 2

    nav_js = (ROOT / "nav.js").read_bytes()
    for repo, label in DASHBOARDS.items():  # the list above must be the one nav.js renders
        check(f"label: '{label}', path: '{repo}/'".encode() in nav_js, f"nav.js lists {label} at {repo}/")

    start = time.time()
    if args.published:
        import urllib.request
        # a fresh query string skips the Pages cache (about 10 minutes) for this one fetch
        with urllib.request.urlopen(f"{LIVE_NAV}?verify={int(start)}", timeout=30) as r:
            live = r.read()
        check(live == nav_js, "published nav.js matches this checkout (if not: Pages hasn't deployed yet, or the checkout isn't main)")
    with (contextlib.nullcontext(PAGES + "aemo-dashboards/") if args.published else serve()) as url, sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            check_home(browser, url)
            if not args.home_only:
                for repo, label in DASHBOARDS.items():
                    check_dashboard(browser, repo, label, None if args.published else nav_js)
        finally:
            browser.close()

    scope = "home page only" if args.home_only else "published site" if args.published else "home page + live dashboards with this nav.js"
    print(f"\n{len(failures)} failed, {time.time() - start:.0f}s ({scope})")
    for f in failures:
        print("  FAIL  " + f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
