"""Static guard: every link nav.js can render points at a known dashboard site.

nav.js runs on five other sites, so a typo in DASHBOARDS breaks all of them at once with no PR in their
repos. The known list is the Keys row of AGENTS.md; adding a dashboard means adding it here too.
"""

import re

from nav_harness import ROOT

NAV = (ROOT / "nav.js").read_text()

# key -> repo (the path on cutout-z.github.io is `<repo>/`)
KNOWN = {
    "historical-prices": "aemo-historical-prices",
    "negative-prices": "aemo-negative-prices",
    "generator-credit": "aemo-generator-credit-dashboard",
    "renewable-generators": "aemo-renewable-generator-dashboard",
    "mlf-tracker": "aemo-mlf-tracker",
}


def _items():
    body = NAV[NAV.index("var DASHBOARDS = ["):NAV.index("// Lucide-style")]
    return re.findall(r"key: '([^']+)', label: '([^']+)', path: '([^']+)', icon: '([^']+)',\s*repo: '([^']+)'", body)


def test_every_item_points_at_a_known_dashboard():
    items = _items()
    assert {k: r for k, _, _, _, r in items} == KNOWN
    for key, label, path, icon, repo in items:
        assert path == repo + "/", (key, path, repo)
        assert label.strip(), key
        assert re.search(rf"\n    {icon}: '", NAV), f"{key}: icon {icon!r} has no entry in ICONS"


def test_links_are_built_on_the_public_pages_origin():
    assert "var BASE = 'https://cutout-z.github.io/';" in NAV
    assert "var HOME = BASE + 'aemo-dashboards/';" in NAV
    assert "http://" not in re.sub(r"http://www\.w3\.org/2000/svg", "", NAV)


def test_the_documented_keys_match_the_known_list():
    agents = (ROOT / "AGENTS.md").read_text()
    row = next(line for line in agents.splitlines() if line.startswith("| Keys |"))
    assert set(re.findall(r"`([a-z-]+)`", row)) == set(KNOWN) | {"home"}
