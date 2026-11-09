"""E09 instance interface: instance.json (the layout of experiments/E03-resetability/executor/README.md, section 6).

DRAFT (operation OP-PREP-E09). instance.json is written by the provisioning steps of the workflow before the executor
runs and is never modified here. The file names the controlled SUT-01 surfaces; the executor refuses any file whose
interface version, SUT, or record class differs from the run's.
"""
import json
import os

from . import common


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
    """sut_provenance components: identity from the provenance record, provisioning facts from instance.json."""
    env = run.env
    prov = common.read_json(env.provenance_json) if os.path.exists(env.provenance_json) else {}
    sv = prov.get('sut_version') or {}
    ip = (run.instance or {}).get('provisioning') or {}
    repo = sv.get('repository') or ip.get('repository')
    commit = sv.get('commit_sha') or ip.get('commit_sha')
    release = sv.get('release') or ip.get('release')
    csr = commit if not release else f'{commit} (release {release})'
    env_type = prov.get('environment_type') or ('LOCAL' if env.record_class == 'DEVELOPMENT' else None)
    out = []
    for name, surface in pairs:
        url = ((run.instance or {}).get('surfaces') or {}).get(surface) or {}
        out.append({'component': name, 'repository': repo, 'commit_sha_or_release': csr, 'endpoint': url.get('base_url'),
                    'environment_type': env_type})
    return out
