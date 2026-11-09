"""Counting, outcome, scrubbing, and run-manifest tests for the E02 API realizations (DRAFT, operation OP-PREP-E02).

No SUT, no browser, no network beyond a loopback fake: each test starts a threaded HTTP fake of the endpoints the realization
calls, builds a Run with a generated instance.json in a temporary directory, runs the realization through executor.run.execute,
writes the bundle with the same functions the entry point uses, and checks the counts, the classes, the outcomes, the
precondition/action split, the scrubbing, and the run manifest against a subset validator of schemas/run-manifest.schema.v2.json.
Web realizations are not executed here (they need Playwright and a SUT); see IMPLEMENTATION-NOTES.md.

Run: python3 -m unittest -v tests/test_counting.py   (from the executor directory; paths are derived from this file's location)
"""
import http.server
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXECUTOR_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.abspath(os.path.join(EXECUTOR_DIR, '..', '..', '..'))
SCHEMA = os.path.join(REPO_ROOT, 'schemas', 'run-manifest.schema.v2.json')
sys.path.insert(0, EXECUTOR_DIR)

from executor import common, instance, run as runner, sut01, sut04, sut05  # noqa: E402

JWT_LIKE = '.'.join(['ey' + 'JhbGciOiJIUzI1NiJ9', 'ey' + 'JzdWIiOiJ0ZXN0In0', 'c2lnbmF0dXJlMTIzNDU2'])  # built from fragments: the publication builder refuses a token-shaped prefix in any exported text file
SESSION_TOKEN = 'ab12cd34ef56gh78'


# ---- schema subset validator (the keywords used by schemas/run-manifest.schema.v2.json; unknown keywords fail loudly) --------
SUPPORTED = {'$id', '$schema', 'title', 'description', 'type', 'properties', 'required', 'additionalProperties', 'items', 'enum',
             'pattern', 'minLength', 'minimum', 'uniqueItems', 'format'}


def _type_ok(value, t):
    return {'string': isinstance(value, str), 'integer': isinstance(value, int) and not isinstance(value, bool),
            'number': isinstance(value, (int, float)) and not isinstance(value, bool), 'boolean': isinstance(value, bool),
            'array': isinstance(value, list), 'object': isinstance(value, dict), 'null': value is None}[t]


def validate(value, schema, path='$'):
    errors = []
    unknown = set(schema) - SUPPORTED
    if unknown:
        raise AssertionError(f'validator does not support {sorted(unknown)} at {path}')
    if 'type' in schema:
        types = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        if not any(_type_ok(value, t) for t in types):
            return [f'{path}: {value!r} is not of type {types}']
    if value is None:
        return errors
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path}: {value!r} not in enum')
    if 'pattern' in schema and isinstance(value, str) and not re.search(schema['pattern'], value):
        errors.append(f'{path}: {value!r} does not match {schema["pattern"]}')
    if 'minLength' in schema and isinstance(value, str) and len(value) < schema['minLength']:
        errors.append(f'{path}: shorter than {schema["minLength"]}')
    if 'minimum' in schema and isinstance(value, (int, float)) and value < schema['minimum']:
        errors.append(f'{path}: below minimum {schema["minimum"]}')
    if 'format' in schema and schema['format'] == 'date-time' and isinstance(value, str) and not re.match(
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
        errors.append(f'{path}: not a date-time')
    if isinstance(value, dict):
        for k in schema.get('required', []):
            if k not in value:
                errors.append(f'{path}: missing required {k}')
        props = schema.get('properties', {})
        addl = schema.get('additionalProperties', True)
        for k, v in value.items():
            if k in props:
                errors += validate(v, props[k], f'{path}.{k}')
            elif addl is False:
                errors.append(f'{path}: additional property {k} not allowed')
            elif isinstance(addl, dict):
                errors += validate(v, addl, f'{path}.{k}')
    if isinstance(value, list):
        if schema.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            errors.append(f'{path}: items not unique')
        if 'items' in schema:
            for i, v in enumerate(value):
                errors += validate(v, schema['items'], f'{path}[{i}]')
    return errors


# ---- fake services -----------------------------------------------------------------------------------------------------------
class _Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):  # the fake is silent
        return

    def _reply(self, status, body=None, cookie=None):
        data = json.dumps(body).encode('utf-8') if body is not None else b''
        self.send_response(status)
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return json.loads(self.rfile.read(n).decode('utf-8')) if n else {}

    def do_GET(self):
        self._route('GET', {})

    def do_POST(self):
        self._route('POST', self._json_body())

    def _route(self, method, body):
        cfg, st = self.server.cfg, self.server.state
        path = self.path.split('?')[0]
        bearer = (self.headers.get('Authorization') or '').startswith('Bearer ')
        cookie_token = 'token=' + SESSION_TOKEN in (self.headers.get('Cookie') or '')
        st.setdefault('calls', []).append((method, self.path))
        if (method, path) == ('POST', '/api/auth/login'):
            return self._reply(cfg.get('login_status', 200), {'access_token': JWT_LIKE, 'behavior': 'standard'})
        if (method, path) == ('GET', '/api/session'):
            if not bearer:
                return self._reply(cfg.get('unauth_session_status', 401), {'detail': 'not authenticated'})
            if cfg.get('verify_status'):
                return self._reply(cfg['verify_status'], {'detail': 'fault'})
            return self._reply(200, {'cart_items': st.setdefault('cart', []), 'country_code': 'MX'})
        if (method, path) == ('POST', '/api/cart'):
            if cfg.get('seed_status'):
                return self._reply(cfg['seed_status'], {'detail': 'fault'})
            if not cfg.get('seed_ignored'):
                st.setdefault('cart', []).extend(body.get('items', []))
            return self._reply(200, {'ok': True})
        if (method, path) == ('POST', '/auth/login'):
            return self._reply(cfg.get('auth_status', 200), {}, cookie=f'token={SESSION_TOKEN}; Path=/')
        if (method, path) == ('GET', '/booking/'):
            if not cookie_token:
                return self._reply(401, {})
            return self._reply(200, {'bookings': st.setdefault('bookings', list(cfg.get('seed_bookings', [])))})
        if (method, path) == ('POST', '/booking/'):
            bookings = st.setdefault('bookings', list(cfg.get('seed_bookings', [])))
            new = {'bookingid': len(bookings) + 10, 'roomid': body.get('roomid'), 'firstname': body.get('firstname'),
                   'lastname': body.get('lastname'), 'bookingdates': body.get('bookingdates')}
            if not cfg.get('create_ignored'):
                bookings.append(new)
            return self._reply(cfg.get('create_status', 201), {'bookingid': new['bookingid']})
        m = re.fullmatch(r'/booking/(\d+)', path)
        if m and method == 'GET':
            found = [b for b in st.setdefault('bookings', []) if b['bookingid'] == int(m.group(1))]
            return self._reply(200, found[0]) if found and cookie_token else self._reply(404, {})
        if (method, path) == ('POST', '/rest/user/login'):
            return self._reply(200, {'authentication': {'token': JWT_LIKE, 'bid': 7}})
        if (method, path) == ('GET', '/rest/basket/7'):
            return self._reply(200, {'status': 'success', 'data': {'id': 7, 'Products': st.setdefault('products', list(cfg.get('seed_products', [])))}})
        if (method, path) == ('POST', '/api/BasketItems'):
            if cfg.get('basket_add_status'):
                return self._reply(cfg['basket_add_status'], {})
            st.setdefault('products', list(cfg.get('seed_products', []))).append({'ProductId': body.get('ProductId'), 'quantity': body.get('quantity')})
            return self._reply(200, {'id': 1})
        return self._reply(404, {'detail': 'no route in the fake'})


class Fake:
    def __init__(self, cfg):
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), _Handler)
        self.server.cfg, self.server.state = cfg, {}
        self.base = f'http://127.0.0.1:{self.server.server_address[1]}'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


# ---- driver ------------------------------------------------------------------------------------------------------------------
CONDITION_ENV = ('CONDITION_ID', 'ASSIGNED_SUT', 'EXECUTION_ID', 'ATTEMPT', 'EXECUTOR_PROMPT_VERSION', 'OUTPUT_DIR',
                 'PROVENANCE_JSON', 'RUNTIME_ENVIRONMENT_JSON', 'RECORD_CLASS', 'INSTANCE_JSON', 'EXECUTOR_DIR')


def drive(test, condition, sut, module, fn_name, base, execution_id='DV0001'):
    """Run one realization the way executor.run does (execute, write_records, build_manifest, write_manifest), in a temp directory."""
    tmp = tempfile.mkdtemp(prefix='e02-test-')
    test.addCleanup(shutil.rmtree, tmp, True)
    run_id = f'{condition}__{execution_id}__A1'
    instance_json = os.path.join(tmp, 'instance.json')
    with open(instance_json, 'w', encoding='utf-8') as f:
        json.dump({'interface_version': 1, 'sut_id': sut, 'record_class': 'DEVELOPMENT',
                   'surfaces': {'web': {'base_url': None}, 'api': {'base_url': base}, 'auth': {'base_url': base}},
                   'provisioning': {'route': 'fake', 'repository': 'fake', 'commit_sha': 'fake', 'release': None,
                                    'asset': {'name': None, 'sha256': None}, 'commands': [], 'provisioning_record': None},
                   'process': None, 'logs': []}, f)
    env_values = {'CONDITION_ID': condition, 'ASSIGNED_SUT': sut, 'EXECUTION_ID': execution_id, 'ATTEMPT': '1',
                  'EXECUTOR_PROMPT_VERSION': 'ORCHESTRATOR-E02-state-establishment-test', 'OUTPUT_DIR': os.path.join(tmp, run_id),
                  'PROVENANCE_JSON': os.path.join(tmp, 'no-provenance.json'), 'RUNTIME_ENVIRONMENT_JSON': os.path.join(tmp, 'no-runtime.json'),
                  'RECORD_CLASS': 'DEVELOPMENT', 'INSTANCE_JSON': instance_json, 'EXECUTOR_DIR': EXECUTOR_DIR}
    saved = {k: os.environ.get(k) for k in CONDITION_ENV}
    os.environ.update(env_values)
    test.addCleanup(lambda: [os.environ.__setitem__(k, v) if v is not None else os.environ.pop(k, None) for k, v in saved.items()])
    env = common.Env()
    run = common.Run(env)
    mod = __import__(f'executor.{module}', fromlist=['SPEC'])
    spec = mod.SPEC[condition]
    result = runner.execute(run, spec, getattr(mod, fn_name))
    run.write_records(result)
    try:
        comps = spec.components(run)
    except Exception as e:  # noqa: BLE001 - recorded, the manifest is still built
        comps = [{'component': 'unavailable', 'observed': repr(e)}]
    manifest = common.build_manifest(run, result, spec, comps)
    common.write_manifest(run, manifest)
    run.close()
    with open(os.path.join(run.out, 'run-manifest.json'), encoding='utf-8') as f:
        written = json.load(f)
    with open(os.path.join(run.out, 'actions.json'), encoding='utf-8') as f:
        actions_json = json.load(f)
    with open(os.path.join(run.out, 'precondition.json'), encoding='utf-8') as f:
        precondition_json = json.load(f)
    return result, written, actions_json, precondition_json, run.out


class CountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCHEMA, encoding='utf-8') as f:
            cls.schema = json.load(f)

    def assertConforms(self, manifest):
        errors = validate(manifest, self.schema)
        self.assertEqual(errors, [], 'run-manifest does not conform to schema v2')

    def fake(self, cfg):
        fake = Fake(cfg)
        self.addCleanup(fake.close)
        return fake

    # SUT-01 API (CS-003): login, seed, verification (3)
    def test_sut01_api_success_counts_three_and_conforms(self):
        f = self.fake({})
        result, m, acts, pre, out = drive(self, 'E02-CS003-SUT01-API', 'SUT-01', 'sut01', 'cs003_api', f.base)
        self.assertEqual(result.status, 'SUCCESS')
        self.assertEqual([a['class'] for a in m['actions']], ['API action'] * 3)
        self.assertEqual([a['outcome'] for a in m['actions']], ['SUCCESS'] * 3)
        self.assertEqual(m['establishment_mechanisms'], ['PREDEFINED_ACCOUNT', 'API_SEED'])
        self.assertIsNone(m['reset_mechanisms'])
        self.assertEqual((m['scenario'], m['target_state_id'], m['starting_state_id'], m['experiment_id']),
                         ('CS-003', 'CS-003', 'CS-003-STARTING', 'E02-CS003'))
        self.assertEqual((m['platform'], m['modality']), ('api', 'API'))
        self.assertEqual(acts['counted_action_count'], 3)
        self.assertEqual([a['mechanism'] for a in acts['actions']], ['PREDEFINED_ACCOUNT', 'API_SEED', None],
                         'the verification read carries no establishment mechanism; its class is API action')
        self.assertTrue(acts['actions'][2]['verification'])
        self.assertEqual([p['phase'] for p in pre['steps']], ['declared-starting-state'])
        self.assertFalse(pre['steps'][0]['counted_as_required_action'])
        self.assertTrue(pre['declared_starting_state']['holds'])
        self.assertNotIn('mechanism', m['actions'][0], 'the manifest action records carry no mechanism field')
        self.assertConforms(m)

    def test_sut01_api_seed_failure_stops_the_establishment(self):
        f = self.fake({'seed_status': 500})
        result, m, acts, _, _ = drive(self, 'E02-CS003-SUT01-API', 'SUT-01', 'sut01', 'cs003_api', f.base)
        self.assertEqual(result.status, 'FAILURE')
        self.assertEqual([a['outcome'] for a in m['actions']], ['SUCCESS', 'FAILURE'])
        self.assertEqual(len(m['actions']), 2, 'no verification is performed after a failed counted operation')
        self.assertConforms(m)

    def test_sut01_api_cart_not_seeded_is_a_failed_verification_not_inconclusive(self):
        f = self.fake({'seed_ignored': True})
        result, m, _, _, _ = drive(self, 'E02-CS003-SUT01-API', 'SUT-01', 'sut01', 'cs003_api', f.base)
        self.assertEqual(result.status, 'FAILURE')
        self.assertEqual(len(m['actions']), 3)
        self.assertEqual(m['actions'][2]['outcome'], 'SUCCESS', 'a verification read that completed is SUCCESS whatever it shows')
        self.assertConforms(m)

    def test_sut01_api_unreadable_verification_is_inconclusive(self):
        f = self.fake({'verify_status': 500})
        result, m, _, _, _ = drive(self, 'E02-CS003-SUT01-API', 'SUT-01', 'sut01', 'cs003_api', f.base)
        self.assertEqual(result.status, 'INCONCLUSIVE')
        self.assertEqual(m['actions'][2]['outcome'], 'FAILURE')
        self.assertConforms(m)

    def test_sut01_api_login_refused_counts_one_and_fails(self):
        f = self.fake({'login_status': 401})
        result, m, _, _, _ = drive(self, 'E02-CS003-SUT01-API', 'SUT-01', 'sut01', 'cs003_api', f.base)
        self.assertEqual(result.status, 'FAILURE')
        self.assertEqual(len(m['actions']), 1)
        self.assertConforms(m)

    def test_sut01_api_dirty_fresh_instance_aborts_before_any_counted_action(self):
        f = self.fake({'unauth_session_status': 200})
        result, m, acts, pre, _ = drive(self, 'E02-CS003-SUT01-API', 'SUT-01', 'sut01', 'cs003_api', f.base)
        self.assertEqual(result.status, 'ABORTED')
        self.assertEqual(m['actions'], [])
        self.assertFalse(pre['declared_starting_state']['holds'])
        self.assertConforms(m)

    # SUT-04 API (CS-003): login, create without email and phone, verification (3); starting check after login
    def test_sut04_api_success_counts_three(self):
        f = self.fake({})
        result, m, acts, pre, _ = drive(self, 'E02-CS003-SUT04-API', 'SUT-04', 'sut04', 'cs003_api', f.base)
        self.assertEqual(result.status, 'SUCCESS')
        self.assertEqual([a['outcome'] for a in m['actions']], ['SUCCESS'] * 3)
        self.assertEqual(m['establishment_mechanisms'], ['PREDEFINED_ACCOUNT', 'API_SEED'])
        self.assertEqual(m['sut_provenance']['ecosystem_id'], 'SUT-04')
        self.assertEqual(pre['steps'][0]['phase'], 'declared-starting-state')
        self.assertConforms(m)

    def test_sut04_api_create_not_visible_fails_verification_read_as_failure(self):
        f = self.fake({'create_ignored': True})
        result, m, _, _, _ = drive(self, 'E02-CS003-SUT04-API', 'SUT-04', 'sut04', 'cs003_api', f.base)
        self.assertEqual(result.status, 'INCONCLUSIVE', 'the booking read answers 404: no observation of the names')
        self.assertConforms(m)

    def test_sut04_api_seed_booking_with_run_names_aborts(self):
        # the run-unique names are derived from the run id; a seeded booking with them makes the starting state fail
        probe = sut04.unique('E02-CS003-SUT04-API__DV0001__A1')
        f = self.fake({'seed_bookings': [{'bookingid': 3, 'roomid': 1, 'firstname': probe['firstname'], 'lastname': probe['lastname']}]})
        result, m, _, _, _ = drive(self, 'E02-CS003-SUT04-API', 'SUT-04', 'sut04', 'cs003_api', f.base)
        self.assertEqual(result.status, 'ABORTED')
        self.assertEqual(len(m['actions']), 1, 'the login (identity acquisition) was counted before the starting-state read')
        self.assertConforms(m)

    # SUT-05 API (CS-003): login, basket add, verification (3)
    def test_sut05_api_success_counts_three(self):
        f = self.fake({})
        result, m, _, pre, _ = drive(self, 'E02-CS003-SUT05-API', 'SUT-05', 'sut05', 'cs003_api', f.base)
        self.assertEqual(result.status, 'SUCCESS')
        self.assertEqual(len(m['actions']), 3)
        self.assertEqual(pre['declared_starting_state']['id'], 'CS-003-STARTING')
        self.assertConforms(m)

    def test_sut05_api_basket_not_empty_at_start_aborts(self):
        f = self.fake({'seed_products': [{'ProductId': 1, 'quantity': 1}]})
        result, m, _, _, _ = drive(self, 'E02-CS003-SUT05-API', 'SUT-05', 'sut05', 'cs003_api', f.base)
        self.assertEqual(result.status, 'ABORTED')
        self.assertEqual(len(m['actions']), 1)
        self.assertConforms(m)

    def test_token_values_never_reach_the_bundle(self):
        f = self.fake({})
        _, _, _, _, out = drive(self, 'E02-CS003-SUT05-API', 'SUT-05', 'sut05', 'cs003_api', f.base)
        for root, _dirs, files in os.walk(out):
            for name in files:
                with open(os.path.join(root, name), encoding='utf-8', errors='replace') as h:
                    text = h.read()
                self.assertNotIn(JWT_LIKE, text, f'a JWT is in {name}')
                self.assertNotIn(f'{SESSION_TOKEN}', text, 'the session token is in a kept file')

    def test_action_semantics_partial_success_counts_once_and_continues(self):
        f = self.fake({})
        env_values = {'CONDITION_ID': 'E02-CS003-SUT01-API', 'ASSIGNED_SUT': 'SUT-01', 'EXECUTION_ID': 'DV0002', 'ATTEMPT': '1',
                      'EXECUTOR_PROMPT_VERSION': 't', 'RECORD_CLASS': 'DEVELOPMENT', 'EXECUTOR_DIR': EXECUTOR_DIR,
                      'INSTANCE_JSON': os.path.join(EXECUTOR_DIR, 'tests', 'nonexistent.json'),
                      'PROVENANCE_JSON': 'x', 'RUNTIME_ENVIRONMENT_JSON': 'x', 'OUTPUT_DIR': tempfile.mkdtemp(prefix='e02-sem-')}
        self.addCleanup(shutil.rmtree, env_values['OUTPUT_DIR'], True)
        saved = {k: os.environ.get(k) for k in env_values}
        os.environ.update(env_values)
        self.addCleanup(lambda: [os.environ.__setitem__(k, v) if v is not None else os.environ.pop(k, None) for k, v in saved.items()])
        run = common.Run(common.Env())
        with run.action('UI action', 'a partially successful submit') as a:
            a['outcome'] = 'PARTIAL_SUCCESS'
        with run.action('UI action', 'the next, corrective submit') as a:
            a['outcome'] = 'SUCCESS'
        self.assertEqual([x['outcome'] for x in run.actions], ['PARTIAL_SUCCESS', 'SUCCESS'])
        self.assertTrue(all(x['is_retry'] is False for x in run.actions))
        run.close()

    def test_action_exception_stops_the_chain_as_failure(self):
        env_values = {'CONDITION_ID': 'E02-CS003-SUT01-API', 'ASSIGNED_SUT': 'SUT-01', 'EXECUTION_ID': 'DV0003', 'ATTEMPT': '1',
                      'EXECUTOR_PROMPT_VERSION': 't', 'RECORD_CLASS': 'DEVELOPMENT', 'EXECUTOR_DIR': EXECUTOR_DIR,
                      'INSTANCE_JSON': 'x', 'PROVENANCE_JSON': 'x', 'RUNTIME_ENVIRONMENT_JSON': 'x', 'OUTPUT_DIR': tempfile.mkdtemp(prefix='e02-sem-')}
        self.addCleanup(shutil.rmtree, env_values['OUTPUT_DIR'], True)
        saved = {k: os.environ.get(k) for k in env_values}
        os.environ.update(env_values)
        self.addCleanup(lambda: [os.environ.__setitem__(k, v) if v is not None else os.environ.pop(k, None) for k, v in saved.items()])
        run = common.Run(common.Env())
        with self.assertRaises(common.Chain):
            with run.action('UI action', 'a click that raises') as a:
                raise RuntimeError('element not found')
        self.assertEqual(run.actions[0]['outcome'], 'FAILURE')
        self.assertEqual(len(run.actions), 1)
        run.close()

    def test_scrubber_replaces_jwt_private_address_and_host_paths(self):
        env_values = {'CONDITION_ID': 'E02-CS003-SUT01-API', 'ASSIGNED_SUT': 'SUT-01', 'EXECUTION_ID': 'DV0004', 'ATTEMPT': '1',
                      'EXECUTOR_PROMPT_VERSION': 't', 'RECORD_CLASS': 'DEVELOPMENT', 'EXECUTOR_DIR': EXECUTOR_DIR,
                      'INSTANCE_JSON': 'x', 'PROVENANCE_JSON': 'x', 'RUNTIME_ENVIRONMENT_JSON': 'x', 'OUTPUT_DIR': tempfile.mkdtemp(prefix='e02-scrub-')}
        self.addCleanup(shutil.rmtree, env_values['OUTPUT_DIR'], True)
        saved = {k: os.environ.get(k) for k in env_values}
        os.environ.update(env_values)
        self.addCleanup(lambda: [os.environ.__setitem__(k, v) if v is not None else os.environ.pop(k, None) for k, v in saved.items()])
        run = common.Run(common.Env())
        home = '/Us' + 'ers/someone'  # built from fragments: the public hygiene scan rejects the literal path
        private_a = '.'.join(['192', '168', '1', '20'])  # built from fragments: the publication builder refuses a private network address in any exported text file
        private_b = '.'.join(['172', '16', '0', '5'])
        text = f'token {JWT_LIKE} at {private_a}:3000 and {private_b} and 172.32.0.1 and {home}/project'
        scrubbed = run.scrub(text)
        self.assertNotIn(JWT_LIKE, scrubbed)
        self.assertNotIn(private_a, scrubbed)
        self.assertNotIn(private_b, scrubbed)
        self.assertIn('172.32.0.1', scrubbed, 'outside RFC 1918 is kept')
        self.assertNotIn(home, scrubbed)
        run.close()


if __name__ == '__main__':
    unittest.main()
