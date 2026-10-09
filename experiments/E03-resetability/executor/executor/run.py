"""E03-resetability executor entry point: python3 -m executor.run (called by run-condition.sh).

DRAFT (operation OP-PREP-E03). Refuses (exit 2, no manifest) on any inconsistent input; otherwise runs the condition
once and writes the bundle, with run-manifest.json last, whatever the outcome (SUCCESS, FAILURE, INCONCLUSIVE, ABORTED,
or ERROR are recorded results, not script failures).
"""
import importlib
import importlib.metadata
import os
import platform
import re
import signal
import sys
import traceback

from . import common, instance

CONDITIONS = {
    'E03-CS001-SUT01-API': 'sut01_api', 'E03-CS001-SUT01-WEB': 'sut01_web', 'E03-CS001-SUT02-WEB': 'sut02_web',
    'E03-CS001-SUT03-WEB': 'sut03_web', 'E03-CS001-SUT04-API': 'sut04_api', 'E03-CS001-SUT04-WEB': 'sut04_web',
    'E03-CS001-SUT05-API': 'sut05_api',
}
PLAYWRIGHT_PIN = '1.63.0'
WATCHDOG_S = 900
EXECUTION_ID = {'MEASURED_EXPERIMENT': r'EX[0-9]{4}', 'DRY_RUN': r'DR[0-9]{4}', 'DEVELOPMENT': r'DV[0-9]{4}'}


def refuse(message):
    print(f'run refused, no manifest written: {message}', file=sys.stderr)
    return 2


def _watchdog(signum, frame):
    raise common.Watchdog(f'the run exceeded its {WATCHDOG_S} s budget')


def main():
    try:
        env = common.Env()
    except (KeyError, ValueError) as e:
        return refuse(f'environment: {e!r}')
    if env.record_class not in common.RECORD_CLASSES:
        return refuse(f'RECORD_CLASS {env.record_class!r}')
    if env.record_class == 'MEASURED_EXPERIMENT' and '/.github/workflows/e03-measured-execution.yml@' not in os.environ.get('GITHUB_WORKFLOW_REF', ''):
        return refuse('MEASURED_EXPERIMENT is recorded only inside .github/workflows/e03-measured-execution.yml')
    if env.condition not in CONDITIONS:
        return refuse(f'{env.condition} has no realization in this implementation')
    if env.condition.split('-')[2] != env.sut.replace('-', ''):
        return refuse(f'{env.condition} does not belong to {env.sut}')
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
    run = common.Run(env)
    run.tools.update({'executor_runtime': {'tool': 'python3', 'version': platform.python_version()},
                      'api_client': {'tool': 'python3 urllib.request', 'version': platform.python_version()},
                      'scripting_runtime': {'tool': 'bash', 'version': env.bash_version}})
    if not env.bash_version:
        run.notes.append('scripting_runtime version null: EXECUTOR_BASH_VERSION was not set by run-condition.sh')
    mod = importlib.import_module(f'executor.{CONDITIONS[env.condition]}')
    signal.signal(signal.SIGALRM, _watchdog)
    signal.alarm(WATCHDOG_S)
    try:
        instance.load(run)
        result = mod.run(run)
    except common.Abort as a:
        result = common.Result('ABORTED', mod.EXPECTED, f'stopped before the first reset-side action: {a}', mod.RESET_MECHANISMS, mod.ESTABLISHMENT_MECHANISMS)
    except common.Watchdog as w:
        result = common.Result('ERROR', mod.EXPECTED, f'watchdog: {w}', mod.RESET_MECHANISMS, mod.ESTABLISHMENT_MECHANISMS)
    except Exception as e:  # noqa: BLE001 - a runner or infrastructure fault is recorded as ERROR with a manifest
        run.log('error', traceback=traceback.format_exc())
        result = common.Result('ERROR', mod.EXPECTED, f'runner or infrastructure fault: {e.__class__.__name__}: {e}', mod.RESET_MECHANISMS, mod.ESTABLISHMENT_MECHANISMS)
    finally:
        signal.alarm(0)
    if result.status == 'ABORTED' and run.actions:
        result.status = 'ERROR'
        result.notes.append('an abort after a reset-side action is a design error; recorded as ERROR')
    instance.collect_logs(run)
    run.write_records(result)
    components = mod.components(run) if run.instance else []
    run.log('run-end', status=result.status, actions=len(run.actions))
    run.close()  # executor.log is complete before the manifest hashes it
    common.write_manifest(run, common.build_manifest(run, result, mod.MODALITY, mod.PLATFORM, components))
    print(f'{env.run_id}: {result.status}; actions {[(a["class"], a["outcome"]) for a in run.actions]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
