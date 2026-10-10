/* Disabled by default: no network requests, cookies or storage.
   Connect a reviewed provider by assigning window.littleDaysAnalytics before this script.
   Allowlisted event names only. Never forward text, child records, URL queries or emails. */
(() => {
  const allowed = new Set(['explore', 'contact']);
  document.addEventListener('click', (event) => {
    const element = event.target.closest?.('[data-event]');
    const name = element?.dataset.event;
    if (!allowed.has(name)) return;
    const detail = Object.freeze({ name });
    window.dispatchEvent(new CustomEvent('little-days:event', { detail }));
    if (typeof window.littleDaysAnalytics === 'function') {
      try { window.littleDaysAnalytics(detail); } catch { /* Analytics never blocks navigation. */ }
    }
  });
})();
