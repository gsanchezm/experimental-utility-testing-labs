"""E07-cross-layer-continuity executor: the instance interface (instance.json).

DRAFT (operation OP-PREP-E07-04; derived from the E04 executor by copying). instance.json is written before run-condition.sh runs
(provisioning steps, a DRY_RUN step, or by hand for DEVELOPMENT) and is never modified on disk. The format is that of
experiments/E05-determinism/executor/README.md, section 3, unchanged: interface_version 1, sut_id, record_class, surfaces.<name>.base_url,
provisioning, logs. The `process` block is not read: no E07 reset restarts a process (D-E07-8), so the restart sequence of the E04 module is
not part of this one. For SUT-01 surfaces.api and surfaces.web are read; for SUT-04 surfaces.api (the booking service), surfaces.auth (the auth
service) and surfaces.web are read.
"""
import json
import os
import socket

from . import common

LOG_TAIL_BYTES = 1 << 20


def load(job):
    path = job.env.instance_json
    with open(path, 'rb') as f:
        raw = f.read()
    inst = json.loads(raw.decode('utf-8'))
    problems = []
    if inst.get('interface_version') != 1:
        problems.append(f'interface_version {inst.get("interface_version")!r} (expected 1)')
    if inst.get('sut_id') != job.env.sut:
        problems.append(f'sut_id {inst.get("sut_id")!r} differs from ASSIGNED_SUT {job.env.sut}')
    if inst.get('record_class') != job.env.record_class:
        problems.append(f'record_class {inst.get("record_class")!r} differs from RECORD_CLASS {job.env.record_class}')
    if problems:
        raise ValueError('instance.json rejected: ' + '; '.join(problems))
    job.instance = inst
    job.instance_sha256 = common.sha256_file(path)
    return inst


def write_evidence(run):
    """The instance interface, as read at the start of the job, is evidence of every execution."""
    run.jsonfile('instance', run.job.instance)


def base(inst, surface):
    url = ((inst.get('surfaces') or {}).get(surface) or {}).get('base_url')
    if not url:
        raise ValueError(f'instance.json has no surfaces.{surface}.base_url')
    return url.rstrip('/')


def components(run, pairs):
    """sut_provenance components: identity from the provenance record (manifests/sut-manifest.yaml through the workflow),
    provisioning facts from instance.json; the commit is cross-checked against manifests/sut-manifest.yaml."""
    env, job = run.env, run.job
    prov = common.read_json(env.provenance_json) if os.path.exists(env.provenance_json) else {}
    sv = prov.get('sut_version') or {}
    ip = (job.instance or {}).get('provisioning') or {}
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
        url = ((job.instance or {}).get('surfaces') or {}).get(surface) or {}
        out.append({'component': name, 'repository': repo, 'commit_sha_or_release': csr, 'endpoint': url.get('base_url'), 'environment_type': env_type})
    return out


def port_open(port, host='127.0.0.1', timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def collect_logs(job, directory):
    """Copy the tail of the SUT logs named in instance.json into the job-level directory, scrubbed."""
    os.makedirs(directory, exist_ok=True)
    for path in (job.instance or {}).get('logs') or []:
        name = os.path.basename(path)
        try:
            with open(path, 'rb') as f:
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(0, size - LOG_TAIL_BYTES))
                data = f.read().decode('utf-8', 'replace')
            with open(os.path.join(directory, 'sut-log-' + name), 'w', encoding='utf-8') as f:
                f.write(job.scrub(data))
        except OSError as e:
            job.notes.append(f'SUT log not copied ({name}): {e.__class__.__name__}')
