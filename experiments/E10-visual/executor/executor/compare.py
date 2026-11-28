"""E10-visual executor: the image comparison (Pixelmatch 8.0.0, pinned by digest) and the PNG codec (Python standard library only).

DRAFT (operation OP-PREP-E10). The comparison tool is the reference npm module `pixelmatch` 8.0.0 (ISC): the single self-contained file
`package/index.js` of the registry tarball, which has no import (its dependency `pngjs` serves only its command-line program). This module
(1) downloads the tarball (or reads a local copy named by the environment variable E10_PIXELMATCH_TARBALL, for tests and development; the
same digests are checked either way), verifies its sha256, its registry sha512 integrity and its sha1 shasum, reads only the one member
`package/index.js` in memory (nothing else is extracted), verifies the member's sha256 and writes it as `pixelmatch.mjs` into a work
directory; (2) decodes the two PNG screenshots with the Python standard library (8-bit RGB or RGBA, not interlaced, all five filter types) to
raw RGBA buffers; (3) runs the module with the runner's Node.js on those buffers, with the library defaults of conditions-draft.json
(`threshold` 0.1, `includeAA` false, `alpha` 0.1), and receives the differing-pixel count, the diff image and a one-byte-per-pixel mask of the
counted differences (taken from the diff colour of the output and cross-checked against the count). Nothing is tuned.

The Node.js runner is the constant NODE_RUNNER_JS below, so that it sits under the digest lock of run-condition.sh (a separate .mjs file in
executor/executor/ would be an unlisted file).
"""
import base64
import hashlib
import io
import json
import os
import shutil
import struct
import subprocess
import tarfile
import tempfile
import urllib.request
import zlib

PIXELMATCH_VERSION = '8.0.0'
PIXELMATCH_TARBALL_URL = 'https://registry.npmjs.org/pixelmatch/-/pixelmatch-8.0.0.tgz'
PIXELMATCH_TARBALL_SHA256 = 'ab59d4c4ec73fbf456c72cbd8200b1529a76142fd9291de72a62ba6e3a845e75'
PIXELMATCH_REGISTRY_INTEGRITY = 'sha512-cIqOLfh5k52us715qf3B3+kTOxZv+WDv77HN7xokLScYQGYQHi4m/ynoDIPpvF2LvCyUJGyvzY64i0QCXtzu1g=='
PIXELMATCH_REGISTRY_SHASUM = 'e1aeaa0b6e52b87603e0a6e8ae35687e1550a143'
PIXELMATCH_MEMBER = 'package/index.js'
PIXELMATCH_INDEX_SHA256 = '5b8583627704b4e1fe4fea472c283c8ca03d10ae4c94e5e029ea3b271a998ee6'
PIXELMATCH_OPTIONS = {'threshold': 0.1, 'includeAA': False, 'alpha': 0.1}
TARBALL_ENV = 'E10_PIXELMATCH_TARBALL'
DOWNLOAD_TIMEOUT_S = 60
NODE_TIMEOUT_S = 120
DIFF_COLOR = (255, 0, 0, 255)  # the library default diffColor with the alpha of drawPixel; no gray or anti-aliased pixel has it

NODE_RUNNER_JS = r"""
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';

const [modulePath, aPath, bPath, w, h, outPath, maskPath, optionsJson] = process.argv.slice(2);
const { default: pixelmatch } = await import(pathToFileURL(modulePath).href);
const width = Number(w);
const height = Number(h);
const len = width * height;
const load = (p) => { const b = fs.readFileSync(p); const u = new Uint8Array(b.length); u.set(b); return u; };
const a = load(aPath);
const b = load(bPath);
if (a.length !== len * 4 || b.length !== len * 4) { throw new Error('raw image size does not match width x height x 4'); }
const out = new Uint8Array(len * 4);
const diff = pixelmatch(a, b, out, width, height, JSON.parse(optionsJson));
const mask = new Uint8Array(len);
let marked = 0;
for (let i = 0, p = 0; i < len; i++, p += 4) {
  if (out[p] === 255 && out[p + 1] === 0 && out[p + 2] === 0 && out[p + 3] === 255) { mask[i] = 1; marked++; }
}
fs.writeFileSync(outPath, out);
fs.writeFileSync(maskPath, mask);
process.stdout.write(JSON.stringify({ diff_count: diff, compared: len, mask_count: marked, node_version: process.version }) + '\n');
"""


class CompareError(Exception):
    """The comparison instrument is not usable (a pin does not match, Node.js is absent, the runner failed). Never a finding about a SUT."""


class PngError(CompareError):
    """A PNG that the standard-library codec does not handle (only 8-bit, not interlaced, colour type 2 or 6)."""


# ---- the pin -----------------------------------------------------------------------------------------------------------------------------
def sha512_integrity(data):
    return 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode('ascii')


def verify_tarball(data, pins=None):
    """Check the downloaded bytes against every digest of the pin; return the member bytes (read in memory, nothing is extracted)."""
    p = {'tarball_sha256': PIXELMATCH_TARBALL_SHA256, 'integrity': PIXELMATCH_REGISTRY_INTEGRITY, 'shasum': PIXELMATCH_REGISTRY_SHASUM,
         'member': PIXELMATCH_MEMBER, 'member_sha256': PIXELMATCH_INDEX_SHA256, **(pins or {})}
    got = hashlib.sha256(data).hexdigest()
    if got != p['tarball_sha256']:
        raise CompareError(f'pixelmatch tarball sha256 {got} does not equal the pin {p["tarball_sha256"]}')
    if sha512_integrity(data) != p['integrity']:
        raise CompareError('pixelmatch tarball sha512 integrity does not equal the registry integrity of the pin')
    if hashlib.sha1(data).hexdigest() != p['shasum']:  # noqa: S324 - the registry publishes a sha1 shasum; checked beside the two stronger digests
        raise CompareError('pixelmatch tarball sha1 shasum does not equal the registry shasum of the pin')
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
            try:
                member = tar.getmember(p['member'])
            except KeyError as e:
                raise CompareError(f'{p["member"]} is absent from the tarball') from e
            if not member.isfile():
                raise CompareError(f'{p["member"]} is not a regular file')
            body = tar.extractfile(member).read()
    except tarfile.TarError as e:
        raise CompareError(f'the pixelmatch tarball cannot be read: {e}') from e
    digest = hashlib.sha256(body).hexdigest()
    if digest != p['member_sha256']:
        raise CompareError(f'{p["member"]} sha256 {digest} does not equal the pin {p["member_sha256"]}')
    return body


def fetch_pixelmatch(dest, pins=None, url=None):
    """Make `pixelmatch.mjs` (the verified module, byte for byte) in `dest`. A local tarball named by E10_PIXELMATCH_TARBALL replaces the
    download; the same digests apply. Returns the record of the pin as used."""
    os.makedirs(dest, exist_ok=True)
    local = os.environ.get(TARBALL_ENV)
    if local:
        try:
            with open(local, 'rb') as f:
                data = f.read()
        except OSError as e:
            raise CompareError(f'the local pixelmatch tarball named by {TARBALL_ENV} cannot be read: {e}') from e
        source = 'local tarball named by ' + TARBALL_ENV
    else:
        try:
            with urllib.request.urlopen(url or PIXELMATCH_TARBALL_URL, timeout=DOWNLOAD_TIMEOUT_S) as r:  # noqa: S310 - fixed https registry URL
                data = r.read()
        except Exception as e:  # noqa: BLE001 - a failed download refuses the run (no retry)
            raise CompareError(f'the pixelmatch tarball could not be downloaded: {e.__class__.__name__}: {e}') from e
        source = url or PIXELMATCH_TARBALL_URL
    body = verify_tarball(data, pins)
    path = os.path.join(dest, 'pixelmatch.mjs')
    with open(path, 'wb') as f:
        f.write(body)
    return {'version': PIXELMATCH_VERSION, 'source': source, 'tarball_sha256': hashlib.sha256(data).hexdigest(),
            'index_sha256': hashlib.sha256(body).hexdigest(), 'module_path': path}


# ---- PNG codec (standard library) --------------------------------------------------------------------------------------------------------
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def _chunks(data):
    if data[:8] != PNG_SIGNATURE:
        raise PngError('not a PNG file')
    pos, n = 8, len(data)
    while pos + 8 <= n:
        length, ctype = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        crc = data[pos + 8 + length:pos + 12 + length]
        if len(body) != length or len(crc) != 4:
            raise PngError('truncated PNG chunk')
        if struct.unpack('>I', crc)[0] != (zlib.crc32(ctype + body) & 0xffffffff):
            raise PngError(f'bad CRC in the {ctype!r} chunk')
        yield ctype, body
        pos += 12 + length
        if ctype == b'IEND':
            return


def png_info(data):
    """(width, height, colour type) from the IHDR chunk, without decompressing."""
    for ctype, body in _chunks(data):
        if ctype == b'IHDR':
            width, height, depth, color, _comp, _filt, interlace = struct.unpack('>IIBBBBB', body)
            return width, height, color, depth, interlace
        break
    raise PngError('no IHDR chunk')


def _sub(line, bpp, stride):
    from itertools import accumulate
    cur = bytearray(stride)
    for c in range(bpp):
        cur[c::bpp] = bytes(accumulate(line[c::bpp], lambda a, b: (a + b) & 255))
    return bytes(cur)


def _up(line, prev, stride):
    """Byte-wise addition modulo 256 of two rows, with big-integer arithmetic (no carry may cross a byte)."""
    high = int.from_bytes(b'\x80' * stride, 'big')
    low = int.from_bytes(b'\x7f' * stride, 'big')
    a, b = int.from_bytes(line, 'big'), int.from_bytes(prev, 'big')
    return (((a & low) + (b & low)) ^ ((a ^ b) & high)).to_bytes(stride, 'big')


def _average(line, prev, bpp, stride):
    cur = bytearray(stride)
    for i in range(stride):
        left = cur[i - bpp] if i >= bpp else 0
        cur[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
    return bytes(cur)


def _paeth(line, prev, bpp, stride):
    cur = bytearray(stride)
    for i in range(stride):
        if i >= bpp:
            a, c = cur[i - bpp], prev[i - bpp]
        else:
            a = c = 0
        b = prev[i]
        pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
        pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
        cur[i] = (line[i] + pred) & 255
    return bytes(cur)


def decode_png(data):
    """Return (width, height, rgba bytes) of an 8-bit, non-interlaced PNG of colour type 2 (RGB) or 6 (RGBA)."""
    width = height = color = None
    idat = []
    for ctype, body in _chunks(data):
        if ctype == b'IHDR':
            width, height, depth, color, comp, filt, interlace = struct.unpack('>IIBBBBB', body)
            if depth != 8 or color not in (2, 6) or comp != 0 or filt != 0 or interlace != 0:
                raise PngError(f'unsupported PNG (bit depth {depth}, colour type {color}, interlace {interlace})')
        elif ctype == b'IDAT':
            idat.append(body)
    if width is None or not idat:
        raise PngError('the PNG has no IHDR or no IDAT chunk')
    bpp = 3 if color == 2 else 4
    stride = width * bpp
    try:
        raw = zlib.decompress(b''.join(idat))
    except zlib.error as e:
        raise PngError(f'the PNG data cannot be decompressed: {e}') from e
    if len(raw) != height * (stride + 1):
        raise PngError(f'the PNG data has {len(raw)} bytes, expected {height * (stride + 1)}')
    out = bytearray(height * stride)
    prev = bytes(stride)
    pos = 0
    for y in range(height):
        ftype = raw[pos]
        line = raw[pos + 1:pos + 1 + stride]
        pos += 1 + stride
        if ftype == 0:
            cur = bytes(line)
        elif ftype == 1:
            cur = _sub(line, bpp, stride)
        elif ftype == 2:
            cur = _up(line, prev, stride)
        elif ftype == 3:
            cur = _average(line, prev, bpp, stride)
        elif ftype == 4:
            cur = _paeth(line, prev, bpp, stride)
        else:
            raise PngError(f'unknown PNG filter type {ftype}')
        out[y * stride:(y + 1) * stride] = cur
        prev = cur
    if color == 6:
        return width, height, bytes(out)
    rgba = bytearray(width * height * 4)
    for c in range(3):
        rgba[c::4] = out[c::3]
    rgba[3::4] = b'\xff' * (width * height)
    return width, height, bytes(rgba)


def _chunk(ctype, body):
    return struct.pack('>I', len(body)) + ctype + body + struct.pack('>I', zlib.crc32(ctype + body) & 0xffffffff)


def encode_png_rgba(width, height, rgba):
    """An 8-bit RGBA PNG (filter 0 on every row)."""
    stride = width * 4
    if len(rgba) != stride * height:
        raise PngError('the RGBA buffer does not match width x height x 4')
    raw = b''.join(b'\x00' + rgba[y * stride:(y + 1) * stride] for y in range(height))
    return (PNG_SIGNATURE + _chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + _chunk(b'IDAT', zlib.compress(raw, 6)) + _chunk(b'IEND', b''))


# ---- the comparator ------------------------------------------------------------------------------------------------------------------------
class Comparator:
    """The prepared instrument of one job: the verified module, the runner, Node.js. `compare` is one comparison of two PNG screenshots."""

    def __init__(self, workdir, node, node_version, pin, runner_path):
        self.workdir, self.node, self.node_version, self.pin, self.runner = workdir, node, node_version, pin, runner_path
        self.runner_sha256 = hashlib.sha256(NODE_RUNNER_JS.encode('utf-8')).hexdigest()
        self._decoded = {}
        self.calls = 0

    @classmethod
    def prepare(cls, workdir=None, pins=None, node=None):
        """Fetch and verify the module, write the runner, find Node.js and read its version. Raises CompareError (the run is refused)."""
        workdir = workdir or tempfile.mkdtemp(prefix='e10-pixelmatch-')
        node = node or shutil.which('node')
        if not node:
            raise CompareError('node is not on PATH (the comparison is run by Node.js)')
        pin = fetch_pixelmatch(workdir, pins)
        runner = os.path.join(workdir, 'runner.mjs')
        with open(runner, 'w', encoding='utf-8', newline='\n') as f:
            f.write(NODE_RUNNER_JS)
        try:
            version = subprocess.run([node, '--version'], capture_output=True, text=True, timeout=30, check=True).stdout.strip()
        except (OSError, subprocess.SubprocessError) as e:
            raise CompareError(f'node --version failed: {e}') from e
        return cls(workdir, node, version, pin, runner)

    def clear(self):
        """Forget the decoded screenshots (called at the end of every execution)."""
        self._decoded.clear()

    def decode(self, png):
        key = hashlib.sha256(png).hexdigest()
        if key not in self._decoded:
            self._decoded[key] = decode_png(png)
        return self._decoded[key]

    def compare(self, png_a, png_b):
        """Compare two screenshots. Returns a dict; `dimension_mismatch` True when their sizes differ (nothing else is then computed).
        Otherwise: width, height, compared, differing, ratio, mask (one byte per pixel, 1 = a counted difference), diff_png, runner facts."""
        wa, ha = png_info(png_a)[:2]
        wb, hb = png_info(png_b)[:2]
        if (wa, ha) != (wb, hb):
            return {'dimension_mismatch': True, 'size_a': [wa, ha], 'size_b': [wb, hb]}
        w, h, ra = self.decode(png_a)
        _w, _h, rb = self.decode(png_b)
        tmp = tempfile.mkdtemp(prefix='cmp-', dir=self.workdir)
        paths = {k: os.path.join(tmp, k) for k in ('a.rgba', 'b.rgba', 'out.rgba', 'mask.bin')}
        try:
            for name, data in (('a.rgba', ra), ('b.rgba', rb)):
                with open(paths[name], 'wb') as f:
                    f.write(data)
            proc = subprocess.run([self.node, self.runner, self.pin['module_path'], paths['a.rgba'], paths['b.rgba'], str(w), str(h),
                                   paths['out.rgba'], paths['mask.bin'], json.dumps(PIXELMATCH_OPTIONS)],
                                  capture_output=True, text=True, timeout=NODE_TIMEOUT_S)
            if proc.returncode != 0:
                raise CompareError(f'the comparison runner failed (exit {proc.returncode}): {proc.stderr.strip()[-400:]}')
            report = json.loads(proc.stdout.strip().splitlines()[-1])
            with open(paths['out.rgba'], 'rb') as f:
                out = f.read()
            with open(paths['mask.bin'], 'rb') as f:
                mask = f.read()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        if report['mask_count'] != report['diff_count'] or mask.count(1) != report['diff_count'] or report['compared'] != w * h:
            raise CompareError(f'the difference mask does not match the count reported by pixelmatch: {report}')
        self.calls += 1
        return {'dimension_mismatch': False, 'width': w, 'height': h, 'compared': w * h, 'differing': report['diff_count'],
                'ratio': report['diff_count'] / (w * h), 'mask': mask, 'diff_png': encode_png_rgba(w, h, out),
                'node_version': report['node_version'], 'options': dict(PIXELMATCH_OPTIONS)}
