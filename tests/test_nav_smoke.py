"""Rendered nav smoke: nav.js in headless chromium, offline (no server, no port, no network)."""

import pytest

try:
    import playwright  # noqa: F401
except ImportError as exc:  # a collection ERROR, which the merge gate counts; never a silent skip
    raise RuntimeError(
        "these smoke tests need Playwright (pinned in requirements-dev.txt); run the suite with "
        "/opt/anaconda3/bin/python3 (playwright 1.58.0 + chromium) or: pip install -r requirements-dev.txt "
        "&& playwright install chromium"
    ) from exc

from nav_harness import assert_clean, loaded  # noqa: E402

BASE = "https://cutout-z.github.io/"
EXPECTED = [  # [label, href] in sidebar order
    ["Overview", BASE + "aemo-dashboards/"],
    ["Historical Prices", BASE + "aemo-historical-prices/"],
    ["Negative Prices", BASE + "aemo-negative-prices/"],
    ["Generator Credit", BASE + "aemo-generator-credit-dashboard/"],
    ["Renewable Generators", BASE + "aemo-renewable-generator-dashboard/"],
    ["MLF Tracker", BASE + "aemo-mlf-tracker/"],
]


def _links(page):
    return page.eval_on_selector_all(
        "#aemo-sidebar .aemo-nav-link", "els => els.map(e => [e.innerText.trim(), e.href])"
    )


def test_desktop_sidebar_lists_every_dashboard_and_pads_the_body():
    with loaded("/host.html", width=1440, current="mlf-tracker") as (page, log):
        assert_clean(log)
        assert _links(page) == EXPECTED
        side = page.locator("#aemo-sidebar")
        assert side.is_visible() and side.bounding_box()["width"] == 232
        assert page.locator(".aemo-topbar").is_hidden()
        assert page.evaluate("document.documentElement.classList.contains('aemo-nav-on')")
        # the 232px rule AGENTS.md documents: content never sits under the fixed sidebar
        assert page.evaluate("getComputedStyle(document.body).paddingLeft") == "232px"
        assert page.locator("#page").bounding_box()["x"] >= 232
        current = page.locator("#aemo-sidebar [aria-current=page]")
        assert current.count() == 1 and current.inner_text().strip() == "MLF Tracker"


def test_padding_rule_starts_exactly_at_1024px():
    with loaded("/host.html", width=1024, current="mlf-tracker") as (page, log):
        assert page.evaluate("getComputedStyle(document.body).paddingLeft") == "232px"
        page.set_viewport_size({"width": 1023, "height": 900})
        assert page.evaluate("getComputedStyle(document.body).paddingLeft") == "0px"
        assert page.locator(".aemo-topbar").is_visible()
        assert_clean(log)


def test_home_page_renders_a_card_per_dashboard_and_marks_overview():
    with loaded("/index.html", width=1440) as (page, log):
        assert_clean(log)
        assert page.locator("#sections article.card").count() == 5
        titles = page.eval_on_selector_all("#sections .card-title", "els => els.map(e => [e.innerText, e.href])")
        assert titles == [e for e in EXPECTED[1:]]
        assert page.locator("#aemo-sidebar [aria-current=page]").inner_text().strip() == "Overview"
        assert page.evaluate("getComputedStyle(document.body).paddingLeft") == "232px"


def test_phone_top_bar_toggle_opens_and_closes_the_drawer():
    with loaded("/host.html", width=400, height=800, current="mlf-tracker") as (page, log):
        bar = page.locator(".aemo-topbar")
        toggle = bar.locator("button")
        assert bar.is_visible() and bar.bounding_box()["height"] == 48
        assert "MLF Tracker" in bar.inner_text()
        assert page.evaluate("getComputedStyle(document.body).paddingLeft") == "0px"
        assert page.locator("#aemo-sidebar").is_hidden()
        assert toggle.get_attribute("aria-expanded") == "false"

        toggle.click()  # opens, focus lands on the current page's link
        assert page.locator("#aemo-sidebar").is_visible()
        assert toggle.get_attribute("aria-expanded") == "true"
        assert page.evaluate("document.activeElement.getAttribute('aria-current')") == "page"

        page.keyboard.press("Escape")  # Escape closes
        page.locator("#aemo-sidebar").wait_for(state="hidden", timeout=3000)  # slides out, then visibility:hidden
        assert toggle.get_attribute("aria-expanded") == "false"

        toggle.click()  # scrim closes (click right of the 280px drawer)
        page.mouse.click(395, 400)
        assert toggle.get_attribute("aria-expanded") == "false"

        toggle.click()  # the close button closes
        page.locator(".aemo-nav-close").click()
        assert toggle.get_attribute("aria-expanded") == "false"
        assert_clean(log)


def test_open_drawer_closes_when_the_window_grows_to_desktop():
    with loaded("/host.html", width=400, height=800, current="mlf-tracker") as (page, log):
        page.locator(".aemo-topbar button").click()
        assert page.evaluate("document.documentElement.classList.contains('aemo-nav-open')")
        page.set_viewport_size({"width": 1200, "height": 800})
        page.wait_for_function("!document.documentElement.classList.contains('aemo-nav-open')")
        assert page.locator("#aemo-sidebar").is_visible()
        assert_clean(log)


def test_key_comes_from_the_url_when_data_current_is_missing():
    with loaded("/aemo-historical-prices/host.html", width=1440) as (page, log):
        current = page.locator("#aemo-sidebar [aria-current=page]")
        assert current.count() == 1 and current.inner_text().strip() == "Historical Prices"
        assert_clean(log)
