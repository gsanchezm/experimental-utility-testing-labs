"""The capture helpers: setup values, selectors, parsing, the timing check, the order of the calls of one capture (with a fake page), and the
in-page scripts (syntax in Node.js, behaviour against a mock of the DOM) (operation OP-PREP-E10).

Static tests: there is no browser here; the first real evidence of the scripts and of the screenshot settings in Chromium is the
ENVIRONMENT_VERIFICATION DRY_RUN."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import capture, compare, config  # noqa: E402

NODE = shutil.which('node')
CFG = config.load()
PNG = compare.encode_png_rgba(4, 3, bytes(range(48)))


class FakeLocator:
    def __init__(self, page, selector):
        self.page, self.selector = page, selector

    @property
    def first(self):
        return self

    def click(self, timeout=None):
        self.page.calls.append(('click', self.selector, timeout))

    def wait_for(self, state=None, timeout=None):
        self.page.calls.append(('wait_for', self.selector, state, timeout))


class FakePage:
    """Records the calls of one capture and answers them with prepared values."""

    def __init__(self, ready=True, now_after=2100.0, elements=None):
        self.calls = []
        self.ready = ready
        self.now_after = now_after
        self.elements = elements or {'scroll_x': 0, 'scroll_y': 0, 'inner_width': 1280, 'inner_height': 900, 'device_pixel_ratio': 1,
                                     'effective_type': '4g', 'groups': {'shift_target': {'error': None, 'elements': [
                                         {'index': 0, 'tag': 'div', 'box': {'x': 40, 'y': 200, 'w': 700, 'h': 320}, 'img': None}]}}}

    def wait_for_function(self, expression, arg=None, timeout=None):
        self.calls.append(('wait_for_function', expression.split(' ')[0] if expression else '', arg, timeout))
        if expression == capture.READY_JS and not self.ready:
            raise TimeoutError('not ready')

    def evaluate(self, expression, arg=None):
        self.calls.append(('evaluate', {capture.SETTLE_JS: 'SETTLE', capture.ELEMENTS_JS: 'ELEMENTS', capture.NOW_JS: 'NOW',
                                        capture.PRESENT_JS: 'PRESENT'}.get(expression, expression), arg))
        if expression == capture.SETTLE_JS:
            return {'fonts_ready': True, 'images_complete': True, 'boxes_stable': True, 'stable_frames': 2, 'frames': 2, 'pending_images': 0, 'waited_ms': 12.0}
        if expression == capture.ELEMENTS_JS:
            return self.elements
        if expression == capture.NOW_JS:
            return self.now_after
        if expression == capture.PRESENT_JS:
            return {k: False for k in arg}
        raise AssertionError(expression)

    def screenshot(self, **kw):
        self.calls.append(('screenshot', kw))
        return PNG

    def locator(self, selector):
        return FakeLocator(self, selector)


class HelperTests(unittest.TestCase):
    def test_the_interface_constant_and_the_settings(self):
        with open(os.path.join(HERE, '..', 'executor', 'capture.py'), encoding='utf-8') as f:
            self.assertRegex(f.read(), r"(?m)^CAPTURE_VERSION = 'e10-capture-v1'$")
        self.assertEqual(capture.context_options(), {'viewport': {'width': 1280, 'height': 900}, 'device_scale_factor': 1, 'locale': 'en-US',
                                                      'timezone_id': 'UTC', 'reduced_motion': 'reduce'})
        self.assertEqual(capture.SCREENSHOT_OPTIONS, {'type': 'png', 'full_page': False, 'animations': 'disabled', 'caret': 'hide', 'scale': 'css'})
        self.assertEqual(CFG['capture']['viewport'], capture.VIEWPORT)

    def test_selectors_and_requests_come_from_the_view(self):
        view = config.condition(CFG, 'E10-SUT02-WEB-VISUAL')['views'][2]
        self.assertEqual(capture.ready_selectors(view), {'inventory_list': '[data-test="inventory-list"]', 'close_icon': '[data-test="close-menu"]'})
        self.assertEqual(capture.elements_request(view), [{'group': 'close_icon', 'selector': '[data-test="close-menu"]'}])
        self.assertEqual(capture.settle_argument(CFG), {'frames': 2, 'timeout_ms': 20000, 'image_timeout_ms': 5000, 'selectors': []})
        self.assertEqual(capture.settle_argument(CFG, view), {'frames': 2, 'timeout_ms': 20000, 'image_timeout_ms': 5000, 'selectors': ['[data-test="close-menu"]']})

    def test_the_timing_check(self):
        self.assertIsNone(capture.timed_capture_ok(None, 123.0))
        self.assertTrue(capture.timed_capture_ok(2000, 2000.0))
        self.assertTrue(capture.timed_capture_ok(2000, 3000.0))
        self.assertFalse(capture.timed_capture_ok(2000, 3000.5))
        self.assertFalse(capture.timed_capture_ok(2000, 1999.0))  # cannot happen after a wait, but a clock that went backwards is not a valid capture
        self.assertFalse(capture.timed_capture_ok(5500, None))

    def test_parse_elements_marks_the_boxes_wholly_inside_the_viewport(self):
        raw = {'scroll_y': 0, 'groups': {'g': {'error': None, 'elements': [{'index': 0, 'box': {'x': 0, 'y': 0, 'w': 1280, 'h': 900}, 'img': None},
                                                                          {'index': 1, 'box': {'x': 0, 'y': 800, 'w': 100, 'h': 101}, 'img': None}]}}}
        out = capture.parse_elements(raw, 1280, 900)
        self.assertEqual([e['wholly_inside'] for e in out['groups']['g']['elements']], [True, False])
        self.assertEqual(out['scroll_y'], 0)

    def test_run_steps_in_order_with_explicit_timeouts(self):
        page = FakePage()
        steps = config.condition(CFG, 'E10-SUT02-WEB-VISUAL')['views'][2]['steps']
        done = capture.run_steps(page, steps)
        self.assertEqual(page.calls, [('click', '#react-burger-menu-btn', capture.ACTION_TIMEOUT_MS),
                                      ('wait_for', '[data-test="close-menu"]', 'visible', capture.ACTION_TIMEOUT_MS)])
        self.assertEqual([d['action'] for d in done], ['click', 'wait_visible'])
        with self.assertRaises(ValueError):
            capture.run_steps(page, [{'action': 'hover', 'selector': 'x'}])
        self.assertEqual(capture.run_steps(page, None), [])


class CapturePageTests(unittest.TestCase):
    def view(self):
        return config.condition(CFG, 'E10-SUT03-WEB-SHIFT')['views'][0]

    def test_the_order_of_the_calls_and_the_record_of_a_timed_capture(self):
        page = FakePage(now_after=2100.0)
        rec = capture.capture_page(page, self.view(), 'A', CFG, timeout_error=TimeoutError)
        kinds = [c[0] if c[0] != 'evaluate' else 'evaluate:' + c[1] for c in page.calls]
        self.assertEqual(kinds, ['wait_for_function', 'wait_for_function', 'evaluate:SETTLE', 'evaluate:ELEMENTS', 'screenshot', 'evaluate:NOW'])
        self.assertEqual(page.calls[0][2], {'content': 'h2[id$="-title"]'})
        self.assertEqual(page.calls[1][2:], (2000, 2000 + capture.TIMED_WAIT_EXTRA_MS))
        self.assertEqual(page.calls[4][1], capture.SCREENSHOT_OPTIONS)
        self.assertTrue(rec['ready_ok'])
        self.assertEqual((rec['capture_at_ms'], rec['timed_ok'], rec['doc_time_after_ms']), (2000, True, 2100.0))
        self.assertEqual((rec['png'], rec['png_sha256'], rec['png_size']), (PNG, hashlib.sha256(PNG).hexdigest(), [4, 3]))
        self.assertTrue(rec['elements']['groups']['shift_target']['elements'][0]['wholly_inside'])
        self.assertEqual(rec['elements']['effective_type'], '4g')
        self.assertNotIn('png', capture.record_for_json(rec))
        json.dumps(capture.record_for_json(rec))

    def test_the_late_capture_uses_its_own_time_and_a_missed_time_is_recorded(self):
        page = FakePage(now_after=5400.0)
        rec = capture.capture_page(page, self.view(), 'B', CFG, timeout_error=TimeoutError)
        self.assertEqual((rec['capture_at_ms'], rec['timed_ok']), (5500, False))  # the clock read right after the screenshot is before the target
        page = FakePage(now_after=7000.0)
        self.assertFalse(capture.capture_page(page, self.view(), 'A2', CFG, timeout_error=TimeoutError)['timed_ok'])  # more than 1 s late

    def test_an_untimed_view_has_no_clock_wait(self):
        page = FakePage()
        view = config.condition(CFG, 'E10-SUT01-WEB-PROBLEM')['views'][0]
        rec = capture.capture_page(page, view, 'A', CFG, timeout_error=TimeoutError)
        self.assertEqual(sum(1 for c in page.calls if c[0] == 'wait_for_function'), 1)
        self.assertIsNone(rec['timed_ok'])

    def test_a_page_that_never_shows_its_content_is_recorded_not_raised(self):
        page = FakePage(ready=False)
        rec = capture.capture_page(page, self.view(), 'A', CFG, timeout_error=TimeoutError)
        self.assertFalse(rec['ready_ok'])
        self.assertEqual(rec['missing_ready'], ['content'])
        self.assertIsNone(rec['timed_ok'])
        self.assertIsNotNone(rec['png'])  # the page is still captured: the screenshot is evidence of what was shown


class ScriptTests(unittest.TestCase):
    @unittest.skipUnless(NODE, 'node is not available')
    def test_every_in_page_script_is_valid_javascript(self):
        tmp = tempfile.mkdtemp(prefix='e10-js-')
        for name, src in capture.IN_PAGE_SCRIPTS.items():
            path = os.path.join(tmp, name + '.js')
            with open(path, 'w', encoding='utf-8') as f:
                f.write('const f = ' + src.strip() + ';\n')
            proc = subprocess.run([NODE, '--check', path], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, f'{name}: {proc.stderr}')

    HARNESS = r"""
const vm = require('vm');
const fs = require('fs');
const scripts = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const mk = (id, rect, img) => ({ tagName: 'DIV', id, getBoundingClientRect: () => rect, querySelector: () => img || null });
const imgEl = (complete, nw, src, rect) => ({ tagName: 'IMG', complete, naturalWidth: nw, naturalHeight: nw, currentSrc: src, src, alt: 'a', getBoundingClientRect: () => rect });
const inside = { left: 0, top: 0, right: 100, bottom: 100, x: 0, y: 0, width: 100, height: 100 };
const outside = { left: 0, top: 900, right: 100, bottom: 1000, x: 0, y: 900, width: 100, height: 100 };
let framesRun = 0;
let mv = 0;
const movingEl = { tagName: 'DIV', getBoundingClientRect: () => ({ x: Math.min(mv++, 6), y: 0, width: 10, height: 10 }), querySelector: () => null };
let mv2 = 0;
const alwaysEl = { tagName: 'DIV', getBoundingClientRect: () => ({ x: mv2++, y: 0, width: 10, height: 10 }), querySelector: () => null };
const images = [imgEl(true, 500, 'https://upload.wikimedia.org/a.jpg', inside), imgEl(false, 0, 'https://broken-image-url.com/404.jpg', inside), imgEl(false, 0, 'https://x/lazy.jpg', outside)];
const doc = {
  fonts: { ready: Promise.resolve() },
  images,
  querySelectorAll: (sel) => { if (sel === 'bad[') { const e = new Error('bad selector'); e.name = 'SyntaxError'; throw e; } if (sel === '.moving') { return [movingEl]; } if (sel === '.always') { return [alwaysEl]; } return sel === '.card' ? [mk('c1', inside, images[0]), mk('c2', outside, null)] : []; },
  querySelector: (sel) => (sel === '#there' ? {} : null),
};
const ctx = { document: doc, window: { scrollX: 0, scrollY: 0, innerWidth: 1280, innerHeight: 900, devicePixelRatio: 1 },
  navigator: { connection: { effectiveType: '4g' } }, location: { href: 'http://127.0.0.1:3000/' }, URL, setTimeout, performance: { now: () => Date.now() },
  requestAnimationFrame: (cb) => { framesRun++; setTimeout(cb, 1); }, Promise, Error };
ctx.window.innerWidth = 1280; ctx.window.innerHeight = 900;
vm.createContext(ctx);
const get = (name) => vm.runInContext('(' + scripts[name] + ')', ctx);
(async () => {
  const out = {};
  out.elements = get('ELEMENTS_JS')([{ group: 'card', selector: '.card' }, { group: 'bad', selector: 'bad[' }, { group: 'none', selector: '.none' }]);
  // the image that is wholly outside the viewport never blocks the settle; the one inside that is not complete does until the deadline
  const t0 = Date.now();
  out.settle_blocked = await get('SETTLE_JS')({ frames: 2, timeout_ms: 200 });
  out.settle_blocked_took_ms = Date.now() - t0;
  const t1 = Date.now();
  out.settle_bounded = await get('SETTLE_JS')({ frames: 2, timeout_ms: 2000, image_timeout_ms: 100 });
  out.settle_bounded_took_ms = Date.now() - t1;
  images[1].complete = true;
  out.settle_ready = await get('SETTLE_JS')({ frames: 2, timeout_ms: 200 });
  out.settle_moving = await get('SETTLE_JS')({ frames: 2, timeout_ms: 2000, selectors: ['.moving'] });
  out.settle_never = await get('SETTLE_JS')({ frames: 2, timeout_ms: 150, selectors: ['.always'] });
  out.frames_run = framesRun;
  out.ready_all = get('READY_JS')({ a: '#there' });
  out.ready_missing = get('READY_JS')({ a: '#there', b: '#nope' });
  out.present = get('PRESENT_JS')({ a: '#there', b: '#nope' });
  console.log(JSON.stringify(out));
})();
"""

    @unittest.skipUnless(NODE, 'node is not available')
    def test_the_scripts_against_a_mock_of_the_dom(self):
        tmp = tempfile.mkdtemp(prefix='e10-js-')
        h = os.path.join(tmp, 'harness.js')
        s = os.path.join(tmp, 'scripts.json')
        with open(h, 'w', encoding='utf-8') as f:
            f.write(self.HARNESS)
        with open(s, 'w', encoding='utf-8') as f:
            json.dump(capture.IN_PAGE_SCRIPTS, f)
        proc = subprocess.run([NODE, h, s], capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout.strip().splitlines()[-1])
        els = out['elements']
        self.assertEqual(els['scroll_y'], 0)
        self.assertEqual(els['effective_type'], '4g')
        self.assertEqual([e['index'] for e in els['groups']['card']['elements']], [0, 1])
        self.assertEqual(els['groups']['card']['elements'][0]['box'], {'x': 0, 'y': 0, 'w': 100, 'h': 100})
        self.assertEqual(els['groups']['card']['elements'][0]['img']['host'], 'upload.wikimedia.org')
        self.assertTrue(els['groups']['card']['elements'][0]['img']['complete'])
        self.assertIsNone(els['groups']['card']['elements'][1]['img'])
        self.assertEqual(els['groups']['bad'], {'error': 'SyntaxError', 'elements': []})
        self.assertEqual(els['groups']['none'], {'error': None, 'elements': []})
        self.assertFalse(out['settle_blocked']['images_complete'])
        self.assertEqual(out['settle_blocked']['pending_images'], 1)  # the lazy image outside the viewport is not counted
        self.assertGreaterEqual(out['settle_blocked_took_ms'], 150)
        # the image wait has a bound of its own: with an image that never completes, the layout check still runs and the call ends long before the whole budget
        self.assertFalse(out['settle_bounded']['images_complete'])
        self.assertEqual(out['settle_bounded']['pending_images'], 1)
        self.assertTrue(out['settle_bounded']['boxes_stable'])
        self.assertLess(out['settle_bounded_took_ms'], 1000)
        self.assertTrue(out['settle_ready']['images_complete'])
        self.assertTrue(out['settle_ready']['fonts_ready'])
        self.assertEqual(out['settle_ready']['frames'], 2)
        self.assertTrue(out['settle_ready']['boxes_stable'])
        self.assertTrue(out['settle_moving']['boxes_stable'])  # the boxes moved for six reads, then held for two frames
        self.assertGreaterEqual(out['settle_moving']['frames'], 8)
        self.assertFalse(out['settle_never']['boxes_stable'])  # a layout that never stops moving is never reported stable
        self.assertTrue(out['ready_all'])
        self.assertFalse(out['ready_missing'])
        self.assertEqual(out['present'], {'a': True, 'b': False})


if __name__ == '__main__':
    unittest.main(verbosity=2)
