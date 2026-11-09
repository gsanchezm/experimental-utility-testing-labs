"""E09 environment verification (ENVIRONMENT_VERIFICATION; never measured, never imported): python3 -m executor.verify.

DRAFT (operation OP-PREP-E09). Checks the controlled SUT-01 instance and the activation path before any measured
dispatch: the instance interface, the pinned axe-core tarball, the control account's login behavior, the glitch
account's login behavior (only when its password is locked), and, in a browser, one load of the Catalog page per
account with one explicit-rule axe run. Writes verification.json; writes no run manifest and nothing under raw-data/.
Exit 0 only when every check passed; any FAIL or NOT_VERIFIED exits 1, so the workflow job reports it.
"""
import importlib.metadata
import json
import os
import platform
import sys
import traceback

from . import classify, common, config, instance, scanner, sut01_catalog, web


def main():
    try:
        env = common.Env()
    except (KeyError, ValueError) as e:
        print(f'verification refused: environment {e!r}', file=sys.stderr)
        return 2
    if env.record_class != 'ENVIRONMENT_VERIFICATION':
        print('verification refused: RECORD_CLASS must be ENVIRONMENT_VERIFICATION', file=sys.stderr)
        return 2
    if not env.axe_tarball:
        print('verification refused: AXE_TARBALL is not set', file=sys.stderr)
        return 2
    run = common.Run(env)
    checks = []

    def check(name, status, detail):
        checks.append({'check': name, 'result': status, 'detail': detail})
        run.log('check', name=name, result=status)

    try:
        instance.load(run)
        check('instance interface and record class', 'PASS', f'sha256 {run.instance_sha256}')
    except Exception as e:  # noqa: BLE001 - recorded as FAIL
        check('instance interface and record class', 'FAIL', f'{e.__class__.__name__}: {e}')
    try:
        axe_source, member_sha = scanner.read_browser_build(env.axe_tarball)
        check('pinned axe-core tarball (sha512) and browser build (sha256)', 'PASS', f'{scanner.AXE_NPM_INTEGRITY}; {member_sha}')
    except (scanner.ScannerIntegrityError, OSError) as e:
        axe_source = None
        check('pinned axe-core tarball (sha512) and browser build (sha256)', 'FAIL', str(e))
    if run.instance is None:
        return finish(run, checks, env)
    api, site = instance.base(run.instance, 'api'), instance.base(run.instance, 'web')
    try:
        status, rbody, error = sut01_catalog.Http(run).call('GET', f'{api}/health', label='health')[0:3]
        check('api health endpoint answers 200', 'PASS' if status == 200 else 'FAIL', f'status {status} {error or ""}'.strip())
    except Exception as e:  # noqa: BLE001
        check('api health endpoint answers 200', 'FAIL', f'{e.__class__.__name__}: {e}')
    accounts = []
    for condition, spec in config.CONDITIONS.items():
        accounts.append((condition, spec['kind'], spec['account']))
    logged = {}
    for condition, kind, account in accounts:
        password = config.ACCOUNTS.get(account)
        if password is None:
            check(f'login behavior of {account} ({condition})', 'NOT_VERIFIED', 'password not locked in the implementation (HUMAN DECISION HD-E09-A)')
            continue
        token, body, status = sut01_catalog.login(run, api, account, password)
        confirmed = bool(token) and classify.activation_confirmed(kind, body.get('behavior'))
        check(f'login behavior of {account} ({condition})', 'PASS' if confirmed else 'FAIL',
              f"status {status}; behavior {body.get('behavior')!r}; activation confirmed {confirmed}")
        if confirmed:
            logged[condition] = (token, body)
    if axe_source is None:
        return finish(run, checks, env)
    browser_ok = False
    for condition, (token, body) in logged.items():
        kind = config.CONDITIONS[condition]['kind']
        try:
            b = web.Browser(run)
        except Exception as e:  # noqa: BLE001 - recorded as FAIL below
            check(f'browser start for {condition}', 'FAIL', f'{e.__class__.__name__}: {e}')
            continue
        browser_ok = True
        try:
            b.goto(site + '/')
            sut01_catalog.seed_client_state(b, token, body)
            status = b.goto(site + config.CATALOG_PATH)
            b.page.locator('h2[data-testid^="pizza-name-"]').first.wait_for(state='attached', timeout=config.ACTION_TIMEOUT_MS)
        except Exception:  # noqa: BLE001 - the DOM state below records what rendered
            status = None
        try:
            records = b.page.evaluate(sut01_catalog.DOM_RECORDS_JS)
            dom, _detail = classify.dom_state(records)
            version, result = sut01_catalog.read_scan(b, run, axe_source, scanner.AXE_VERSION)
            matches = classify.matching_nodes(result)
            check(f'catalog load, DOM state and explicit-rule axe run for {condition}', 'PASS' if version == scanner.AXE_VERSION else 'FAIL',
                  f'catalog status {status}; DOM state {dom}; axe {version}; matching nodes {len(matches)}')
        except Exception as e:  # noqa: BLE001
            check(f'catalog load, DOM state and explicit-rule axe run for {condition}', 'FAIL', f'{e.__class__.__name__}: {e}')
        finally:
            b.close()
    if not browser_ok and logged:
        check('browser available', 'FAIL', 'no Chromium context could be started')
    if not logged:
        check('catalog load and explicit-rule axe run', 'NOT_VERIFIED', 'no account with a locked password and a confirmed activation')
    return finish(run, checks, env)


def finish(run, checks, env):
    verified = bool(checks) and all(c['result'] == 'PASS' for c in checks)
    record = {'record_class': 'ENVIRONMENT_VERIFICATION', 'run_id': env.run_id, 'sut_id': env.sut, 'verified': verified,
              'checks': checks, 'python': platform.python_version(), 'playwright': _pw_version(),
              'axe_pin': {'version': scanner.AXE_VERSION, 'npm_integrity': scanner.AXE_NPM_INTEGRITY}}
    with open(os.path.join(run.out, 'verification.json'), 'w', encoding='utf-8') as f:
        f.write(run.scrub(json.dumps(record, indent=2, ensure_ascii=False)))
    run.close()
    print(json.dumps({'verified': verified, 'checks': [(c['check'], c['result']) for c in checks]}, indent=2))
    return 0 if verified else 1


def _pw_version():
    try:
        return importlib.metadata.version('playwright')
    except importlib.metadata.PackageNotFoundError:
        return None


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - an unexpected fault exits non-zero with its traceback in the log
        traceback.print_exc()
        sys.exit(1)
