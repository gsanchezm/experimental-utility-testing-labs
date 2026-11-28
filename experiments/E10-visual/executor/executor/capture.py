"""E10-visual executor: the capture of one view (page setup values, the in-page helper scripts, the screenshot, the boxes read from the DOM).

DRAFT (operation OP-PREP-E10). One capture is: the page's own ready signal; for a timed view, the document clock reaching the target time
(`performance.now()` of the document, whose origin is the start of the navigation); the settle check (fonts ready, every image that
lies wholly or partly inside the viewport complete, the boxes of the expected elements unchanged over two consecutive animation frames); the boxes of the expected elements and the state of their images;
and one viewport screenshot at scroll position 0 with CSS animations fast-forwarded to their end and the caret hidden. The scripts only read
the page (they set no state, send nothing, and leave no global in the page). A capture's size is always the viewport, so two captures are
always comparable; full-page and element-scoped screenshots are not used (conditions-draft.json, capture).

The pure helpers (setup values, selectors, parsing, the timing check) are tested without a browser; the in-page scripts are syntax-checked in
Node.js; the browser behaviour is first observed in the ENVIRONMENT_VERIFICATION DRY_RUN.
"""
import hashlib

from . import classify, compare

CAPTURE_VERSION = 'e10-capture-v1'
VIEWPORT = {'width': 1280, 'height': 800}
BROWSER_LOCALE = 'en-US'
TIMEZONE = 'UTC'
NAV_TIMEOUT_MS = 30000
ACTION_TIMEOUT_MS = 15000
# A timed capture is valid when the document clock read right after the screenshot is at most this long after the target time.
TIMED_CAPTURE_MAX_LAG_MS = 1000
TIMED_WAIT_EXTRA_MS = 20000
SCREENSHOT_OPTIONS = {'type': 'png', 'full_page': False, 'animations': 'disabled', 'caret': 'hide', 'scale': 'css'}

SETTLE_JS = r"""
async ({ frames, timeout_ms, selectors }) => {
  const started = performance.now();
  const deadline = started + timeout_ms;
  const out = { fonts_ready: null, images_complete: null, boxes_stable: false, stable_frames: 0, frames: 0, pending_images: 0, waited_ms: 0 };
  const inView = (el) => {
    const r = el.getBoundingClientRect();
    return r.right > 0 && r.bottom > 0 && r.left < window.innerWidth && r.top < window.innerHeight;
  };
  try {
    if (document.fonts && document.fonts.ready) {
      await Promise.race([document.fonts.ready, new Promise((_, reject) => setTimeout(() => reject(new Error('fonts')), Math.max(0, deadline - performance.now())))]);
    }
    out.fonts_ready = true;
  } catch (e) { out.fonts_ready = false; }
  const pending = () => Array.from(document.images).filter((img) => inView(img) && !img.complete);
  while (pending().length > 0 && performance.now() < deadline) { await new Promise((resolve) => setTimeout(resolve, 50)); }
  out.pending_images = pending().length;
  out.images_complete = out.pending_images === 0;
  // the layout is stable when the boxes of the expected elements are equal over `frames` consecutive frames (a drawer or a banner in a transition is not a state)
  const boxesKey = () => JSON.stringify((selectors || []).map((s) => {
    let nodes = [];
    try { nodes = Array.from(document.querySelectorAll(s)); } catch (e) { nodes = []; }
    return nodes.map((el) => { const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; });
  }));
  let last = boxesKey();
  let same = 0;
  while (performance.now() < deadline) {
    await new Promise((resolve) => requestAnimationFrame(() => resolve()));
    out.frames += 1;
    const now = boxesKey();
    if (now === last) { same += 1; if (same >= frames) { out.boxes_stable = true; break; } } else { same = 0; last = now; }
  }
  out.stable_frames = same;
  out.waited_ms = performance.now() - started;
  return out;
}
"""

ELEMENTS_JS = r"""
(groups) => {
  const imageState = (el) => {
    const img = el.tagName === 'IMG' ? el : el.querySelector('img');
    if (!img) { return null; }
    let host = null;
    try { host = new URL(img.currentSrc || img.src, location.href).host || null; } catch (e) { host = null; }
    return { complete: img.complete, natural_width: img.naturalWidth, natural_height: img.naturalHeight, host: host,
             src: String(img.currentSrc || img.src || '').slice(0, 300), alt: String(img.alt || '').slice(0, 120) };
  };
  const out = {};
  for (const { group, selector } of groups) {
    let nodes = [];
    try { nodes = Array.from(document.querySelectorAll(selector)); } catch (e) { out[group] = { error: e.name, elements: [] }; continue; }
    out[group] = { error: null, elements: nodes.map((el, index) => {
      const r = el.getBoundingClientRect();
      return { index: index, tag: el.tagName.toLowerCase(), box: { x: r.x, y: r.y, w: r.width, h: r.height }, img: imageState(el) };
    }) };
  }
  const conn = navigator.connection;
  return { scroll_x: window.scrollX, scroll_y: window.scrollY, inner_width: window.innerWidth, inner_height: window.innerHeight,
           device_pixel_ratio: window.devicePixelRatio, effective_type: (conn && conn.effectiveType) || null, groups: out };
}
"""

READY_JS = '(selectors) => Object.values(selectors).every((s) => { try { return !!document.querySelector(s); } catch (e) { return false; } })'
PRESENT_JS = '(selectors) => Object.fromEntries(Object.entries(selectors).map(([k, s]) => { try { return [k, !!document.querySelector(s)]; } catch (e) { return [k, false]; } }))'
DOC_TIME_JS = '(ms) => performance.now() >= ms'
NOW_JS = '() => performance.now()'
IN_PAGE_SCRIPTS = {'SETTLE_JS': SETTLE_JS, 'ELEMENTS_JS': ELEMENTS_JS, 'READY_JS': READY_JS, 'PRESENT_JS': PRESENT_JS, 'DOC_TIME_JS': DOC_TIME_JS, 'NOW_JS': NOW_JS}


# ---- pure helpers ------------------------------------------------------------------------------------------------------------------------
def context_options():
    """The options of every fresh browser context (a new context per capture: no cache, storage or cookies carried over)."""
    return {'viewport': dict(VIEWPORT), 'device_scale_factor': 1, 'locale': BROWSER_LOCALE, 'timezone_id': TIMEZONE, 'reduced_motion': 'reduce'}


def ready_selectors(view):
    return {k: view['ready'][k] for k in view['required_ready']}


def elements_request(view):
    return [{'group': e['group'], 'selector': e['selector']} for e in view['expected_elements']]


def settle_argument(cfg, view=None):
    """The argument of SETTLE_JS: the frames, the timeout and the selectors whose boxes must stop moving (the expected elements of the view)."""
    s = cfg['capture']['settle']
    return {'frames': s['animation_frames'], 'timeout_ms': s['timeout_ms'], 'selectors': [e['selector'] for e in (view or {}).get('expected_elements', [])]}


def timed_capture_ok(target_ms, after_ms):
    """None for an untimed capture; otherwise True when the document clock after the screenshot is within the permitted lag of the target."""
    if target_ms is None:
        return None
    return after_ms is not None and target_ms <= after_ms <= target_ms + TIMED_CAPTURE_MAX_LAG_MS


def parse_elements(raw, width, height):
    """The raw result of ELEMENTS_JS with `wholly_inside` added to every element, in the shape the rule reads."""
    groups = {}
    for name, g in (raw.get('groups') or {}).items():
        groups[name] = {'error': g.get('error'), 'elements': [{**e, 'wholly_inside': classify.wholly_inside(e['box'], width, height)} for e in g.get('elements') or []]}
    return {**{k: v for k, v in raw.items() if k != 'groups'}, 'groups': groups}


def run_steps(page, steps, timeout_ms=ACTION_TIMEOUT_MS):
    """The view's steps (a click, or a wait until an element is visible), in order; each with an explicit timeout and no retry."""
    done = []
    for step in steps or []:
        loc = page.locator(step['selector']).first
        if step['action'] == 'click':
            loc.click(timeout=timeout_ms)
        elif step['action'] == 'wait_visible':
            loc.wait_for(state='visible', timeout=timeout_ms)
        else:
            raise ValueError(f'unknown step action {step["action"]!r}')
        done.append({'action': step['action'], 'selector': step['selector']})
    return done


def _timeout_error():
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        return PlaywrightTimeout
    except ImportError:  # the static tests run without Playwright
        return TimeoutError


def capture_page(page, view, role, cfg, timeout_error=None):
    """The capture of one view in its page, already navigated (and with the view's steps done). Returns the capture record; the PNG bytes are
    in record['png'] (the caller writes them as evidence and drops the key from the JSON record)."""
    timeout_error = timeout_error or _timeout_error()
    size = cfg['capture']['viewport']
    rec = {'view_id': view['view_id'], 'role': role, 'capture_version': CAPTURE_VERSION, 'ready_ok': False, 'missing_ready': [], 'capture_at_ms': None,
           'doc_time_after_ms': None, 'timed_ok': None, 'settle': None, 'elements': None, 'png': None, 'png_sha256': None, 'png_size': None}
    selectors = ready_selectors(view)
    try:
        page.wait_for_function(READY_JS, arg=selectors, timeout=view['ready_timeout_ms'])
        rec['ready_ok'] = True
    except timeout_error:
        present = page.evaluate(PRESENT_JS, selectors)
        rec['missing_ready'] = sorted(k for k, ok in present.items() if not ok)
        rec['ready_ok'] = False
    at = (view.get('capture_at_ms') or {}).get(role)
    rec['capture_at_ms'] = at
    if rec['ready_ok'] and at is not None:
        page.wait_for_function(DOC_TIME_JS, arg=at, timeout=at + TIMED_WAIT_EXTRA_MS)
    rec['settle'] = page.evaluate(SETTLE_JS, settle_argument(cfg, view))
    raw = page.evaluate(ELEMENTS_JS, elements_request(view))
    rec['elements'] = parse_elements(raw, size['width'], size['height'])
    png = page.screenshot(**SCREENSHOT_OPTIONS)
    rec['doc_time_after_ms'] = page.evaluate(NOW_JS)
    rec['timed_ok'] = timed_capture_ok(at, rec['doc_time_after_ms']) if rec['ready_ok'] else None
    rec['png'] = png
    rec['png_sha256'] = hashlib.sha256(png).hexdigest()
    w, h = compare.png_info(png)[:2]
    rec['png_size'] = [w, h]
    return rec


def record_for_json(rec):
    """The capture record without its PNG bytes (the PNG is its own evidence file)."""
    return {k: v for k, v in rec.items() if k != 'png'}
