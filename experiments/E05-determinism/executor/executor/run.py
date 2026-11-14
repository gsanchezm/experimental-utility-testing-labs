"""E05-determinism executor entry point: python3 -m executor.run (called by run-condition.sh).

DRAFT (operation OP-PREP-E05). Refuses (exit 2, no record) on any inconsistent input; otherwise runs the executions of one condition on its
shared instance, one bundle per execution (run-manifest.json last in each), and one counts-only condition-summary.json. Exit status 0 when every
execution that began has a manifest (a stub counts); 1 otherwise. Recorded outcomes (RESET_, ESTABLISHMENT_, S_, INTERRUPTED_) are never errors.
"""
import importlib
import importlib.metadata
import os
import platform
import re
import signal
import sys

from . import attempt, classify, common, config, instance

MODULES = {'SUT-01': 'sut01', 'SUT-02': 'sut02', 'SUT-04': 'sut04', 'SUT-05': 'sut05'}
PLAYWRIGHT_PIN = '1.63.0'
MEASURED_WORKFLOW = '/.github/workflows/e05-measured-execution.yml@'
DRY_RUN_MAX = 3


def refuse(message):
    print(f'run refused, no record written: {message}', file=sys.stderr)
    return 2


def _watchdog(signum, frame):
    raise common.Watchdog(f'the execution exceeded its {common.WATCHDOG_S} s budget')


def check(env, cfg):
    """Return (condition, problem). A problem is a refusal."""
    if env.record_class not in common.RECORD_CLASSES:
        return None, f'RECORD_CLASS {env.record_class!r}'
    try:
        c = config.condition(cfg, env.condition)
    except config.ConfigError as e:
        return None, str(e)
    if c['sut_id'] != env.sut:
        return None, f'{env.condition} does not belong to {env.sut}'
    if env.record_class == 'MEASURED_EXPERIMENT':
        if MEASURED_WORKFLOW not in os.environ.get('GITHUB_WORKFLOW_REF', ''):
            return None, 'MEASURED_EXPERIMENT is recorded only inside .github/workflows/e05-measured-execution.yml'
        if env.executions not in (None, c['n']):
            return None, f'a measured run executes the N = {c["n"]} executions of the condition (EXECUTIONS {env.executions})'
    else:
        if env.executions is None or not 1 <= env.executions <= (DRY_RUN_MAX if env.record_class == 'DRY_RUN' else c['n']):
            return None, f'{env.record_class} needs EXECUTIONS between 1 and {DRY_RUN_MAX if env.record_class == "DRY_RUN" else c["n"]}'
    last = env.executions if env.executions is not None else c['n']
    if env.attempt < 1 or not 1 <= env.first <= last:
        return None, f'ATTEMPT {env.attempt} or FIRST_EXECUTION {env.first} not valid'
    return c, None


def main():
    try:
        env = common.Env()
        cfg = config.load()
    except (KeyError, ValueError, config.ConfigError) as e:
        return refuse(f'environment or configuration: {e!r}')
    c, problem = check(env, cfg)
    if problem:
        return refuse(problem)
    mod = importlib.import_module(f'executor.{MODULES[env.sut]}') if env.sut in MODULES else None
    cls = mod.REALIZATIONS.get(env.condition) if mod else None
    if cls is None:
        return refuse(f'{env.condition} has no realization in this implementation')
    if not cls.SPEC.configured:
        return refuse(f'{env.condition} is not configured (a value the START package decides is missing; see the module docstring)')
    for i in range(env.first, (env.executions or c['n']) + 1):
        if os.path.exists(os.path.join(env.output_dir, 'executions', env.run_id(i), 'run-manifest.json')):
            return refuse(f'{env.run_id(i)} already has a run manifest: attempts are immutable')
    if c['surface'] == 'web':
        try:
            pw = importlib.metadata.version('playwright')
        except importlib.metadata.PackageNotFoundError:
            pw = None
        if pw != PLAYWRIGHT_PIN:
            return refuse(f'Playwright for Python {pw} is installed; the pin is {PLAYWRIGHT_PIN}')
    job = common.Job(env, cfg, c)
    job.tools.update({'executor_runtime': {'tool': 'python3', 'version': platform.python_version()},
                      'api_client': {'tool': 'python3 urllib.request', 'version': platform.python_version()},
                      'scripting_runtime': {'tool': 'bash', 'version': env.bash_version}})
    if not env.bash_version:
        job.notes.append('scripting_runtime version null: EXECUTOR_BASH_VERSION was not set by run-condition.sh')
    try:
        instance.load(job)
    except (OSError, ValueError) as e:
        return refuse(f'instance.json: {e!r}')
    os.makedirs(os.path.join(env.output_dir, 'executions'), exist_ok=True)
    signal.signal(signal.SIGALRM, _watchdog)
    results = attempt.run_job(job, cls(job))
    missing = [r['run_id'] for r in results if not os.path.exists(os.path.join(env.output_dir, 'executions', r['run_id'], 'run-manifest.json'))]
    print(f'{env.condition}: {len(results)} executions; {len(missing)} without a manifest')
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
