"""E09 scanner loading: verify the pinned axe-core npm tarball and read its browser build (no network, no extraction to disk).

DRAFT (operation OP-PREP-E09). Pins are copied from experiments/E09-accessibility/axe-core-pin-proposal-draft.md,
section 2 (registry dist.integrity; browser build sha256 computed from the tarball on 2026-11-06, and re-checked by the
registry metadata of the same window). The workflow downloads the tarball during provisioning; this module only reads
the local file, verifies it, and returns the browser build text. Standard library only.
"""
import base64
import hashlib
import tarfile

AXE_VERSION = '4.14.0'
AXE_NPM_INTEGRITY = 'sha512-9WTZxEjsZ7b13TH8JPmbV2z8CHbl80/2hm3XPEG4JgNdQLK81IBRXmSxHfMAOkSqQeRxT/0dwNDz2GOm3zzpcQ=='
AXE_TARBALL_URL = 'https://registry.npmjs.org/axe-core/-/axe-core-4.14.0.tgz'
AXE_MEMBER = 'package/axe.min.js'
AXE_MIN_SHA256 = '20c09fe157a8a34a30e241aaa1fcdade657734f08ab379ecfbeb7d45cc46e878'
# The options object of every run; recorded verbatim in the bundle (HUMAN DECISION HD-4, option iii).
AXE_RUN_OPTIONS = {'runOnly': {'type': 'rule', 'values': ['empty-heading']}}


class ScannerIntegrityError(Exception):
    """The tarball or the browser build does not match its pin; the run is refused before any browser starts."""


def sha512_integrity(path):
    """The npm integrity string (sha512, base64) of a local file, read in chunks."""
    h = hashlib.sha512()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return 'sha512-' + base64.b64encode(h.digest()).decode('ascii')


def read_browser_build(tarball_path, expected_integrity=None, expected_member_sha256=None):
    """Verify the tarball's sha512 against the pin, then return (text, sha256) of package/axe.min.js from inside it.

    The expected values default to the module pins; a test may pass other values for a synthetic archive.
    Raises ScannerIntegrityError on any mismatch, and when the member is absent or is not a regular file.
    """
    integrity = AXE_NPM_INTEGRITY if expected_integrity is None else expected_integrity
    member_sha = AXE_MIN_SHA256 if expected_member_sha256 is None else expected_member_sha256
    actual = sha512_integrity(tarball_path)
    if actual != integrity:
        raise ScannerIntegrityError(f'tarball sha512 {actual} does not equal the pinned integrity {integrity}')
    with tarfile.open(tarball_path, 'r:gz') as tar:
        try:
            member = tar.getmember(AXE_MEMBER)
        except KeyError as e:
            raise ScannerIntegrityError(f'{AXE_MEMBER} is absent from the tarball') from e
        if not member.isfile():
            raise ScannerIntegrityError(f'{AXE_MEMBER} is not a regular file')
        data = tar.extractfile(member).read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != member_sha:
        raise ScannerIntegrityError(f'{AXE_MEMBER} sha256 {digest} does not equal the pin {member_sha}')
    return data.decode('utf-8'), digest
