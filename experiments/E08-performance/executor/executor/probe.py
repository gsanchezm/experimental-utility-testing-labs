"""E08-performance executor: the in-page measurement script (one instrument and one script for every condition).

DRAFT (operation OP-PREP-E08). The script is injected into every document of a load before any page script runs (Playwright
add_init_script). It reads only the browser's own Performance APIs (design brief, section 4): Largest Contentful Paint, Layout Instability,
Long Tasks, Paint and Resource Timing entries, plus the time at which the first element matching a selector is attached to the document
(a MutationObserver). It changes nothing in the page, sets no state, and sends nothing. All times are performance.now() of the document
of the load, in milliseconds (the time origin is the start of the navigation). The snapshot is raw: every entry is kept; the metrics are
computed afterwards in classify.py from the saved snapshot, so a later reader can recompute them from the evidence file.
"""
import json

PROBE_VERSION = 'e08-probe-v1'

PROBE_JS = r"""
(() => {
  if (window.__e08) { return; }
  const cfg = window.__e08_config || { watch: {} };
  const S = { probe_version: 'e08-probe-v1', time_origin: performance.timeOrigin, supported: [], errors: [], ready: {}, lcp: [], cls: [], longtasks: [], paints: [] };
  window.__e08 = S;
  const observers = [];
  try { S.supported = Array.from(PerformanceObserver.supportedEntryTypes || []); } catch (e) { S.errors.push('supportedEntryTypes: ' + e.name); }
  const desc = (n) => {
    try {
      if (!n) { return null; }
      if (n.nodeType !== 1) { return String(n.nodeName); }
      const id = n.id ? '#' + n.id : '';
      const cls = (typeof n.className === 'string' && n.className.trim()) ? '.' + n.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
      return n.tagName.toLowerCase() + id + cls;
    } catch (e) { return null; }
  };
  const rect = (r) => (r ? { x: r.x, y: r.y, width: r.width, height: r.height } : null);
  const observe = (type, handler) => {
    try {
      const o = new PerformanceObserver((list) => { for (const e of list.getEntries()) { handler(e); } });
      o.observe({ type, buffered: true });
      observers.push({ o, handler });
    } catch (e) { S.errors.push(type + ': ' + e.name); }
  };
  observe('largest-contentful-paint', (e) => S.lcp.push({
    start_time: e.startTime, render_time: e.renderTime, load_time: e.loadTime, size: e.size, id: e.id, url: e.url, element: desc(e.element) }));
  observe('layout-shift', (e) => S.cls.push({
    start_time: e.startTime, value: e.value, had_recent_input: e.hadRecentInput,
    sources: Array.from(e.sources || []).map((s) => ({ node: desc(s.node), node_id: (s.node && s.node.id) || null,
                                                       previous_rect: rect(s.previousRect), current_rect: rect(s.currentRect) })) }));
  observe('longtask', (e) => S.longtasks.push({ start_time: e.startTime, duration: e.duration, name: e.name }));
  observe('paint', (e) => S.paints.push({ name: e.name, start_time: e.startTime }));
  const watchers = Object.entries(cfg.watch || {});
  const check = () => {
    for (const [key, selector] of watchers) {
      if (S.ready[key] === undefined) {
        try { if (document.querySelector(selector)) { S.ready[key] = performance.now(); } } catch (e) { S.errors.push('watch ' + key + ': ' + e.name); S.ready[key] = null; }
      }
    }
  };
  check();
  try {
    const mo = new MutationObserver(() => { check(); });
    mo.observe(document, { childList: true, subtree: true });
  } catch (e) { S.errors.push('MutationObserver: ' + e.name); }
  window.__e08_flush = () => {
    for (const { o, handler } of observers) { for (const e of o.takeRecords()) { handler(e); } }
    check();
    const nav = performance.getEntriesByType('navigation')[0];
    S.navigation = nav ? { start_time: nav.startTime, response_start: nav.responseStart, dom_content_loaded: nav.domContentLoadedEventEnd,
                           load_event_end: nav.loadEventEnd, type: nav.type } : null;
    S.resources = performance.getEntriesByType('resource').map((r) => ({ name: r.name, initiator_type: r.initiatorType, start_time: r.startTime,
      response_end: r.responseEnd, duration: r.duration, transfer_size: r.transferSize, response_status: r.responseStatus === undefined ? null : r.responseStatus }));
    S.now = performance.now();
    return S;
  };
})();
"""


def init_script(watch):
    """The init script of one load: the watch selectors (key -> CSS selector) in a config object, then the probe."""
    return 'window.__e08_config = ' + json.dumps({'watch': watch}, sort_keys=True) + ';\n' + PROBE_JS


FLUSH_JS = '() => window.__e08_flush ? window.__e08_flush() : null'
