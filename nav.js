/* AEMO Dashboards: the shared sidebar.
 *
 * Served from https://cutout-z.github.io/aemo-dashboards/nav.js and loaded by every AEMO dashboard
 * with one tag at the end of <head> (plain, not defer/async, so the page reserves the sidebar's
 * space before its first paint and charts size themselves to the right width):
 *
 *   <script src="https://cutout-z.github.io/aemo-dashboards/nav.js" data-current="mlf-tracker"></script>
 *
 * data-current is the page's key in DASHBOARDS below; without it the key comes from the URL path.
 * Self-contained: it injects its own CSS, reads the page's colour tokens (--bg, --line, --text …)
 * so it follows the page's light/dark theme, and touches nothing else on the page. If this file
 * fails to load, the page works exactly as it did before.
 *
 * Adding or renaming a dashboard: edit DASHBOARDS here; the home page (index.html) renders from it.
 */
(function () {
  'use strict';
  if (window.AEMO_NAV) return;

  var BASE = 'https://cutout-z.github.io/';
  var HOME = BASE + 'aemo-dashboards/';
  var SIDEBAR_W = 232;
  var DESKTOP = '(min-width: 1024px)';

  var DASHBOARDS = [
    { section: 'Prices', items: [
      { key: 'historical-prices', label: 'Historical Prices', path: 'aemo-historical-prices/', icon: 'line',
        repo: 'aemo-historical-prices', cadence: 'Checked daily · monthly data',
        blurb: 'Monthly NEM spot prices by region, nominal and CPI-real, from July 2003.' },
      { key: 'negative-prices', label: 'Negative Prices', path: 'aemo-negative-prices/', icon: 'below',
        repo: 'aemo-negative-prices', cadence: 'Checked daily · monthly data',
        blurb: 'How often daylight dispatch prices fall below zero and deeper thresholds, from May 2019.' }
    ] },
    { section: 'Generators', items: [
      { key: 'generator-credit', label: 'Generator Credit', path: 'aemo-generator-credit-dashboard/', icon: 'shield',
        repo: 'aemo-generator-credit-dashboard', cadence: 'Updated daily',
        blurb: 'Generation, revenue, capacity factor, curtailment and price capture for each registered generator.' },
      { key: 'renewable-generators', label: 'Renewable Generators', path: 'aemo-renewable-generator-dashboard/', icon: 'sun',
        repo: 'aemo-renewable-generator-dashboard', cadence: 'Updated daily',
        blurb: 'Curtailment, loss factors and ISP forecasts for every utility-scale solar and wind farm.' },
      { key: 'mlf-tracker', label: 'MLF Tracker', path: 'aemo-mlf-tracker/', icon: 'gauge',
        repo: 'aemo-mlf-tracker', cadence: 'Updated monthly',
        blurb: 'Marginal loss factors for every NEM unit from FY15-16, with year-on-year changes.' }
    ] }
  ];

  // Lucide-style 24px stroke icons.
  var ICONS = {
    home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>',
    line: '<path d="M3 3v18h18"/><path d="m7 15 4-5 3 3 5-7"/>',
    below: '<path d="M3 12h18" stroke-dasharray="2 3"/><path d="M3 6c3 0 4 10 7 10s3-6 5-6 3 4 6 4"/>',
    shield: '<path d="M12 3 4.5 6v5.5c0 4.6 3.2 8.3 7.5 9.5 4.3-1.2 7.5-4.9 7.5-9.5V6z"/><path d="m9 12 2 2 4-4"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    gauge: '<path d="M4.5 18a9 9 0 1 1 15 0"/><path d="m12 13 4-5"/><circle cx="12" cy="13" r="1"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
    close: '<path d="M6 6l12 12M18 6 6 18"/>',
    external: '<path d="M14 4h6v6"/><path d="M20 4 11 13"/><path d="M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>'
  };

  function icon(name, cls) {
    return '<svg class="' + (cls || 'aemo-nav-icon') + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONS[name] + '</svg>';
  }

  function hrefOf(item) { return BASE + item.path; }

  var script = document.currentScript;
  function currentKey() {
    var k = script && script.getAttribute('data-current');
    if (k) return k;
    var seg = (location.pathname.split('/')[1] || '') + '/';
    if (seg === 'aemo-dashboards/') return 'home';
    for (var s = 0; s < DASHBOARDS.length; s++) {
      for (var i = 0; i < DASHBOARDS[s].items.length; i++) {
        if (DASHBOARDS[s].items[i].path === seg) return DASHBOARDS[s].items[i].key;
      }
    }
    return null;
  }

  var CSS = [
    'html.aemo-nav-on{--aemo-nav-w:' + SIDEBAR_W + 'px}',
    '.aemo-sidebar,.aemo-topbar,.aemo-scrim{box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Inter,system-ui,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}',
    '.aemo-sidebar *,.aemo-topbar *{box-sizing:border-box}',
    '.aemo-sidebar{position:fixed;top:0;bottom:0;left:0;z-index:60;width:var(--aemo-nav-w);display:flex;flex-direction:column;overflow-y:auto;padding:16px 12px;background:var(--bg,#0a0a0a);border-right:1px solid var(--line-soft,#212121);color:var(--text,#fafafa)}',
    '.aemo-brand{display:flex;align-items:center;gap:10px;padding:2px 6px 14px;text-decoration:none;color:inherit}',
    '.aemo-badge{display:flex;align-items:center;justify-content:center;flex:none;width:34px;height:34px;border-radius:9px;background:var(--accent,#ff7a3d);color:var(--bg,#0a0a0a);font-size:13px;font-weight:700;letter-spacing:.02em}',
    '.aemo-brand-name{display:block;font-size:14.5px;font-weight:600;line-height:1.25;color:var(--text,#fafafa)}',
    '.aemo-brand-sub{display:block;font-size:12.5px;line-height:1.3;color:var(--faint,#898989)}',
    '.aemo-nav-section{margin:16px 10px 4px;font-size:12px;font-weight:500;color:var(--faint,#898989)}',
    '.aemo-nav-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}',
    '.aemo-nav-link{display:flex;align-items:center;gap:10px;min-height:34px;padding:6px 10px;border-radius:8px;font-size:13.5px;line-height:1.3;color:var(--muted,#a3a3a3);text-decoration:none;transition:background-color .12s,color .12s}',
    '.aemo-nav-link:hover{background:var(--surface-2,#1e1e1e);color:var(--text,#fafafa)}',
    '.aemo-nav-link[aria-current=page]{background:var(--surface-2,#1e1e1e);color:var(--text,#fafafa);font-weight:500}',
    '.aemo-nav-link[aria-current=page] .aemo-nav-icon{color:var(--accent,#ff7a3d)}',
    '.aemo-nav-icon{flex:none;width:16px;height:16px}',
    '.aemo-sidebar a:focus-visible,.aemo-topbar button:focus-visible,.aemo-sidebar button:focus-visible{outline:2px solid var(--ring,rgba(255,122,61,.45));outline-offset:-2px}',
    '.aemo-nav-foot{margin-top:auto;padding:16px 10px 2px;font-size:12px;line-height:1.45;color:var(--faint,#898989)}',
    '.aemo-nav-close,.aemo-topbar button{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;margin:0;padding:0;border:0;border-radius:8px;background:transparent;color:var(--muted,#a3a3a3);cursor:pointer;font:inherit}',
    '.aemo-nav-close:hover,.aemo-topbar button:hover{background:var(--surface-2,#1e1e1e);color:var(--text,#fafafa)}',
    '.aemo-nav-close{position:absolute;top:14px;right:10px}',
    '.aemo-nav-close svg,.aemo-topbar button svg{width:18px;height:18px}',
    '.aemo-topbar{display:none;align-items:center;gap:8px;height:48px;padding:0 8px;background:var(--bg,#0a0a0a);border-bottom:1px solid var(--line-soft,#212121);color:var(--text,#fafafa)}',
    '.aemo-topbar .aemo-badge{width:26px;height:26px;border-radius:7px;font-size:11px}',
    '.aemo-topbar-title{font-size:14px;font-weight:600;color:var(--text,#fafafa);text-decoration:none}',
    '.aemo-topbar-page{min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-size:13px;color:var(--faint,#898989)}',
    '.aemo-scrim{display:none}',
    '@media ' + DESKTOP + '{html.aemo-nav-on body{padding-left:var(--aemo-nav-w)}.aemo-nav-close{display:none}}',
    '@media not all and ' + DESKTOP + '{',
    '  .aemo-topbar{display:flex}',
    '  .aemo-sidebar{width:min(280px,86vw);transform:translateX(-100%);visibility:hidden;transition:transform .2s ease,visibility 0s .2s;box-shadow:var(--shadow-pop,0 16px 48px -12px rgba(0,0,0,.7))}',
    '  html.aemo-nav-open .aemo-sidebar{transform:none;visibility:visible;transition:transform .2s ease}',
    '  html.aemo-nav-open .aemo-scrim{display:block;position:fixed;inset:0;z-index:59;background:var(--scrim,rgba(0,0,0,.6))}',
    '  html.aemo-nav-open,html.aemo-nav-open body{overflow:hidden}',
    '}',
    '@media (prefers-reduced-motion: reduce){.aemo-sidebar,.aemo-nav-link{transition:none!important}}',
    '@media print{.aemo-sidebar,.aemo-topbar,.aemo-scrim{display:none!important}html.aemo-nav-on body{padding-left:0!important}}'
  ].join('\n');

  // Reserve the space now (this runs in <head>, before the body paints).
  var root = document.documentElement;
  root.classList.add('aemo-nav-on');
  var style = document.createElement('style');
  style.id = 'aemo-nav-style';
  style.textContent = CSS;
  (document.head || root).appendChild(style);

  var current = currentKey();

  function linkHtml(href, label, iconName, isCurrent) {
    return '<li><a class="aemo-nav-link" href="' + href + '"' + (isCurrent ? ' aria-current="page"' : '') + '>' +
      icon(iconName) + '<span>' + label + '</span></a></li>';
  }

  function build() {
    if (document.getElementById('aemo-sidebar')) return;
    var currentLabel = 'Overview';
    var html = '<a class="aemo-brand" href="' + HOME + '"><span class="aemo-badge">AE</span>' +
      '<span><span class="aemo-brand-name">AEMO Dashboards</span><span class="aemo-brand-sub">NEM market data</span></span></a>' +
      '<button type="button" class="aemo-nav-close" aria-label="Close menu">' + icon('close', '') + '</button>' +
      '<ul class="aemo-nav-list">' + linkHtml(HOME, 'Overview', 'home', current === 'home') + '</ul>';
    DASHBOARDS.forEach(function (sec, n) {
      html += '<div class="aemo-nav-section" id="aemo-nav-sec-' + n + '">' + sec.section + '</div>' +
        '<ul class="aemo-nav-list" aria-labelledby="aemo-nav-sec-' + n + '">';
      sec.items.forEach(function (it) {
        if (it.key === current) currentLabel = it.label;
        html += linkHtml(hrefOf(it), it.label, it.icon, it.key === current);
      });
      html += '</ul>';
    });
    html += '<div class="aemo-nav-foot">Built from AEMO’s public data.</div>';

    var aside = document.createElement('nav');
    aside.id = 'aemo-sidebar';
    aside.className = 'aemo-sidebar';
    aside.setAttribute('aria-label', 'AEMO dashboards');
    aside.innerHTML = html;

    var bar = document.createElement('div');
    bar.className = 'aemo-topbar';
    bar.innerHTML = '<button type="button" aria-label="Open menu" aria-controls="aemo-sidebar" aria-expanded="false">' +
      icon('menu', '') + '</button><span class="aemo-badge" aria-hidden="true">AE</span>' +
      '<a class="aemo-topbar-title" href="' + HOME + '">AEMO Dashboards</a>' +
      (current && current !== 'home' ? '<span class="aemo-topbar-page">/ ' + currentLabel + '</span>' : '');

    var scrim = document.createElement('div');
    scrim.className = 'aemo-scrim';

    var body = document.body;
    body.insertBefore(scrim, body.firstChild);
    body.insertBefore(aside, body.firstChild);
    body.insertBefore(bar, body.firstChild);

    var openBtn = bar.querySelector('button');
    var closeBtn = aside.querySelector('.aemo-nav-close');
    var mq = window.matchMedia(DESKTOP);

    function setOpen(open) {
      root.classList.toggle('aemo-nav-open', open);
      openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) (aside.querySelector('[aria-current=page]') || aside.querySelector('a')).focus();
      else if (aside.contains(document.activeElement)) openBtn.focus();
    }
    openBtn.addEventListener('click', function () { setOpen(true); });
    closeBtn.addEventListener('click', function () { setOpen(false); });
    scrim.addEventListener('click', function () { setOpen(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && root.classList.contains('aemo-nav-open')) setOpen(false);
    });
    var onChange = function () { if (mq.matches) root.classList.remove('aemo-nav-open'); };
    if (mq.addEventListener) mq.addEventListener('change', onChange); else mq.addListener(onChange);
  }

  window.AEMO_NAV = { dashboards: DASHBOARDS, home: HOME, href: hrefOf, icon: icon, current: current };

  if (document.body && document.readyState !== 'loading') build();
  else document.addEventListener('DOMContentLoaded', build);
})();
