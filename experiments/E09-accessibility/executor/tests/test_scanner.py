"""Tests of the tarball verification and the browser-build read (executor/scanner.py), on synthetic archives.

DRAFT (operation OP-PREP-E09). The real pinned tarball is checked only when the environment variable
E09_AXE_TARBALL_FOR_TEST names a local file (a read-only fetch made for the pin re-check; see IMPLEMENTATION-NOTES.md);
otherwise that test reports SKIPPED. No network access happens in these tests.
"""
import base64
import hashlib
import io
import os
import sys
import tarfile
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))

from executor import scanner  # noqa: E402

SYNTHETIC_JS = b'/* DRAFT synthetic browser build for unit tests; not axe-core */ window.axe = { version: "0.0.0-test" };\n'


def make_tarball(path, members):
    with tarfile.open(path, 'w:gz') as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


def integrity(path):
    with open(path, 'rb') as f:
        return 'sha512-' + base64.b64encode(hashlib.sha512(f.read()).digest()).decode('ascii')


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='e09-test-')
        self.tar = os.path.join(self.tmp, 'synthetic.tgz')
        make_tarball(self.tar, {'package/axe.min.js': SYNTHETIC_JS, 'package/package.json': b'{}'})
        self.member_sha = hashlib.sha256(SYNTHETIC_JS).hexdigest()

    def test_reads_member_when_both_digests_match(self):
        text, digest = scanner.read_browser_build(self.tar, integrity(self.tar), self.member_sha)
        self.assertEqual(digest, self.member_sha)
        self.assertIn('window.axe', text)

    def test_default_pins_reject_a_synthetic_archive(self):
        with self.assertRaises(scanner.ScannerIntegrityError):
            scanner.read_browser_build(self.tar)

    def test_wrong_tarball_integrity_is_refused(self):
        with self.assertRaises(scanner.ScannerIntegrityError) as cm:
            scanner.read_browser_build(self.tar, 'sha512-AAAA', self.member_sha)
        self.assertIn('does not equal the pinned integrity', str(cm.exception))

    def test_wrong_member_digest_is_refused(self):
        with self.assertRaises(scanner.ScannerIntegrityError):
            scanner.read_browser_build(self.tar, integrity(self.tar), '0' * 64)

    def test_absent_member_is_refused(self):
        other = os.path.join(self.tmp, 'no-member.tgz')
        make_tarball(other, {'package/other.js': SYNTHETIC_JS})
        with self.assertRaises(scanner.ScannerIntegrityError) as cm:
            scanner.read_browser_build(other, integrity(other), self.member_sha)
        self.assertIn('absent', str(cm.exception))

    def test_pins_are_the_recorded_values(self):
        self.assertEqual(scanner.AXE_VERSION, '4.14.0')
        self.assertEqual(scanner.AXE_NPM_INTEGRITY, 'sha512-9WTZxEjsZ7b13TH8JPmbV2z8CHbl80/2hm3XPEG4JgNdQLK81IBRXmSxHfMAOkSqQeRxT/0dwNDz2GOm3zzpcQ==')
        self.assertEqual(scanner.AXE_MIN_SHA256, '20c09fe157a8a34a30e241aaa1fcdade657734f08ab379ecfbeb7d45cc46e878')
        self.assertEqual(scanner.AXE_RUN_OPTIONS, {'runOnly': {'type': 'rule', 'values': ['empty-heading']}})

    @unittest.skipUnless(os.environ.get('E09_AXE_TARBALL_FOR_TEST'), 'E09_AXE_TARBALL_FOR_TEST not set (no local copy of the pinned tarball)')
    def test_real_pinned_tarball_when_available(self):
        text, digest = scanner.read_browser_build(os.environ['E09_AXE_TARBALL_FOR_TEST'])
        self.assertEqual(digest, scanner.AXE_MIN_SHA256)
        self.assertIn('4.14.0', text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
