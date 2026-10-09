# Repo contract — AEMO Dashboards (`cutout-z/aemo-dashboards`)

Read this before touching anything. This repo is the home page and the shared sidebar for the five
AEMO dashboards; it holds no data and no pipeline. The family conventions below are generated from
the `agent-contracts` repo; where this file's repo-specific rules are stricter, they win.

<!-- BEGIN agent-contracts:family -->
<!-- source: family/AGENTS.family.md sha256:116b1391e2bb — edit in cutout-z/agent-contracts, not here -->
## Family conventions (every repo, every agent)

*Generated from `agent-contracts/family/AGENTS.family.md`. Edit it there, never here: a drift check
reports any local edit.* These apply to every agent (Hermes, Claude Code, Codex or any other),
whatever app drives it. Where this repo's own rules (above or below this block) are stricter, they
win. Machine-specific conventions (which checkout is which, the lane runtime, where memory lives)
are in the owner's private contract, which reaches agents through their user-level instructions
where a harness supports it.

### Branches, concurrency, cleanup

- Work in a working clone, on a branch, never in a live or serving checkout: a live checkout is what
  serves or publishes, so an edit there goes out unreviewed. Merge to `main` only if this repo's
  contract says the agent may; otherwise push the branch and hand back for review.
- Other agents may be working in this repo right now. Fetch before you act. If a branch moved
  unexpectedly, or files you didn't touch changed, stop and report rather than reconcile.
- Use a worktree for parallel work, not a second clone. The exception is a live checkout: use a
  separate clone, because adding a worktree writes into the live checkout's `.git`. At session end,
  remove the worktrees you created and leave each checkout on the branch it was on when you arrived:
  a leftover worktree pins its branch, and a checkout left on your branch changes what the next
  agent, or a server running from it, sees.
- Push every branch you want kept. An unpushed branch is one disk failure from gone.

### Instructions and automation

- **`AGENTS.md` is the only instruction file.** `CLAUDE.md`, or any other harness-specific file, holds
  just a comment line and `@AGENTS.md`. Other harnesses never read those files, so a rule or fact put
  there reaches only one agent.
- **Nothing you depend on lives only in one harness or app.** Hooks, slash commands, plugins, app
  quick actions and app-scheduled tasks may speed things up. The only copy of any automation or rule
  goes in this repo (scripts, `AGENTS.md`) or the owner's scheduler, because the harness or app may be
  swapped.
- **Name the tier, not the model.** Briefs, skills and procedures say a tier and an effort (tier 0
  mechanical, 1 routine, 2 standard, 3 hard or review, 4 vision); `agent-contracts/tiers.yaml` maps
  each tier to a model per harness. Models change often, so a name in a skill goes stale.
- **A fact other agents need goes where they load it**: this repo's `AGENTS.md` Facts, with source
  and date. If it applies across repos, propose it for the shared facts block in your handback. Your
  own memory or skills are invisible to the other agents.

### What needs the owner's yes

An explicit instruction from the owner in the current session covers that action only, not similar
later ones: the yes was for what the owner saw, not for what follows. A repo contract may record a
standing permission from the owner (e.g. "the agent merges to `main` once `check.sh` is green"). It
counts as the owner's yes only for the actions and the agents it names, only in the repo whose
contract records it, and only as that text stands on `origin/main` when you start. It never covers
adding, widening or rewording a standing permission, or any change to `AGENTS.md` or this block:
those always need the owner's yes in the current session. Without either, declare these and wait
for a yes:

- **Publishing**: anything that changes what other people can see (`main` on a published repo,
  Pages, public data files).
- **Data and ETL**: data files, pipeline code, data contracts (columns, keys, paths, schemas).
  Lanes, dashboards and other repos read them, and a change breaks them silently.
- **The instruments**: `check.sh`, guard tests, audit and verify scripts. They are how anyone,
  including you, knows a change works. Never weaken one to make something pass. If one is wrong,
  say so and leave it.
- **Infra**: ports, scheduled jobs, servers, publish pipelines. Other jobs, and the owner, rely on
  them running as they are.
- **Another agent's state**: another agent's memory, config or notes. With the owner's yes any agent
  may change them; no agent is the only writer. The owning agent can't see your edit, so commit it
  where it's visible, and edit the source rather than a generated copy.

Never read, quote or commit secrets (`.env`, auth files, keys, tokens): repos, transcripts and
handback notes get copied and published.

### Verification standard

- A change is done when you have seen the evidence yourself: tests run (exact counts, failures
  named, pre-existing failures shown to exist on `main`), and for UI, a real browser render, or a
  plain statement that it wasn't rendered and why. A reviewer can check evidence, not belief.
- For a fix, show its test fails with the fix reverted and passes with it applied; otherwise nothing
  shows the test exercises the fix.
- Don't relay another agent's or subagent's numbers. Re-run or read the evidence yourself: a relayed
  number can't be traced, and you are the one signing the handback.

### Attribution and handback

- **Every commit names its agent** in a trailer, so audits and the owner's digest can tell which agent
  made each change, whatever app drove it: `Co-Authored-By: <Agent> <model> <email>`, e.g.
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. `<Agent>` is one word (`Claude`,
  `Codex`, `Hermes`, …); `<model>` is the model name without a provider prefix (e.g. `Opus 5.5`,
  `deepseek-v4.1-flash`). The email goes in angle brackets: Claude `noreply@anthropic.com`, Hermes
  `noreply@nousresearch.com` (as in existing commits), any other agent `<agent>@agents.invalid`.
  Audits match the key case-insensitively and the first word of the value.
- **Commit with the repo's configured identity.** Never set or override `user.name` or `user.email`,
  and never pass `--author`: on a public repo, author fields are published.
- **End every piece of work with a handback note.** It is the durable record; app session lists and
  an agent's memory are not, and both may be swapped. Use the repo's own path and branch convention
  if it has one; it wins, including whether notes merge. Otherwise use
  `handbacks/<YYYY-MM-DD>-<topic>.md`. On a repo whose `main` is published (a public repo, or one that
  deploys or builds a site from `main`), commit the note on its own branch, `handback/<your-branch>`:
  push it, and never merge or delete it, so the record survives the work branch's merge without
  landing on `main`. On a public repo every pushed branch is public too, so keep notes there free of
  private details. The frontmatter goes above the first line of any repo template:

  ```yaml
  ---
  project: <project name as on the owner's dashboard>
  agent: <the trailer's Agent, lowercase: claude, codex, hermes, …>
  branch: <branch>
  merged: false
  status: <one line>
  outstanding:
    - "to-do [mac-local] <item>"   # [mac-local] = only actionable on the owner's Mac
  ---
  ```

  Then cover what changed, the evidence, what's left, and any decision the brief didn't cover.
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
