# Little Days · Marketing website & agent loop

Live: https://supermarlon.github.io/little-days-website/

Static mobile-first German site, GitHub Pages, no framework or backend.
Product: https://github.com/supermarlon/little-days . Copy describes development, not a confirmed launch.

## What is now implemented

- Landing page, semantic HTML, canonical/OpenGraph/FAQ data, legal pages and sitemap.
- Public resource hub, baby-journal template and caregiver-handover checklist with direct text downloads.
- Supplied Google Search Console verification tag. Property verified and sitemap submitted;
  initial Google fetch still reported a read error. HTTP delivery is independently valid.
- Optional PostHog EU measurement (project 300977), strictly after active visitor consent.
  Direct allowlisted events, no SDK, replay, person profiles or persistent visitor identity.
- Daily Actions: restore previous state, fetch aggregate provider data when authorized,
  check freshness and experiment windows, audit live pages, save report/history as artifacts.
- IndexNow: notify changed indexable pages after successful deployments. Receipt is not indexing.
- Local Codex operating prompt, distribution queue, first outreach/social/launch drafts and 30-day plan.
- Optional paid Codex API strategy is off. Local scheduled Codex uses the existing account.

## Run

```sh
python3 -m http.server 8080 --directory site
python3 scripts/check.py
python3 -m unittest discover -s tests -v
node tests/analytics.cjs
python3 scripts/marketing/loop.py
```

Pushes to main deploy after checks. Changes should normally use a PR.
Full operating guide: [docs/marketing-loop.md](docs/marketing-loop.md).
Agent instructions: [docs/local-agent-prompt.md](docs/local-agent-prompt.md).
Drafts: [optimization/distribution/drafts.md](optimization/distribution/drafts.md).

## Connections: no invented readiness

Ingestion uses the public write-only PostHog project token. Daily API reads require
POSTHOG_READ_KEY (Query:Read, restricted to project 300977) as an Actions secret.
A prepared key is not an activated connection. No secret is committed or printed.

Search Console API optionally uses GSC_ACCESS_TOKEN or refresh-token credentials
GSC_REFRESH_TOKEN, GSC_CLIENT_ID, GSC_CLIENT_SECRET as Actions secrets. OAuth permission
must be explicitly granted; a verified website alone does not authorize the API.
Local runs can record actually observed provider totals in ignored work/provider-snapshots.json.
GEO observations live privately in work/geo-observations.json. No paid tracker is connected.

The API-backed Codex job requires OPENAI_API_KEY and ENABLE_CODEX_STRATEGY=true.
Leave off for minimum cost. It consumes API usage, not a ChatGPT-subscription API allowance.
Reference: https://developers.openai.com/codex/github-action .

## Operations and limits

Actions run daily at 05:23 UTC (06:23 CET / 07:23 CEST). Scheduler delays are possible.
Local Codex requires the computer and app to be available and uses account quotas.
Private work/ and artifacts hold 90 observations; artifacts expire after 30 days. A gap
longer than retention loses historical state; a durable private store can be added later.
Missing/stale data stays missing/stale, never zero. Only one experiment at a time,
minimum 28-day window, no causal winner inferred from sparse pre/post event counts.
Contacts measure clicks, not sent emails; downloads measure clicks, not app installs.

No paid upgrade, ad campaign, email broadcast or external social publication is enabled.
External drafts need concrete recipient/channel authorization before sending.
No automatic medical content, invented ratings, store availability or launch claims.
The existing app's public readiness must be confirmed before advertising a download.

Project robots.txt is a published file, but robots policy belongs at the host root.
Use a custom domain or the root Pages repository for host-wide crawler control.
Update canonical, sitemap, OpenGraph and IndexNow config together when moving domains.
Actions are pinned to commits; update pins deliberately. Current pinned Pages actions
are successful, with GitHub's Node-runtime migration warnings where applicable.
