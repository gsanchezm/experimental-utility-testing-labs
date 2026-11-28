"""The comparison instrument: the PNG codec, the pin of the Pixelmatch tarball, and the Node.js runner (operation OP-PREP-E10).

Static tests: no browser and no network. The PNG cases are built by a reference encoder that is written here and shares no code with the
decoder. The tarball cases use synthetic archives with their own pins (the real pin is checked for shape only). The runner is exercised
with a stub module (plumbing: files in, counts and mask out) whenever `node` exists, and with the real pinned module when the environment
variable E10_PIXELMATCH_TARBALL names a local copy of the registry tarball (otherwise that case is skipped and the skip is visible)."""
import base64
import hashlib
import io
import os
import re
import shutil
import struct
import sys
import tarfile
import tempfile
import unittest
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import compare  # noqa: E402

NODE = shutil.which('node')
REAL_TARBALL = os.environ.get(compare.TARBALL_ENV)


# ---- a reference PNG encoder (independent of the decoder) ---------------------------------------------------------------------------------------
def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else (b if pb <= pc else c)


def filter_row(ftype, row, prev, bpp):
    out = bytearray()
    for i, x in enumerate(row):
        a = row[i - bpp] if i >= bpp else 0
        b = prev[i]
        c = prev[i - bpp] if i >= bpp else 0
        pred = (0, a, b, (a + b) // 2, paeth(a, b, c))[ftype]
        out.append((x - pred) & 255)
    return bytes(out)


def reference_png(width, height, pixels, color, filters):
    """pixels: height rows of bytes (width x 3 or x 4 bytes); filters: the filter type of each row (cycled)."""
    bpp = 3 if color == 2 else 4
    raw = bytearray()
    prev = bytes(width * bpp)
    for y in range(height):
        ftype = filters[y % len(filters)]
        raw.append(ftype)
        raw += filter_row(ftype, pixels[y], prev, bpp)
        prev = pixels[y]

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, color, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(raw))) + chunk(b'IEND', b''))


def pattern_rows(width, height, bpp):
    return [bytes(((x * 7 + y * 13 + c * 29 + (x * y) % 11) * 5) & 255 for x in range(width) for c in range(bpp)) for y in range(height)]


def solid_rgba(width, height, rgba):
    return bytes(rgba) * (width * height)


class PngCodecTests(unittest.TestCase):
    def test_every_filter_type_and_both_colour_types_round_trip(self):
        for color, bpp in ((6, 4), (2, 3)):
            rows = pattern_rows(17, 13, bpp)
            for ftype in range(5):
                png = reference_png(17, 13, rows, color, [ftype])
                w, h, rgba = compare.decode_png(png)
                self.assertEqual((w, h), (17, 13))
                expected = b''.join(rows) if color == 6 else b''.join(b''.join(r[i:i + 3] + b'\xff' for i in range(0, len(r), 3)) for r in rows)
                self.assertEqual(rgba, expected, f'colour {color}, filter {ftype}')
            mixed = reference_png(17, 13, rows, color, [0, 1, 2, 3, 4, 4, 3, 2, 1])
            self.assertEqual(compare.decode_png(mixed)[2], compare.decode_png(reference_png(17, 13, rows, color, [0]))[2])

    def test_the_encoder_output_decodes_to_its_input(self):
        rgba = b''.join(pattern_rows(9, 5, 4))
        png = compare.encode_png_rgba(9, 5, rgba)
        self.assertEqual(compare.decode_png(png), (9, 5, rgba))
        self.assertEqual(compare.png_info(png)[:3], (9, 5, 6))
        with self.assertRaises(compare.PngError):
            compare.encode_png_rgba(9, 5, rgba[:-1])

    def test_png_info_reads_the_size_without_decompressing(self):
        png = reference_png(1280, 4, pattern_rows(1280, 4, 3), 2, [1])
        self.assertEqual(compare.png_info(png)[:2], (1280, 4))

    def test_a_damaged_or_unsupported_png_is_refused(self):
        good = compare.encode_png_rgba(4, 4, solid_rgba(4, 4, (1, 2, 3, 4)))
        for bad in (b'not a png', good[:40], good[:33], good[:23] + b'\x05' + good[24:], good.replace(b'IDAT', b'IDAX')):
            with self.assertRaises(compare.PngError):
                compare.decode_png(bad)

        def with_header(depth, color, interlace):
            def chunk(t, d):
                return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
            return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 2, depth, color, 0, 0, interlace))
                    + chunk(b'IDAT', zlib.compress(bytes(2 * (2 * 4 + 1)))) + chunk(b'IEND', b''))
        for depth, color, interlace in ((16, 6, 0), (8, 3, 0), (8, 0, 0), (8, 6, 1)):
            with self.assertRaises(compare.PngError):
                compare.decode_png(with_header(depth, color, interlace))


# ---- the pin ---------------------------------------------------------------------------------------------------------------------------------
def make_tarball(members):
    """A .tgz with the given members: {name: bytes | ('link', target)}."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as tar:
        for name, body in members.items():
            if isinstance(body, tuple):
                info = tarfile.TarInfo(name)
                info.type = tarfile.SYMTYPE
                info.linkname = body[1]
                tar.addfile(info)
            else:
                info = tarfile.TarInfo(name)
                info.size = len(body)
                tar.addfile(info, io.BytesIO(body))
    return buf.getvalue()


def pins_for(data, member_body):
    return {'tarball_sha256': hashlib.sha256(data).hexdigest(), 'integrity': compare.sha512_integrity(data),
            'shasum': hashlib.sha1(data).hexdigest(), 'member_sha256': hashlib.sha256(member_body).hexdigest()}


class PinTests(unittest.TestCase):
    MODULE = b'export default function pixelmatch() { return 0; }\n'

    def test_the_real_pin_has_the_shape_the_registry_publishes(self):
        self.assertEqual(compare.PIXELMATCH_VERSION, '8.0.0')
        self.assertRegex(compare.PIXELMATCH_TARBALL_SHA256, r'^[0-9a-f]{64}$')
        self.assertRegex(compare.PIXELMATCH_INDEX_SHA256, r'^[0-9a-f]{64}$')
        self.assertRegex(compare.PIXELMATCH_REGISTRY_SHASUM, r'^[0-9a-f]{40}$')
        self.assertEqual(len(base64.b64decode(compare.PIXELMATCH_REGISTRY_INTEGRITY.split('-', 1)[1])), 64)
        self.assertTrue(compare.PIXELMATCH_TARBALL_URL.startswith('https://registry.npmjs.org/pixelmatch/-/pixelmatch-8.0.0.tgz'))
        self.assertEqual(compare.PIXELMATCH_MEMBER, 'package/index.js')

    def test_the_constants_read_by_the_gate_have_the_exact_line_form(self):
        with open(os.path.join(HERE, '..', 'executor', 'compare.py'), encoding='utf-8') as f:
            src = f.read()
        self.assertRegex(src, r"(?m)^PIXELMATCH_VERSION = '8\.0\.0'$")
        self.assertRegex(src, r"(?m)^PIXELMATCH_TARBALL_SHA256 = '[0-9a-f]{64}'$")
        self.assertRegex(src, r"(?m)^PIXELMATCH_INDEX_SHA256 = '[0-9a-f]{64}'$")

    def test_a_good_tarball_gives_the_member_and_ignores_every_other_member(self):
        data = make_tarball({'package/index.js': self.MODULE, 'package/package.json': b'{}', 'package/bin/pixelmatch': b'#!/usr/bin/env node\n',
                             '../evil.txt': b'x', 'package/extra.js': b'y'})
        self.assertEqual(compare.verify_tarball(data, pins_for(data, self.MODULE)), self.MODULE)

    def test_refusals(self):
        data = make_tarball({'package/index.js': self.MODULE})
        good = pins_for(data, self.MODULE)
        for key in ('tarball_sha256', 'integrity', 'shasum', 'member_sha256'):
            with self.assertRaises(compare.CompareError, msg=key):
                compare.verify_tarball(data, {**good, key: good[key][:-1] + ('0' if good[key][-1] != '0' else '1')})
        other = make_tarball({'package/index.js': self.MODULE + b'// changed\n'})
        with self.assertRaises(compare.CompareError):  # the tarball digest is the pin of another archive
            compare.verify_tarball(other, good)
        with self.assertRaises(compare.CompareError):  # the member digest differs
            compare.verify_tarball(other, pins_for(other, self.MODULE))
        no_member = make_tarball({'package/other.js': self.MODULE})
        with self.assertRaises(compare.CompareError):
            compare.verify_tarball(no_member, pins_for(no_member, self.MODULE))
        link = make_tarball({'package/index.js': ('link', 'package/other.js')})
        with self.assertRaises(compare.CompareError):
            compare.verify_tarball(link, pins_for(link, self.MODULE))
        with self.assertRaises(compare.CompareError):
            compare.verify_tarball(b'not a tarball', pins_for(b'not a tarball', b''))
        with self.assertRaises(compare.CompareError):  # the real pin refuses a synthetic archive
            compare.verify_tarball(data)

    def test_fetch_writes_only_the_verified_module_from_the_local_hook(self):
        data = make_tarball({'package/index.js': self.MODULE, 'package/README.md': b'readme'})
        tmp = tempfile.mkdtemp(prefix='e10-pin-')
        tgz = os.path.join(tmp, 'p.tgz')
        with open(tgz, 'wb') as f:
            f.write(data)
        dest = os.path.join(tmp, 'work')
        os.environ[compare.TARBALL_ENV] = tgz
        try:
            rec = compare.fetch_pixelmatch(dest, pins_for(data, self.MODULE))
            self.assertEqual(sorted(os.listdir(dest)), ['pixelmatch.mjs'])
            with open(rec['module_path'], 'rb') as f:
                self.assertEqual(f.read(), self.MODULE)
            self.assertEqual(rec['index_sha256'], hashlib.sha256(self.MODULE).hexdigest())
            with self.assertRaises(compare.CompareError):  # the real pin refuses the synthetic archive even through the hook
                compare.fetch_pixelmatch(os.path.join(tmp, 'work2'))
            os.environ[compare.TARBALL_ENV] = os.path.join(tmp, 'missing.tgz')
            with self.assertRaises(compare.CompareError):
                compare.fetch_pixelmatch(os.path.join(tmp, 'work3'))
        finally:
            os.environ.pop(compare.TARBALL_ENV, None)
            if REAL_TARBALL:
                os.environ[compare.TARBALL_ENV] = REAL_TARBALL


# ---- the runner (Node.js) -------------------------------------------------------------------------------------------------------------------
STUB_MODULE = r"""
export default function pixelmatch(a, b, out, w, h, opts) {
  let n = 0;
  for (let i = 0, p = 0; i < w * h; i++, p += 4) {
    if (a[p] !== b[p] || a[p + 1] !== b[p + 1] || a[p + 2] !== b[p + 2]) { out[p] = 255; out[p + 1] = 0; out[p + 2] = 0; out[p + 3] = 255; n++; }
    else { out[p] = out[p + 1] = out[p + 2] = 200; out[p + 3] = 255; }
  }
  if (opts.threshold !== 0.1 || opts.includeAA !== false || opts.alpha !== 0.1) { throw new Error('options not passed through'); }
  return n;
}
"""


def comparator_with(module_source):
    work = tempfile.mkdtemp(prefix='e10-runner-')
    module = os.path.join(work, 'pixelmatch.mjs')
    with open(module, 'w', encoding='utf-8') as f:
        f.write(module_source)
    runner = os.path.join(work, 'runner.mjs')
    with open(runner, 'w', encoding='utf-8') as f:
        f.write(compare.NODE_RUNNER_JS)
    return compare.Comparator(work, NODE, 'test', {'module_path': module}, runner)


def block(png_w, png_h, base, x0, y0, bw, bh, color):
    rgba = bytearray(solid_rgba(png_w, png_h, base))
    for y in range(y0, y0 + bh):
        for x in range(x0, x0 + bw):
            rgba[(y * png_w + x) * 4:(y * png_w + x) * 4 + 4] = bytes(color)
    return compare.encode_png_rgba(png_w, png_h, bytes(rgba))


@unittest.skipUnless(NODE, 'node is not available')
class RunnerPlumbingTests(unittest.TestCase):
    def test_identical_images_and_one_changed_block(self):
        cmp_ = comparator_with(STUB_MODULE)
        a = block(40, 30, (255, 255, 255, 255), 0, 0, 0, 0, (0, 0, 0, 255))
        same = cmp_.compare(a, a)
        self.assertEqual((same['differing'], same['compared'], same['ratio'], same['mask'].count(1)), (0, 1200, 0.0, 0))
        b = block(40, 30, (255, 255, 255, 255), 5, 6, 10, 10, (0, 0, 0, 255))
        diff = cmp_.compare(a, b)
        self.assertEqual((diff['differing'], diff['mask'].count(1), diff['width'], diff['height']), (100, 100, 40, 30))
        self.assertAlmostEqual(diff['ratio'], 100 / 1200)
        self.assertEqual(diff['mask'][6 * 40 + 5], 1)
        self.assertEqual(diff['mask'][5 * 40 + 5], 0)
        w, h, rgba = compare.decode_png(diff['diff_png'])
        self.assertEqual((w, h), (40, 30))
        self.assertEqual(sum(1 for i in range(0, len(rgba), 4) if tuple(rgba[i:i + 4]) == compare.DIFF_COLOR), 100)
        self.assertEqual(cmp_.calls, 2)

    def test_a_dimension_mismatch_is_reported_without_a_comparison(self):
        cmp_ = comparator_with(STUB_MODULE)
        a = compare.encode_png_rgba(4, 4, solid_rgba(4, 4, (1, 2, 3, 255)))
        b = compare.encode_png_rgba(4, 5, solid_rgba(4, 5, (1, 2, 3, 255)))
        out = cmp_.compare(a, b)
        self.assertEqual((out['dimension_mismatch'], out['size_a'], out['size_b']), (True, [4, 4], [4, 5]))
        self.assertEqual(cmp_.calls, 0)

    def test_a_failing_runner_is_a_comparison_error(self):
        cmp_ = comparator_with('export default function () { throw new Error("boom"); }\n')
        a = compare.encode_png_rgba(2, 2, solid_rgba(2, 2, (1, 2, 3, 255)))
        with self.assertRaises(compare.CompareError):
            cmp_.compare(a, a)

    def test_a_mask_that_disagrees_with_the_count_is_refused(self):
        lie = STUB_MODULE.replace('return n;', 'return n + 1;')
        cmp_ = comparator_with(lie)
        a = compare.encode_png_rgba(4, 4, solid_rgba(4, 4, (1, 2, 3, 255)))
        with self.assertRaises(compare.CompareError):
            cmp_.compare(a, a)

    def test_the_decoded_screenshots_are_cached_until_cleared(self):
        cmp_ = comparator_with(STUB_MODULE)
        a = compare.encode_png_rgba(4, 4, solid_rgba(4, 4, (1, 2, 3, 255)))
        cmp_.decode(a)
        cmp_.decode(a)
        self.assertEqual(len(cmp_._decoded), 1)
        cmp_.clear()
        self.assertEqual(len(cmp_._decoded), 0)

    def test_the_runner_constant_is_what_is_hashed(self):
        self.assertEqual(comparator_with(STUB_MODULE).runner_sha256, hashlib.sha256(compare.NODE_RUNNER_JS.encode('utf-8')).hexdigest())

    def test_the_runner_syntax(self):
        import subprocess
        tmp = tempfile.mkdtemp(prefix='e10-syntax-')
        path = os.path.join(tmp, 'runner.mjs')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(compare.NODE_RUNNER_JS)
        self.assertEqual(subprocess.run([NODE, '--check', path], capture_output=True, text=True).returncode, 0)


@unittest.skipUnless(NODE and REAL_TARBALL and os.path.exists(REAL_TARBALL or ''), 'the real pixelmatch tarball is not named by E10_PIXELMATCH_TARBALL')
class RealModuleTests(unittest.TestCase):
    """The pinned module itself, on synthetic images. Needs a local copy of the registry tarball (the digests are checked by prepare)."""

    @classmethod
    def setUpClass(cls):
        cls.cmp = compare.Comparator.prepare()

    def test_the_pinned_module_counts_a_solid_block_exactly(self):
        a = block(64, 48, (255, 255, 255, 255), 0, 0, 0, 0, (0, 0, 0, 255))
        same = self.cmp.compare(a, a)
        self.assertEqual(same['differing'], 0)
        b = block(64, 48, (255, 255, 255, 255), 10, 12, 10, 10, (0, 0, 0, 255))
        diff = self.cmp.compare(a, b)
        self.assertEqual((diff['differing'], diff['mask'].count(1)), (100, 100))
        self.assertEqual(diff['options'], {'threshold': 0.1, 'includeAA': False, 'alpha': 0.1})

    def test_a_difference_below_the_colour_threshold_is_not_counted(self):
        a = compare.encode_png_rgba(8, 8, solid_rgba(8, 8, (200, 200, 200, 255)))
        b = compare.encode_png_rgba(8, 8, solid_rgba(8, 8, (201, 200, 200, 255)))
        self.assertEqual(self.cmp.compare(a, b)['differing'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
