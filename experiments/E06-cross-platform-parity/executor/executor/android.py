"""E06-cross-platform-parity executor: the Android side in Python (APK verification, clean install, and the call of the Node harness).

DRAFT (operation OP-PREP-E06-EXECUTOR). The WebDriver session, the taps, and the page reads of one execution are in
harness/e06-android.mjs (a Node.js process per execution, talking to an Appium 3.7.0 server over HTTP). This module does the parts that
are not WebDriver: it checks the APK digest before any device action, uninstalls the application before each execution (the clean
install of CS-007's reset realization), writes the harness input to a temporary file outside the repository (the password never
appears on a command line), and reads back the harness record, whose identity is parsed again here from the kept page source.
"""
import base64
import json
import os
import subprocess
import tempfile

from . import common

HARNESS_FILE = 'e06-android.mjs'
HARNESS_TIMEOUT_S = 900
ADB_TIMEOUT_S = 120


class ApkError(Exception):
    """The APK on disk does not match the pinned digest; no device action is taken."""


class HarnessFault(Exception):
    """The harness process ended without a record (the execution is a RUNNER fault)."""


def verify_apk(path, expected_sha256):
    if not path or not os.path.isfile(path):
        raise ApkError('the APK file is absent')
    actual = common.sha256_file(path)
    if actual != expected_sha256:
        raise ApkError('the APK digest differs from the pinned value')
    return actual


def adb(env, *args):
    """One adb call with a bounded wait; returns (exit status, combined output). Never raises on a non-zero status."""
    cmd = [env.adb_bin]
    if env.udid:
        cmd += ['-s', env.udid]
    cmd += list(args)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=ADB_TIMEOUT_S)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def uninstall(env, package):
    """adb uninstall of the package before an execution. An absent package is a no-op, recorded as such."""
    status, output = adb(env, 'uninstall', package)
    return {'package': package, 'exit_status': status, 'output': output, 'was_installed': status == 0 and 'Success' in output}


def run_harness(env, scrub, condition, index, *, username, password, app_package, launch, budget_ms):
    """One execution through the Node harness; returns the parsed harness record (never raises on an application outcome).

    Raises HarnessFault when the process could not produce a record (a missing node binary, a crash, or a timeout)."""
    harness = os.path.join(env.harness_dir, HARNESS_FILE)
    if not os.path.isfile(harness):
        raise HarnessFault('the Android harness file is absent')
    if not env.appium_url:
        raise HarnessFault('APPIUM_SERVER_URL is not set')
    workdir = tempfile.mkdtemp(prefix='e06-harness-')
    input_path = os.path.join(workdir, 'input.json')
    output_path = os.path.join(workdir, 'record.json')
    payload = {'sut_id': condition['sut_id'], 'app_package': app_package, 'launch': launch, 'username': username, 'password': password,
               'identity_oracle': env.expected_identity_oracle, 'index': index, 'budget_ms': budget_ms,
               'apk_path': env.apk_path, 'udid': env.udid, 'appium_url': env.appium_url}
    try:
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f)
        cmd = [env.node_bin, harness, f'--input={input_path}', f'--out={output_path}']
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=HARNESS_TIMEOUT_S, cwd=env.harness_dir)
        except subprocess.TimeoutExpired as e:
            raise HarnessFault(f'the harness exceeded {HARNESS_TIMEOUT_S} s') from e
        if not os.path.isfile(output_path):
            tail = scrub((proc.stderr or proc.stdout or '')[-800:])
            raise HarnessFault(f'the harness wrote no record (exit status {proc.returncode}): {tail}')
        with open(output_path, encoding='utf-8') as f:
            record = json.load(f)
        record['harness_exit_status'] = proc.returncode
        return record
    finally:
        for name in (input_path, output_path):
            try:
                os.remove(name)
            except OSError:
                pass
        try:
            os.rmdir(workdir)
        except OSError:
            pass


def screenshot_bytes(record):
    """The terminal screenshot of the harness record (PNG bytes), or None when the harness captured none."""
    data = record.get('screenshot_png_base64')
    if not data:
        return None
    return base64.b64decode(data)
