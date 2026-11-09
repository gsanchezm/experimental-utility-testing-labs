"""E09 executor entry point: python3 -m executor.run (called by run-condition.sh). DRAFT (operation OP-PREP-E09).

Refuses (exit 2, no manifest) on any inconsistent input; otherwise runs the attempt once and writes the bundle with
run-manifest.json last. SUCCESS, FAILURE, INCONCLUSIVE, ABORTED, and ERROR are recorded outcomes, not script failures.
"""
import importlib.metadata
import os
import platform
import re
import signal
import sys
import traceback

from . import classify, common, config, instance, scanner, sut01_catalog

EXECUTION_ID = {'MEASURED_EXPERIMENT': r'EX[0-9]{4}', 'DRY_RUN': r'DR[0-9]{4}', 'DEVELOPMENT': r'DV[0-9]{4}'}
PLAYWRIGHT_PIN = '1.63.0'
MEASURED_WORKFLOW = '/.github/workflows/e09-measured-execution.yml@'


def refuse(message):
    print(f'run refused, no manifest written: {message}', file=sys.stderr)
    return 2


def _watchdog(signum, frame):
    raise common.Watchdog(f'the run exceeded its {config.WATCHDOG_S} s budget')


def main():
    try:
        env = common.Env()
    except (KeyError, ValueError) as e:
        return refuse(f'environment: {e!r}')
    if env.record_class not in EXECUTION_ID:
        return refuse(f'RECORD_CLASS {env.record_class!r}')
    if env.record_class == 'MEASURED_EXPERIMENT' and MEASURED_WORKFLOW not in os.environ.get('GITHUB_WORKFLOW_REF', ''):
        return refuse('MEASURED_EXPERIMENT is recorded only inside .github/workflows/e09-measured-execution.yml')
    if env.condition not in config.CONDITIONS:
        return refuse(f'{env.condition} has no realization in this implementation')
    if env.sut != config.ASSIGNED_SUT:
        return refuse(f'{env.condition} is realized for {config.ASSIGNED_SUT}, not {env.sut}')
    if not re.fullmatch(EXECUTION_ID[env.record_class], env.execution_id) or env.attempt < 1:
        return refuse(f'execution id {env.execution_id!r} or attempt {env.attempt} not valid for {env.record_class}')
    if os.path.basename(env.output_dir) != env.run_id:
        return refuse(f'OUTPUT_DIR must be named after the run id {env.run_id}')
    if os.path.exists(os.path.join(env.output_dir, 'run-manifest.json')):
        return refuse('a run manifest already exists in OUTPUT_DIR: attempts are immutable')
    try:
        pw = importlib.metadata.version('playwright')
    except importlib.metadata.PackageNotFoundError:
        pw = None
    if pw != PLAYWRIGHT_PIN:
        return refuse(f'Playwright for Python {pw} is installed; the pin is {PLAYWRIGHT_PIN}')
    account = config.CONDITIONS[env.condition]['account']
    if config.ACCOUNTS.get(account) is None:
        return refuse(f'the password of {account} is not locked in the implementation (HUMAN DECISION HD-E09-A)')
    if not env.axe_tarball:
        return refuse('AXE_TARBALL is not set (the provisioning step downloads the pinned tarball)')
    try:
        axe_source, axe_member_sha256 = scanner.read_browser_build(env.axe_tarball)
    except (scanner.ScannerIntegrityError, OSError) as e:
        return refuse(f'the pinned axe-core tarball failed its check: {e}')

    run = common.Run(env)
    run.tools.update({'executor_runtime': {'tool': 'python3', 'version': platform.python_version()},
                      'api_client': {'tool': 'python3 urllib.request', 'version': platform.python_version()},
                      'scripting_runtime': {'tool': 'bash', 'version': env.bash_version}})
    run.notes.append(f'axe-core pin {scanner.AXE_VERSION}; tarball integrity {scanner.AXE_NPM_INTEGRITY}; browser build sha256 {axe_member_sha256} (verified before use)')
    if not env.bash_version:
        run.notes.append('scripting_runtime version null: EXECUTOR_BASH_VERSION was not set by run-condition.sh')
    expected = sut01_catalog.expected_text(config.CONDITIONS[env.condition]['kind'])
    accessibility_version = None
    signal.signal(signal.SIGALRM, _watchdog)
    signal.alarm(config.WATCHDOG_S)
    try:
        instance.load(run)
        result, extra = sut01_catalog.run(run, env.condition, axe_source, scanner.AXE_VERSION)
        accessibility_version = extra.get('accessibility_version')
    except common.Abort as a:
        result = common.Result('ABORTED', 'ABORTED_BEFORE_SCAN', expected, f'stopped before the scan: {a}', None)
    except common.Watchdog as w:
        result = common.Result('ERROR', 'WATCHDOG', expected, f'watchdog: {w}', None)
    except scanner.ScannerIntegrityError as e:
        result = common.Result('ERROR', 'SCANNER_INTEGRITY', expected, f'scanner integrity: {e}', None)
    except Exception as e:  # noqa: BLE001 - a runner or infrastructure fault is recorded as ERROR with a manifest
        run.log('error', traceback=traceback.format_exc())
        result = common.Result('ERROR', 'RUNNER_FAULT', expected, f'runner or infrastructure fault: {e.__class__.__name__}: {e}', None)
    finally:
        signal.alarm(0)
    if accessibility_version is None:
        run.notes.append(f'accessibility version not observed in this attempt (pin {scanner.AXE_VERSION}); recorded as null with this reason')
    toolchain = {k: v for k, v in run.tools.items() if isinstance(v, dict) and 'tool' in v}
    toolchain['accessibility'] = {'tool': 'axe-core', 'version': accessibility_version}
    run.close()
    components = instance.components(run, [('web', 'web'), ('api', 'api')]) if run.instance else []
    manifest = common.build_manifest(run, result, components, env.condition, config.CONDITIONS[env.condition]['behavior_class'],
                                     config.ROUTE_EVIDENCE, toolchain)
    common.write_manifest(run, manifest)
    print(f'{env.run_id}: {result.status} ({result.category}); matches_expected {result.matches_expected}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
