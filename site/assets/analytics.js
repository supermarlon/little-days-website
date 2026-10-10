/* Explicit opt-in only. Direct event API, no SDK, cookies, replay or person profiles. */
(() => {
  'use strict';
  const token = 'phc_rrrcneX867ztouJFhAKFh2zQCT6ap7jutgLHNApSgakn'; // Public write-only project token.
  const endpoint = 'https://eu.i.posthog.com/i/v0/e/';
  const consentKey = 'little-days-statistics';
  const allowed = new Set(['explore', 'contact', 'resource', 'download']);
  const aiHosts = new Set(['chatgpt.com', 'chat.openai.com', 'perplexity.ai', 'claude.ai', 'gemini.google.com', 'copilot.microsoft.com']);
  let consent = false;
  let pageviewSent = false;
  let ephemeralId = null;
  try { consent = localStorage.getItem(consentKey) === 'yes'; } catch { /* Deny by default. */ }
  function referrerCategory() {
    try {
      const host = new URL(document.referrer).hostname;
      if (aiHosts.has(host)) return 'ai';
      if (host === location.hostname) return 'internal';
      if (/(^|\.)(google\.[a-z.]+|bing\.com)$/.test(host)) return 'search';
      return 'other';
    } catch { return 'direct_or_unavailable'; }
  }
  function send(name) {
    if (!consent || location.hostname !== 'supermarlon.github.io') return;
    if (name !== 'pageview' && !allowed.has(name)) return;
    ephemeralId ||= crypto.randomUUID(); // New per page; no stable user identity.
    const paths = new Set(['/little-days-website/', '/little-days-website/index.html', '/little-days-website/ressourcen.html', '/little-days-website/baby-tagebuch.html', '/little-days-website/betreuungsuebergabe.html', '/little-days-website/presse.html', '/little-days-website/impressum.html', '/little-days-website/datenschutz.html']);
    const pagePath = paths.has(location.pathname) ? location.pathname : 'unknown';
    const channels = new Set(['linkedin', 'instagram', 'eltern', 'producthunt', 'partner']);
    const candidate = new URLSearchParams(location.search).get('utm_source');
    const campaignSource = channels.has(candidate) ? candidate : 'unattributed';
    const payload = { api_key: token, event: 'ld_' + name, distinct_id: ephemeralId, properties: {
      site: 'little-days-marketing', page: pagePath,
      referrer_category: referrerCategory(), campaign_source: campaignSource, $process_person_profile: false,
      $geoip_disable: true, $ip: null
    }};
    fetch(endpoint, { method: 'POST', body: JSON.stringify(payload),
      headers: { 'Content-Type': 'application/json' }, credentials: 'omit',
      referrerPolicy: 'no-referrer', keepalive: true }).catch(() => {});
  }
  function pageview() { if (consent && !pageviewSent) { pageviewSent = true; send('pageview'); } }
  function update() {
    const status = document.getElementById('statistics-status');
    if (status) status.textContent = consent ? 'Freiwillige Statistik ist aktiviert.' : 'Freiwillige Statistik ist deaktiviert.';
    for (const button of document.querySelectorAll('[data-consent]')) {
      const selected = (button.dataset.consent === 'yes') === consent;
      button.setAttribute('aria-pressed', String(selected));
    }
  }
  document.addEventListener('click', (event) => {
    const choice = event.target.closest?.('[data-consent]');
    if (choice) {
      consent = choice.dataset.consent === 'yes';
      try { localStorage.setItem(consentKey, consent ? 'yes' : 'no'); } catch { /* Choice lasts only on this page. */ }
      if (!consent) ephemeralId = null;
      update(); pageview(); return;
    }
    const element = event.target.closest?.('[data-event]');
    const name = element?.dataset.event;
    if (allowed.has(name)) send(name);
  });
  update(); pageview();
})();
