# AEMO Dashboards

**[cutout-z.github.io/aemo-dashboards](https://cutout-z.github.io/aemo-dashboards/)**

The home page and shared sidebar for five dashboards on Australia's National Electricity Market (NEM),
each built from AEMO's public data:

| Dashboard | Repository |
|---|---|
| [Historical Prices](https://cutout-z.github.io/aemo-historical-prices/) | [aemo-historical-prices](https://github.com/cutout-z/aemo-historical-prices) |
| [Negative Prices](https://cutout-z.github.io/aemo-negative-prices/) | [aemo-negative-prices](https://github.com/cutout-z/aemo-negative-prices) |
| [Generator Credit](https://cutout-z.github.io/aemo-generator-credit-dashboard/) | [aemo-generator-credit-dashboard](https://github.com/cutout-z/aemo-generator-credit-dashboard) |
| [Renewable Generators](https://cutout-z.github.io/aemo-renewable-generator-dashboard/) | [aemo-renewable-generator-dashboard](https://github.com/cutout-z/aemo-renewable-generator-dashboard) |
| [MLF Tracker](https://cutout-z.github.io/aemo-mlf-tracker/) | [aemo-mlf-tracker](https://github.com/cutout-z/aemo-mlf-tracker) |

Each dashboard keeps its own repository, data pipeline and schedule. This repository holds only:

- `nav.js`: the sidebar every dashboard loads. On wide screens it is a fixed left column; below
  1024px it is a top bar with a menu drawer. It injects its own CSS and uses each page's colour
  tokens, so it follows the page's light or dark theme.
- `index.html`: the home page, which lists the dashboards from the same list `nav.js` uses.

## Adding the sidebar to a dashboard

Put this at the end of the page's `<head>`, with `data-current` set to the page's key in `nav.js`:

```html
<script src="https://cutout-z.github.io/aemo-dashboards/nav.js" data-current="mlf-tracker"></script>
```

Load it plainly (not `defer` or `async`): it reserves the sidebar's width before the page's first
paint, so charts size themselves correctly. If the script fails to load, the page works as before,
just without the sidebar.

## Adding or renaming a dashboard

Edit `DASHBOARDS` in `nav.js`. The sidebar on every page and the home page both update on the next
deploy, because they all read this one file.

## Local preview

```bash
python3 -m http.server 9390 --bind 127.0.0.1
```

Then open http://127.0.0.1:9390/. Sidebar links point at the live sites.
