"""Offline Playwright host for nav.js: no server, no port, no network.

http://aemo.test/ is routed to this checkout (nav.js, index.html) plus a small host page standing in for
a dashboard. Every other request is aborted and recorded; tests fail if any happened.
"""

import contextlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "http://aemo.test"

# A dashboard stand-in: the colour tokens nav.js reads, and the one tag the dashboards use.
HOST_HTML = """<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>host</title>
<style>:root{--bg:#0a0a0a;--text:#fafafa;--muted:#a3a3a3;--faint:#898989;--accent:#ff7a3d;
--line-soft:#212121;--surface-2:#1e1e1e}body{margin:0;background:var(--bg);color:var(--text)}</style>
%(tag)s</head><body><main id="page"><h1>Dashboard</h1><p>Page content that must not sit under the sidebar.</p></main></body></html>"""


class NavLog:
    def __init__(self):
        self.page_errors = []
        self.console_errors = []
        self.unexpected = []


@contextlib.contextmanager
def loaded(path="/index.html", width=1440, height=900, current=None):
    """Open `path` offline. /host.html is the stand-in dashboard (data-current=`current`, if given);
    any path ending in /host.html under another first segment lets nav.js derive its key from the URL."""
    from playwright.sync_api import sync_playwright

    log = NavLog()

    def handle(route):
        url = route.request.url
        if url.startswith(ORIGIN + "/"):
            p = url[len(ORIGIN):].split("?", 1)[0]
            if p.endswith("/host.html") or p == "/host.html":
                attr = f' data-current="{current}"' if current else ""
                body = HOST_HTML % {"tag": f'<script src="/nav.js"{attr}></script>'}
                return route.fulfill(status=200, body=body, content_type="text/html")
            if p in ("/nav.js", "/index.html"):
                return route.fulfill(
                    status=200,
                    body=(ROOT / p.lstrip("/")).read_bytes(),
                    content_type="application/javascript" if p.endswith(".js") else "text/html",
                )
        log.unexpected.append(f"{route.request.method} {url}")
        return route.abort()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            context = browser.new_context(viewport={"width": width, "height": height}, service_workers="block")
            context.route("**/*", handle)
            page = context.new_page()
            page.on("pageerror", lambda e: log.page_errors.append(str(e)))
            page.on("console", lambda m: log.console_errors.append(m.text) if m.type == "error" else None)
            page.goto(ORIGIN + path, wait_until="load")
            yield page, log
        finally:
            browser.close()


def assert_clean(log):
    problems = []
    if log.page_errors:
        problems.append(f"page errors: {log.page_errors}")
    if log.console_errors:
        problems.append(f"console errors: {log.console_errors}")
    if log.unexpected:
        problems.append(f"unexpected requests: {log.unexpected}")
    assert not problems, "; ".join(problems)
