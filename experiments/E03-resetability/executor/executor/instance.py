"""E03-resetability executor: the instance interface (instance.json, README section 6) and the SUT-05 process restart.

DRAFT (operation OP-PREP-E03). instance.json is written before run-condition.sh runs (provisioning steps, a DRY_RUN step,
or by hand for DEVELOPMENT) and is never modified here. The restart follows the OP-CI-02 verification step: SIGTERM to the
whole process group, the port must refuse connections before the start, the start in a new session and process group,
readiness before the verification, process trees before the stop, after it, and after the restart kept as evidence.
"""
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

from . import common

LOG_TAIL_BYTES = 1 << 20


def load(run):
    path = run.env.instance_json
    with open(path, 'rb') as f:
        raw = f.read()
    inst = json.loads(raw.decode('utf-8'))
    problems = []
    if inst.get('interface_version') != 1:
        problems.append(f'interface_version {inst.get("interface_version")!r} (expected 1)')
    if inst.get('sut_id') != run.env.sut:
        problems.append(f'sut_id {inst.get("sut_id")!r} differs from ASSIGNED_SUT {run.env.sut}')
    if inst.get('record_class') != run.env.record_class:
        problems.append(f'record_class {inst.get("record_class")!r} differs from RECORD_CLASS {run.env.record_class}')
    if problems:
        raise ValueError('instance.json rejected: ' + '; '.join(problems))
    run.instance = inst
    run.instance_sha256 = common.sha256_file(path)
    run.jsonfile('instance', inst)
    run.log('instance', sha256=run.instance_sha256)
    return inst


def base(inst, surface):
    url = ((inst.get('surfaces') or {}).get(surface) or {}).get('base_url')
    if not url:
        raise ValueError(f'instance.json has no surfaces.{surface}.base_url')
    return url.rstrip('/')


def components(run, pairs):
    """sut_provenance components: identity from the provenance record (manifests/sut-manifest.yaml through the workflow),
    provisioning facts from instance.json; the commit is cross-checked against manifests/sut-manifest.yaml."""
    env = run.env
    prov = common.read_json(env.provenance_json) if os.path.exists(env.provenance_json) else {}
    sv = prov.get('sut_version') or {}
    ip = (run.instance or {}).get('provisioning') or {}
    repo = sv.get('repository') or ip.get('repository')
    commit = sv.get('commit_sha') or ip.get('commit_sha')
    release = sv.get('release') or ip.get('release')
    if sv.get('commit_sha') and ip.get('commit_sha') and sv['commit_sha'] != ip['commit_sha']:
        run.notes.append(f'provenance commit {sv["commit_sha"]} differs from the instance.json commit {ip["commit_sha"]}')
    manifest = os.path.join(env.executor_dir, '..', '..', '..', 'manifests', 'sut-manifest.yaml')
    if commit and os.path.exists(manifest):
        with open(manifest, encoding='utf-8') as f:
            found = commit in f.read()
        run.notes.append(f'sut commit {commit} {"found" if found else "NOT found"} in manifests/sut-manifest.yaml')
    csr = commit if not release else f'{commit} (release {release})'
    asset = ip.get('asset') or {}
    if asset.get('name'):
        csr += f'; provisioning route {ip.get("route")}: asset {asset.get("name")} sha256 {asset.get("sha256")}'
    env_type = prov.get('environment_type') or ('LOCAL' if env.record_class == 'DEVELOPMENT' else None)
    out = []
    for name, surface in pairs:
        url = ((run.instance or {}).get('surfaces') or {}).get(surface) or {}
        out.append({'component': name, 'repository': repo, 'commit_sha_or_release': csr, 'endpoint': url.get('base_url'), 'environment_type': env_type})
    return out


def port_open(port, host='127.0.0.1', timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _ps():
    cmd = ['ps', '-eo', 'pid,ppid,pgid,sid,stat,etimes,args'] if sys.platform.startswith('linux') else ['ps', '-axo', 'pid,ppid,pgid,stat,etime,command']
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
    except Exception as e:  # noqa: BLE001 - evidence only
        return f'ps unavailable: {e!r}'


def _listeners(port):
    cmd = ['ss', '-ltnp'] if sys.platform.startswith('linux') else ['lsof', '-nP', f'-iTCP:{port}', '-sTCP:LISTEN']
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
    except Exception as e:  # noqa: BLE001 - evidence only
        return f'listener query unavailable: {e!r}'
    return '\n'.join(l for l in out.splitlines() if f':{port}' in l or l.startswith(('State', 'COMMAND')))


def _tree(run, label, port):
    return run.text(label, _ps() + f'\n# listeners on port {port}\n' + _listeners(port) + '\n')


def _status(url, timeout=10):
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(url, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # noqa: BLE001 - a refused or reset connection is an observation
        return f'ERROR:{e.__class__.__name__}'


def restart(run, a):
    """SUT-05 reset action (README section 4.7): one reset action; its evidence records the stop, port-refused, start, and readiness times."""
    p = (run.instance or {}).get('process') or {}
    for k in ('pgid', 'start_command', 'cwd', 'port', 'readiness_url', 'readiness_timeout_s', 'stop_timeout_s'):
        if p.get(k) in (None, '', []):
            raise ValueError(f'instance.json process.{k} is missing')
    pgid, port = int(p['pgid']), int(p['port'])
    url = base(run.instance, 'api') + p['readiness_url']
    obs = {}
    a['evidence'].append(_tree(run, 'process-tree-before-stop', port))
    t = common.utcnow()
    try:
        os.killpg(pgid, signal.SIGTERM)
        obs['stop_signal'] = f'SIGTERM to process group {pgid}'
    except ProcessLookupError as e:
        obs['stop_signal'] = f'process group {pgid} not found: {e}'
    obs['stop_sent_at'] = common.stamp(t)
    deadline, polls, refused = time.monotonic() + float(p['stop_timeout_s']), 0, None
    while time.monotonic() < deadline:
        polls += 1
        if not port_open(port):
            refused = common.utcnow()
            break
        time.sleep(0.5)
    obs['port_refused_at'] = common.stamp(refused) if refused else None
    obs['port_polls'] = polls
    a['evidence'].append(_tree(run, 'process-tree-after-stop', port))
    if refused is None:
        obs['start'] = 'NOT_ATTEMPTED: the port still accepted connections at the end of the stop budget'
        a['observation'] = obs
        a['outcome'] = 'FAILURE'
        return
    logdir = tempfile.mkdtemp(prefix='e03-sut05-restart-')
    out_path, err_path = os.path.join(logdir, 'stdout-restart.log'), os.path.join(logdir, 'stderr-restart.log')
    env = dict(os.environ)
    env.update({str(k): str(v) for k, v in (p.get('env') or {}).items()})
    t = common.utcnow()
    with open(out_path, 'wb') as fo, open(err_path, 'wb') as fe:
        proc = subprocess.Popen([str(x) for x in p['start_command']], cwd=p['cwd'], env=env, stdin=subprocess.DEVNULL,
                                stdout=fo, stderr=fe, start_new_session=True)
    obs['start_at'] = common.stamp(t)
    obs['new_pid'], obs['new_pgid'] = proc.pid, os.getpgid(proc.pid)
    run.restarted_logs = [out_path, err_path]
    deadline, polls, ready, last = time.monotonic() + float(p['readiness_timeout_s']), 0, None, None
    while time.monotonic() < deadline:
        polls += 1
        if proc.poll() is not None:
            obs['exited_early_with'] = proc.returncode
            break
        last = _status(url)
        if last == 200:
            ready = common.utcnow()
            break
        time.sleep(1.0)
    obs['ready_at'] = common.stamp(ready) if ready else None
    obs['readiness_polls'], obs['last_readiness_status'] = polls, last
    a['evidence'].append(_tree(run, 'process-tree-after-restart', port))
    a['observation'] = obs
    a['outcome'] = 'SUCCESS' if ready else 'FAILURE'


def collect_logs(run):
    """Copy the tail of the SUT logs named in instance.json (and of a restarted process) into evidence/, scrubbed."""
    paths = list((run.instance or {}).get('logs') or []) + list(getattr(run, 'restarted_logs', []) or [])
    for path in paths:
        try:
            with open(path, 'rb') as f:
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(0, size - LOG_TAIL_BYTES))
                data = f.read().decode('utf-8', 'replace')
            run.text('sut-log-' + os.path.basename(path), data, 'log')
        except OSError as e:
            run.notes.append(f'SUT log not copied ({os.path.basename(path)}): {e.__class__.__name__}')
