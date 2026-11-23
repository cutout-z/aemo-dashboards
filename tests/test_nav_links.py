"""Static guard: every link nav.js can render points at a known dashboard site.

nav.js runs on five other sites, so a typo in DASHBOARDS breaks all of them at once with no PR in their
repos. The known keys are read from nav.js; the Keys row of AGENTS.md and the data-current each page repo
sends (tests/fixtures/page_nav_keys.txt) are checked against them.
"""

import re

from nav_harness import ROOT

NAV = (ROOT / "nav.js").read_text()


def _items():
    body = NAV[NAV.index("var DASHBOARDS = ["):NAV.index("// Lucide-style")]
    return re.findall(r"key: '([^']+)', label: '([^']+)', path: '([^']+)', icon: '([^']+)',\s*repo: '([^']+)'", body)


# key -> repo, read from nav.js itself (not a hand copy), so it cannot drift from what nav.js defines.
KNOWN = {k: r for k, _, _, _, r in _items()}


def _fixture_pairs():
    lines = (ROOT / "tests" / "fixtures" / "page_nav_keys.txt").read_text().splitlines()
    return [tuple(line.split()) for line in lines if line.strip() and not line.lstrip().startswith("#")]


def test_every_item_points_at_a_known_dashboard():
    items = _items()
    assert len(items) >= 5 and len(KNOWN) == len(items), "key regex lost items, or a key is duplicated"
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


def test_nav_js_defines_every_key_in_the_array_and_nothing_hidden():
    """The regex above must see every `key:` in nav.js (a differently formatted item would escape it)."""
    body = NAV[NAV.index("var DASHBOARDS = ["):NAV.index("// Lucide-style")]
    assert set(re.findall(r"\bkey:\s*'([^']+)'", body)) == set(KNOWN)


def test_every_page_repo_sends_a_known_data_current_for_its_own_repo():
    pairs = _fixture_pairs()
    assert len(pairs) == 5, pairs
    for repo, current in pairs:
        assert current in KNOWN, f"{repo} sends data-current={current!r}; nav.js knows {sorted(KNOWN)}"
        assert KNOWN[current] == repo, f"data-current={current!r} is {KNOWN[current]}'s key, not {repo}'s"
