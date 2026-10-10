// Actual privacy boundary tests with a browser-independent DOM and fetch harness.
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('site/assets/analytics.js', 'utf8');
function harness(stored = null, denyStorage = false) {
  const requests = []; const handlers = {}; let storage = stored;
  const context = { URL, URLSearchParams, Set, String,
    crypto: { randomUUID: () => 'ephemeral-test-id' },
    location: { pathname: '/little-days-website/', hostname: 'supermarlon.github.io', search: '?email=private@example.com&utm_source=private@example.com', hash: '#baby-secret' },
    localStorage: { getItem() { if(denyStorage)throw Error(); return storage; }, setItem(k,v) { if(denyStorage)throw Error(); storage = v; } },
    fetch(url, options) { requests.push({url, options, payload: JSON.parse(options.body)}); return Promise.resolve({ok:true}); },
    document: { referrer: 'https://chatgpt.com/c/private-conversation?secret=value',
      getElementById: () => null, querySelectorAll: () => [], addEventListener: (name, cb) => handlers[name] = cb },
  };
  vm.runInNewContext(source, context);
  return { requests, context, click(dataset) { handlers.click({ target: {closest: selector => selector === '[data-consent]' ? (dataset.consent ? {dataset} : null) : {dataset} } }); } };
}
const h = harness(); assert.equal(h.requests.length,0,'No traffic before consent');
h.click({event:'contact'}); assert.equal(h.requests.length,0,'No click data without consent');
h.click({consent:'yes'}); assert.equal(h.requests.length,1,'Exactly one pageview after consent');
h.click({event:'contact'}); assert.equal(h.requests.length,2);
const serial = JSON.stringify(h.requests);
assert(!serial.includes('private@example.com'));assert(!serial.includes('private-conversation'));assert(!serial.includes('baby-secret'));
assert.equal(h.requests[0].options.credentials,'omit');assert.equal(h.requests[0].options.referrerPolicy,'no-referrer');
assert.equal(h.requests[0].payload.properties.$process_person_profile,false);
assert.equal(h.requests[0].payload.properties.referrer_category,'ai');
h.click({event:'baby_weight'});assert.equal(h.requests.length,2,'Non-allowlisted events blocked');
h.click({consent:'no'});h.click({event:'contact'});assert.equal(h.requests.length,2,'Withdraw immediately stops future traffic');
assert.equal(harness('no',true).requests.length,0,'Storage failures deny measurement');
assert.equal(harness('yes').requests.length,1,'Saved consent enables pageview');
const local = harness();local.context.location.hostname = 'localhost';local.click({consent:'yes'});assert.equal(local.requests.length,0,'Local preview must not pollute production analytics');
console.log('PASS: consent, withdrawal, event allowlist and no URL/contact/referrer leakage');
