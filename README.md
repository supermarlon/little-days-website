# Little Days · Marketing website

Live: https://supermarlon.github.io/little-days-website/

A static German mobile-first landing page. No build tool, npm dependencies, external fonts,
backend, active analytics or paid service. Only `site/` is deployed. The app is a separate project:
https://github.com/supermarlon/little-days . Product copy describes development, not public availability.

## Run and change

`python3 -m http.server 8080 --directory site` previews locally.
`python3 scripts/check.py` checks local links/anchors, metadata, FAQ consistency and size.
Edit `site/index.html` and `site/assets/style.css`; push to main deploys after checks pass.
GitHub Pages publishing source: GitHub Actions. Canonical URL, sitemap, OpenGraph and
robots must be updated together when attaching a custom domain. Project-level robots.txt
cannot govern the host-wide crawler policy: crawlers request https://supermarlon.github.io/robots.txt.
The sitemap works at the project URL. Add a custom domain or maintain a host-root robots.txt
in the account's root Pages repository if host-wide control is needed.

## Launch information still needed

The supplied operator information, contact email and confirmed managing director Marlon Rüscher
are included. The notices describe this marketing website only; app privacy terms and the
final store/production information must be supplied separately before an app launch.
No bank details or personal tax number are stored. No app URL, release date, pricing or app-store
listing was supplied; the contact CTA is intentionally usable email feedback, not a fake download.

## Analytics connection

`site/assets/analytics.js` emits only `explore` and `contact` events in the browser, without
transmitting or storing anything. A reviewed adapter can set `window.littleDaysAnalytics`
before this script or listen to `little-days:event`. Add required consent and update the privacy
notice before connecting a provider. Never forward child data, emails, free text or query strings.
Start with Google Search Console and Bing Webmaster Tools for search/indexing measurement.
Use URL-prefix verification (HTML file or meta tag supplied by the owner). No accounts are
created or claimed to be connected by this repository. Submit the live sitemap after verification.
Only aggregate, non-personal exports belong in optimization/data/metrics.json; raw data stays private.

## Daily optimization foundation

Daily at 05:23 UTC (06:23 CET / 07:23 CEST), GitHub Actions checks the live URLs and records
status, payload size, content hashes and missing measurement sources. Reports are kept for
30 days in Actions artifacts. Schedules may be delayed by GitHub. No daily site churn.

Optional hosted Codex strategy is OFF. To opt in, add `OPENAI_API_KEY` as a repository secret
and `ENABLE_CODEX_STRATEGY=true` as an Actions variable. This invokes the OpenAI API and
can incur usage charges; the ChatGPT subscription is not an API-key budget. Set an API project
budget and monitor usage before enabling. The agent has read-only access, a 10-minute timeout,
no posting token and returns one recommendation to a separate job summary. It does not merge
or publish changes. Documentation: https://developers.openai.com/codex/github-action .

Lowest-service alternative: use the existing Codex app on your available laptop with this checkout
and `.github/codex/strategy.md` as a daily automation prompt. Clone/register the repository as a
local project first. Review aggregate evidence, implement one bounded change on a branch,
run checks and open a PR. Keep the experiment record with hypothesis, baseline, metric and
at least 28-day observation window. Do not send outreach or publish external posts without authorization.

Loop: observe → validate data → prioritize one hypothesis → draft a PR → check → review/merge
→ Pages deploy → compare over an observation window → retain or revert.

Initial prompts and experiment register are in optimization/. No GEO tracker is connected.
Missing metrics are null, not zero. Check GEO with the same prompt, locale, engine and search
settings and multiple samples; API replies do not measure ChatGPT's consumer search rankings.
No guarantee of citations or high rankings after 30 days. Distribution ideas should earn useful
mentions through real resources and relevant partnerships, not automated spam.

## Verification boundaries

Automated checks are release safeguards, not a full accessibility, legal or security certification.
Check keyboard focus, 320/375/390 px layouts, reduced motion and the mail link before launch.
GitHub actions are pinned to commit SHAs; update pins deliberately. HTTPS is managed by Pages.
