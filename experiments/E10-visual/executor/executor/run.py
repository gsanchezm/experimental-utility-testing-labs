"""E10-visual executor entry point: python3 -m executor.run (called by run-condition.sh).

DRAFT (operation OP-PREP-E10). Refuses (exit 2, no record) on any inconsistent input, including a comparison instrument that cannot be
prepared (the Pixelmatch pin does not match, Node.js is absent) and a measured run whose thresholds are not calibrated; otherwise runs the
executions of one condition on its shared instance, one bundle per execution (run-manifest.json last in each), and one counts-only
condition-summary.json. Exit status 0 when every execution that began has a manifest (a stub counts); 1 otherwise. Recorded outcomes
(START_, INCONCLUSIVE_, INTERRUPTED_, NOT_DETECTED) are never errors.
"""
import importlib
import os
import platform
import signal
import sys

from . import attempt, capture, common, compare, config, instance

MODULES = {'SUT-01': 'sut01', 'SUT-02': 'sut02', 'SUT-03': 'sut03'}
MEASURED_WORKFLOW = '/.github/workflows/e10-measured-execution.yml@'
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
            return None, 'MEASURED_EXPERIMENT is recorded only inside .github/workflows/e10-measured-execution.yml'
        if env.executions not in (None, cfg['n_per_condition']):
            return None, f'a measured run executes the N = {cfg["n_per_condition"]} executions of the condition (EXECUTIONS {env.executions})'
        if config.thresholds(cfg, c)['provisional']:
            return None, 'a measured run needs the calibrated thresholds T_R and T_e (the calibration record); the floors are for DRY_RUN and DEVELOPMENT only'
    else:
        limit = DRY_RUN_MAX if env.record_class == 'DRY_RUN' else cfg['n_per_condition']
        if env.executions is None or not 1 <= env.executions <= limit:
            return None, f'{env.record_class} needs EXECUTIONS between 1 and {limit}'
    last = env.executions if env.executions is not None else cfg['n_per_condition']
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
    for i in range(env.first, (env.executions or cfg['n_per_condition']) + 1):
        if os.path.exists(os.path.join(env.output_dir, 'executions', env.run_id(i), 'run-manifest.json')):
            return refuse(f'{env.run_id(i)} already has a run manifest: attempts are immutable')
    job = common.Job(env, cfg, c)
    job.tools.update({'executor_runtime': {'tool': 'python3', 'version': platform.python_version()},
                      'scripting_runtime': {'tool': 'bash', 'version': env.bash_version}})
    if env.sut == 'SUT-01':
        job.tools['api_client'] = {'tool': 'python3 urllib.request', 'version': platform.python_version()}
    if not env.bash_version:
        job.notes.append('scripting_runtime version null: EXECUTOR_BASH_VERSION was not set by run-condition.sh')
    try:
        instance.load(job)
    except (OSError, ValueError) as e:
        return refuse(f'instance.json: {e!r}')
    try:
        job.comparator = compare.Comparator.prepare()
    except compare.CompareError as e:
        return refuse(f'the comparison instrument: {e}')
    job.tools['comparison_runtime'] = {'tool': 'Node.js', 'version': job.comparator.node_version}
    pin = job.comparator.pin
    job.notes.append(f'comparison instrument: Pixelmatch {compare.PIXELMATCH_VERSION} (tarball sha256 {pin["tarball_sha256"]}, {compare.PIXELMATCH_MEMBER} sha256 {pin["index_sha256"]}), '
                     f'run by Node.js {job.comparator.node_version} with options {compare.PIXELMATCH_OPTIONS}; capture version {capture.CAPTURE_VERSION}; '
                     f'runner sha256 {job.comparator.runner_sha256}')
    os.makedirs(os.path.join(env.output_dir, 'executions'), exist_ok=True)
    signal.signal(signal.SIGALRM, _watchdog)
    results = attempt.run_job(job, cls(job))
    missing = [r['run_id'] for r in results if not os.path.exists(os.path.join(env.output_dir, 'executions', r['run_id'], 'run-manifest.json'))]
    print(f'{env.condition}: {len(results)} executions; {len(missing)} without a manifest')
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
