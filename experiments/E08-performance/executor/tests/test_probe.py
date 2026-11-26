"""The in-page measurement script, run in Node against a mock of the browser APIs it reads (operation OP-PREP-E08). Static tests:
there is no browser here; the first real evidence of the script in Chromium is the ENVIRONMENT_VERIFICATION DRY_RUN."""
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

from executor import probe  # noqa: E402

NODE = shutil.which('node')

HARNESS = r"""
const vm = require('vm');
const fs = require('fs');
const script = fs.readFileSync(process.argv[2], 'utf8');
const state = { observers: [], mutation: null, present: new Set(), now: 100 };
class PO {
  constructor(cb) { this.cb = cb; this.type = null; this.queue = []; state.observers.push(this); }
  observe(o) { if (!['largest-contentful-paint', 'layout-shift', 'longtask', 'paint'].includes(o.type)) { const e = new Error('unsupported'); e.name = 'TypeError'; throw e; } this.type = o.type; this.buffered = o.buffered; }
  takeRecords() { const q = this.queue; this.queue = []; return q; }
  deliver(entries) { this.cb({ getEntries: () => entries }); }
}
PO.supportedEntryTypes = ['largest-contentful-paint', 'layout-shift', 'longtask', 'paint'];
class MO { constructor(cb) { state.mutation = cb; } observe() {} disconnect() {} }
const sandbox = {
  performance: { now: () => state.now, timeOrigin: 1700000000000, getEntriesByType: (t) => t === 'navigation' ? [{ startTime: 0, responseStart: 12, domContentLoadedEventEnd: 300, loadEventEnd: 400, type: 'navigate' }] : [{ name: 'http://x/api/pizzas', initiatorType: 'fetch', startTime: 50, responseEnd: 3050, duration: 3000, transferSize: 10, responseStatus: 200 }] },
  PerformanceObserver: PO, MutationObserver: MO,
  document: { querySelector: (sel) => state.present.has(sel) ? { id: 'x' } : null },
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(script, sandbox);
const out = {};
const by = (t) => state.observers.find((o) => o.type === t);
out.observer_types = state.observers.map((o) => o.type).sort();
out.buffered = state.observers.every((o) => o.buffered === true);
// entries delivered through the callback, and entries still queued at flush time
by('largest-contentful-paint').deliver([{ startTime: 400, renderTime: 400, loadTime: 0, size: 5000, id: '', url: '', element: { nodeType: 1, tagName: 'P', id: 'a', className: 'c1 c2 c3' } }]);
by('longtask').queue.push({ startTime: 200, duration: 5012, name: 'self' });
by('layout-shift').deliver([{ startTime: 4000, value: 0.1, hadRecentInput: false, sources: [{ node: { nodeType: 1, tagName: 'P', id: 'target-text', className: '' }, previousRect: { x: 0, y: 1, width: 2, height: 3 }, currentRect: { x: 0, y: 5, width: 2, height: 3 } }, { node: null, previousRect: null, currentRect: null }] }]);
by('paint').deliver([{ name: 'first-contentful-paint', startTime: 380 }]);
// a watched element that appears later is stamped when the mutation callback runs
state.now = 3150; state.present.add('h2.x'); state.mutation();
state.now = 3200; state.mutation();  // a second mutation does not move the stamp
const snap = sandbox.window.__e08_flush();
out.snapshot = JSON.parse(JSON.stringify(snap));
out.second_flush_same_object = sandbox.window.__e08_flush() === snap;
console.log(JSON.stringify(out));
"""


@unittest.skipUnless(NODE, 'node is not available')
class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='e08-probe-')
        script = os.path.join(cls.tmp, 'init.js')
        with open(script, 'w', encoding='utf-8') as f:
            f.write(probe.init_script({'first_item': 'h2.x', 'never': 'h3.never'}))
        harness = os.path.join(cls.tmp, 'harness.js')
        with open(harness, 'w', encoding='utf-8') as f:
            f.write(HARNESS)
        r = subprocess.run([NODE, harness, script], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        cls.out = json.loads(r.stdout)
        cls.snap = cls.out['snapshot']

    def test_the_script_is_valid_javascript_and_registers_the_four_observers_with_buffering(self):
        self.assertEqual(self.out['observer_types'], ['largest-contentful-paint', 'layout-shift', 'longtask', 'paint'])
        self.assertTrue(self.out['buffered'])
        self.assertEqual(self.snap['probe_version'], probe.PROBE_VERSION)
        self.assertEqual(self.snap['errors'], [])

    def test_entries_from_the_callback_and_from_the_queue_are_both_kept(self):
        self.assertEqual(self.snap['lcp'][0]['start_time'], 400)
        self.assertEqual(self.snap['lcp'][0]['element'], 'p#a.c1.c2')
        self.assertEqual(self.snap['longtasks'], [{'start_time': 200, 'duration': 5012, 'name': 'self'}])
        self.assertEqual(self.snap['paints'], [{'name': 'first-contentful-paint', 'start_time': 380}])

    def test_layout_shift_sources_keep_the_node_id_and_survive_a_removed_node(self):
        shift = self.snap['cls'][0]
        self.assertEqual((shift['start_time'], shift['value'], shift['had_recent_input']), (4000, 0.1, False))
        self.assertEqual(shift['sources'][0]['node_id'], 'target-text')
        self.assertEqual(shift['sources'][0]['current_rect']['y'], 5)
        self.assertEqual(shift['sources'][1]['node_id'], None)

    def test_a_watched_element_is_stamped_once_and_an_absent_one_stays_undefined(self):
        self.assertEqual(self.snap['ready']['first_item'], 3150)
        self.assertNotIn('never', self.snap['ready'])

    def test_navigation_and_resources_are_recorded(self):
        self.assertEqual(self.snap['navigation']['response_start'], 12)
        self.assertEqual(self.snap['resources'][0]['response_end'], 3050)
        self.assertEqual(self.snap['resources'][0]['response_status'], 200)
        self.assertTrue(self.out['second_flush_same_object'])

    def test_init_script_embeds_the_watch_config_before_the_probe(self):
        text = probe.init_script({'a': 'b'})
        self.assertTrue(text.startswith('window.__e08_config = {"watch": {"a": "b"}};'))
        self.assertIn("probe_version: 'e08-probe-v1'", text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
