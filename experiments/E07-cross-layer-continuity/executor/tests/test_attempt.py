"""The attempt loop and the realizations, against fake systems under test (operation OP-PREP-E07-04). Static tests: nothing here is a SUT run.

Each case runs the executor in process on a fake instance (tests/fake_sut.py, a separate process). The web leg of every condition is replaced by a
fake UI (FakeSut01Ui, FakeSut04Ui) that talks to the same fake SUT over HTTP and records every call with the phase it was made in, because no browser is
installed in the static tests; the Playwright code (executor/web.py and the Ui classes of executor/sut01.py and executor/sut04.py) is verified later by
the non-measured DRY_RUN rounds on GitHub Actions. The cases check the categories, the bundles, the manifests against schemas/run-manifest.schema.v2.json,
the identity comparison, that the verification block changes no state, and that no secret survived."""
import base64
import contextlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import attempt, classify, common, config, instance, run as run_mod, sut01, sut04  # noqa: E402
import fake_sut  # noqa: E402
import mini_jsonschema  # noqa: E402

FAKE = os.path.join(HERE, 'fake_sut.py')
SCHEMA = os.path.join(REPO, 'schemas', 'run-manifest.schema.v2.json')
SECRETS = ('ey' + 'JhbGciOi', 'Tk4Secret1234', 'pizza123', 'SIDSECRET')  # none may appear in a kept file
C5_S1, C5_S4, C6_S1, C6_S4 = 'E07-CS005-SUT01-API-WEB', 'E07-CS005-SUT04-API-WEB', 'E07-CS006-SUT01-WEB-API', 'E07-CS006-SUT04-WEB-API'
V = config.SUCCESS_CATEGORY


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class Fake:
    def __init__(self, kind, env=None):
        self.kind, self.port = kind, free_port()
        self.proc = subprocess.Popen([sys.executable, '-I', FAKE, kind, str(self.port)], start_new_session=True,
                                     env={**os.environ, **(env or {})}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            if instance.port_open(self.port):
                break
            time.sleep(0.1)

    @property
    def base(self):
        return f'http://127.0.0.1:{self.port}'

    def stop(self):
        if self.proc.poll() is None:
            self.proc.terminate()
        with contextlib.suppress(Exception):
            self.proc.wait(timeout=5)


# ---- the fake web legs ---------------------------------------------------------------------------------------------------
class FakeUi:
    """What both fake web legs share: HTTP calls to the fake SUT, each recorded with the phase of the execution it was made in."""

    def __init__(self, base, **flags):
        self.base, self.flags, self.calls, self.run, self.client = base, flags, [], None, {}

    def call(self, method, path, body=None, headers=None):
        self.calls.append((self.run.phase if self.run else None, method, path))
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method, headers={'Content-Type': 'application/json', **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw else None), r.headers
        except urllib.error.HTTPError as e:
            return e.code, None, e.headers

    def bind(self, run):
        self.run, self.client = run, {}  # a new browser context: no client state survives from the previous execution

    def end(self, run):
        pass

    def close(self):
        pass

    def snapshot(self, run, rec, name):
        pass

    def picture(self, run, rec, name):
        pass


class FakeSut01Ui(FakeUi):
    """Flags: sync_on_add (the UI add also writes the server cart; the source of the SUT says it does not), hydrate (the Checkout view shows the server
    cart), quantity_shown (the text shown for the quantity), rotate_token (the web client holds another session's token), add_fails (the add control is
    not shown), add_twice (the UI add runs twice), checkout_status."""

    def inject_session(self, token, login):
        self.client = {'token': token, 'cart': []}
        return {'first_load_status': 200}, 200

    def client_cart(self):
        return list(self.client['cart'])

    def client_token(self):
        token = fake_sut.make_jwt('standard_user', 'SIDSECRETROTATED') if self.flags.get('rotate_token') else self.client['token']
        self.run.scrub.secret(token)
        return token

    def add_through_ui(self, pizza_id):
        if self.flags.get('add_fails'):
            return {'catalog_loaded': False}
        for _ in range(2 if self.flags.get('add_twice') else 1):
            if self.client['cart'] and self.client['cart'][0]['pizza_id'] == pizza_id:
                self.client['cart'][0]['quantity'] += 1
            else:
                self.client['cart'].append({'pizza_id': pizza_id, 'quantity': 1})
        if self.flags.get('sync_on_add'):
            self.call('POST', '/api/cart', {'items': [{'pizza_id': pizza_id, 'quantity': 1, 'size': 'small', 'toppings': []}]},
                      {'Authorization': f'Bearer {self.client["token"]}'})
        return {'confirmed': True}

    def open_checkout(self):
        return self.flags.get('checkout_status', 200)

    def checkout_lines(self):
        if not self.flags.get('hydrate', True):
            return []
        status, body, _ = self.call('GET', '/api/session', headers={'Authorization': f'Bearer {self.client["token"]}'})
        items = (body or {}).get('cart_items') or []
        shown = self.flags.get('quantity_shown')
        return [{'pizza_id': i['pizza_id'], 'details': f'{shown or i["quantity"]}x • Small'} for i in items]


class FakeSut04Ui(FakeUi):
    """Flags: hide_rows (the admin room page lists no row), omit_checkin (the row text has no check-in date), submit_checkin_shift (the form
    is submitted with a check-in date one day later), no_confirmation, login_fails."""

    def admin_login(self):
        status, _, headers = self.call('POST', '/auth/login', {'username': 'admin', 'password': 'password'})
        cookie = (headers.get('Set-Cookie') or '').split(';')[0].split('=', 1)[-1] if not self.flags.get('login_fails') else None
        self.run.scrub.secret(cookie)
        return status, cookie or None

    def submit_reservation(self, u):
        checkin = u['checkin']
        if self.flags.get('submit_checkin_shift'):
            import datetime
            checkin = (datetime.date.fromisoformat(checkin) + datetime.timedelta(days=1)).isoformat()
        status, _, _ = self.call('POST', '/booking/', {'roomid': 1, 'firstname': u['firstname'], 'lastname': u['lastname'], 'depositpaid': False,
                                                       'bookingdates': {'checkin': checkin, 'checkout': u['checkout']}})
        self.client['confirmed'] = status == 201 and not self.flags.get('no_confirmation')
        return {'status': 200, 'submitted': True}

    def confirmation_visible(self):
        return bool(self.client.get('confirmed'))

    def admin_room_rows(self):
        if self.flags.get('hide_rows'):
            return 200, []
        _, body, _ = self.call('GET', '/booking/?roomid=1')
        rows = []
        for b in (body or {}).get('bookings') or []:
            rows.append(f'{b["firstname"]} {b["lastname"]}' + ('' if self.flags.get('omit_checkin') else f' {b["bookingdates"]["checkin"]}'))
        return 200, rows


def make_job(condition, port, executions, record_class='DEVELOPMENT'):
    tmp = tempfile.mkdtemp(prefix='e07-attempt-')
    sut = 'SUT-' + condition.split('-')[2][3:]
    base = f'http://127.0.0.1:{port}'
    inst = {'interface_version': 1, 'sut_id': sut, 'record_class': record_class, 'surfaces': {k: {'base_url': base} for k in ('api', 'auth', 'web')}}
    with open(os.path.join(tmp, 'instance.json'), 'w') as f:
        json.dump(inst, f)
    os.environ.update({'CONDITION_ID': condition, 'ASSIGNED_SUT': sut, 'EXECUTOR_PROMPT_VERSION': 'TEST-FIXTURE-PROMPT-v1',
                       'OUTPUT_DIR': os.path.join(tmp, 'out'), 'PROVENANCE_JSON': os.path.join(tmp, 'absent-provenance.json'),
                       'RUNTIME_ENVIRONMENT_JSON': os.path.join(tmp, 'absent-runtime.json'), 'INSTANCE_JSON': os.path.join(tmp, 'instance.json'),
                       'RECORD_CLASS': record_class, 'EXECUTIONS': str(executions), 'EXECUTOR_BASH_VERSION': '5.2.0'})
    env = common.Env()
    cfg = config.load()
    job = common.Job(env, cfg, config.condition(cfg, condition))
    job.tools.update({'executor_runtime': {'tool': 'python3', 'version': '3.12.0'}})
    instance.load(job)
    os.makedirs(os.path.join(env.output_dir, 'executions'), exist_ok=True)
    return job


MODULES = {'SUT-01': sut01, 'SUT-04': sut04}
KIND = {'SUT-01': 'sut01', 'SUT-04': 'sut04'}
UI = {'SUT-01': FakeSut01Ui, 'SUT-04': FakeSut04Ui}


class AttemptCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCHEMA, encoding='utf-8') as f:
            cls.schema = json.load(f)

    def run_condition(self, condition, executions, fake_env=None, **flags):
        sut = 'SUT-' + condition.split('-')[2][3:]
        fake = Fake(KIND[sut], fake_env)
        self.addCleanup(fake.stop)
        job = make_job(condition, fake.port, executions)
        ui = UI[sut](fake.base, **flags)
        base_cls = MODULES[sut].REALIZATIONS[condition]
        cls = type('Fixture' + base_cls.__name__, (base_cls,), {'make_ui': lambda self: ui})
        results = attempt.run_job(job, cls(job))
        return job, results, ui

    def bundle(self, job, i):
        return os.path.join(job.env.output_dir, 'executions', job.env.run_id(i))

    def read(self, job, i, name):
        with open(os.path.join(self.bundle(job, i), name), encoding='utf-8') as f:
            return json.load(f)

    def manifest(self, job, i):
        return self.read(job, i, 'run-manifest.json')

    def record(self, job, i):
        return self.read(job, i, 'attempt-record.json')

    def check_bundles(self, job, results):
        self.assertEqual(len(results), job.planned)
        for n, r in enumerate(results, 1):
            m = self.manifest(job, n)
            self.assertEqual(mini_jsonschema.validate(m, self.schema), [], m['run_id'])
            self.assertEqual(m['outcome']['outcome_category'], r['category'])
            self.assertEqual(m['run_id'], r['run_id'])
            self.assertNotIn('actions', m)  # the reset is not emitted as an action (E05 decision D-08c)
            c = job.c
            self.assertEqual((m['scenario'], m['source_layer'], m['verification_layer']), (c['canonical_scenario_id'], c['source_layer'], c['verification_layer']))
            self.assertEqual((m['target_state_id'], m['starting_state_id']), (c['canonical_scenario_id'], c['canonical_scenario_id'] + '-STARTING'))
            self.assertEqual((m['campaign_id'], m['condition'], m['outcome']['expected']), ('E07-cross-layer-continuity', job.env.condition, 'VERIFIED'))
            for a in m['artifacts']:
                path = os.path.join(self.bundle(job, n), a['path'].split('/', 4)[4])
                if a['sha256'] is not None:
                    self.assertEqual(common.sha256_file(path), a['sha256'], a['path'])
            for root, _d, files in os.walk(self.bundle(job, n)):
                for fn in files:
                    with open(os.path.join(root, fn), 'rb') as f:
                        data = f.read()
                    for secret in SECRETS:
                        self.assertNotIn(secret.encode(), data, f'{secret} in {fn}')
        with open(os.path.join(job.env.output_dir, 'condition-summary.json'), encoding='utf-8') as f:
            summary = json.load(f)
        self.assertEqual(summary['executions_run'], job.planned)
        return summary

    def categories(self, results):
        return [r['category'] for r in results]

    def verification_writes(self, job, i, ui):
        """Every request made in the verification block of execution i: the API calls recorded as evidence and the calls of the fake web leg."""
        step = [s for s in self.record(job, i)['steps'] if s['phase'] == 'verification']
        methods = []
        for s in step:
            for rel in s['evidence']:
                if rel.endswith('.json'):
                    with open(os.path.join(self.bundle(job, i), rel), encoding='utf-8') as f:
                        ev = json.load(f)
                    if isinstance(ev, dict) and 'request' in ev:
                        methods.append(ev['request']['method'])
        methods += [m for phase, m, _p in ui.calls if phase == 'verification']
        return methods


class Sut01Tests(AttemptCase):
    def test_api_to_web_is_verified_and_the_identity_is_recorded(self):
        job, results, ui = self.run_condition(C5_S1, 3)
        self.assertEqual(self.categories(results), [V] * 3)
        self.check_bundles(job, results)
        m = self.manifest(job, 1)
        self.assertEqual((m['outcome']['status'], m['outcome']['matches_expected'], m['platform'], m['modality']), ('SUCCESS', True, 'api', 'API'))
        self.assertEqual(m['reset_mechanisms'], ['API_RESET', 'SESSION_RESET'])
        self.assertEqual(m['establishment_mechanisms'], ['PREDEFINED_ACCOUNT', 'API_SEED'])
        ident = self.record(job, 1)['identity']
        self.assertEqual(ident['compared_keys'], ['sid', 'cart_line.count', 'cart_line.pizza_id', 'cart_line.quantity'])
        self.assertTrue(all(e['match'] for e in ident['comparison']))
        self.assertTrue(ident['established']['sid'].startswith('sha256:'))
        self.assertNotIn('SIDSECRET', json.dumps(ident))

    def test_api_to_web_the_verification_changes_no_state(self):
        job, results, ui = self.run_condition(C5_S1, 2)
        for i in (1, 2):
            methods = self.verification_writes(job, i, ui)
            self.assertTrue(methods, 'the verification made no request, the test would prove nothing')
            self.assertEqual(set(methods), {'GET'})

    def test_web_to_api_with_the_ui_add_written_to_the_server_is_verified(self):
        job, results, ui = self.run_condition(C6_S1, 3, sync_on_add=True)
        self.assertEqual(self.categories(results), [V] * 3)
        self.check_bundles(job, results)
        m = self.manifest(job, 1)
        self.assertEqual((m['platform'], m['modality']), ('web', 'Web UI Functional'))
        self.assertEqual(m['establishment_mechanisms'], ['PREDEFINED_ACCOUNT', 'UI_FLOW'])
        self.assertEqual(set(self.verification_writes(job, 1, ui)), {'GET'})

    def test_web_to_api_when_the_ui_add_does_not_reach_the_server_is_not_verified(self):
        """The source of the SUT makes the UI add a client-store write only: the observation is recorded as it is, never as an error."""
        job, results, _ = self.run_condition(C6_S1, 2)
        self.assertEqual(self.categories(results), ['NOT_VERIFIED'] * 2)
        self.assertEqual([r['attribution'] for r in results], ['SUT'] * 2)
        self.check_bundles(job, results)
        m = self.manifest(job, 1)
        self.assertEqual((m['outcome']['status'], m['outcome']['matches_expected']), ('FAILURE', False))
        rec = self.record(job, 1)
        self.assertIn('cart_line.count: established 1, observed 0', rec['cause'])
        by_key = {e['key']: e['match'] for e in rec['identity']['comparison']}
        self.assertEqual(by_key, {'sid': True, 'cart_line.count': False, 'cart_line.pizza_id': False, 'cart_line.quantity': False})

    def test_one_attribute_that_differs_is_named_and_the_others_still_match(self):
        job, results, _ = self.run_condition(C5_S1, 1, quantity_shown=2)
        self.assertEqual(self.categories(results), ['NOT_VERIFIED'])
        rec = self.record(job, 1)
        self.assertIn('cart_line.quantity: established 1, observed 2', rec['cause'])
        self.assertEqual([e['key'] for e in rec['identity']['comparison'] if not e['match']], ['cart_line.quantity'])
        self.check_bundles(job, results)

    def test_a_session_that_differs_between_the_layers_is_not_verified(self):
        job, results, _ = self.run_condition(C5_S1, 1, rotate_token=True)
        self.assertEqual(self.categories(results), ['NOT_VERIFIED'])
        self.assertEqual([e['key'] for e in self.record(job, 1)['identity']['comparison'] if not e['match']], ['sid'])

    def test_a_verification_layer_without_the_unit_is_not_verified(self):
        job, results, _ = self.run_condition(C5_S1, 1, hydrate=False)
        self.assertEqual(self.categories(results), ['NOT_VERIFIED'])
        self.assertEqual({e['key']: e['observed'] for e in self.record(job, 1)['identity']['comparison']}['cart_line.count'], 0)

    def test_a_checkout_that_does_not_answer_200_is_not_verified(self):
        job, results, _ = self.run_condition(C5_S1, 1, checkout_status=500)
        self.assertEqual(self.categories(results), ['NOT_VERIFIED'])

    def test_establishment_failures(self):
        job, results, _ = self.run_condition(C5_S1, 2, fake_env={'FAKE_CART_FAIL': '1'})
        self.assertEqual(self.categories(results), ['ESTABLISHMENT_FAILED'] * 2)
        self.assertEqual(self.manifest(job, 1)['outcome']['status'], 'ABORTED')
        self.assertEqual(self.record(job, 1)['last_phase'], 'establishment')
        job2, results2, _ = self.run_condition(C6_S1, 1, add_fails=True)
        self.assertEqual(self.categories(results2), ['ESTABLISHMENT_FAILED'])
        self.check_bundles(job2, results2)

    def test_the_source_side_check_that_does_not_confirm_the_unit_is_an_establishment_failure(self):
        job, results, _ = self.run_condition(C6_S1, 1, add_twice=True)  # the client cart holds quantity 2: the unit is not the declared one
        self.assertEqual(self.categories(results), ['ESTABLISHMENT_FAILED'])
        self.assertEqual(self.record(job, 1)['last_phase'], 'establishment-check')

    def test_reset_and_starting_state(self):
        job, results, _ = self.run_condition(C5_S1, 2, fake_env={'FAKE_RESET_MODE': 'fail'})
        self.assertEqual(self.categories(results), ['INTERRUPTED'] * 2)
        self.assertEqual([r['interrupted_cause'] for r in results], ['RESET_FAILED'] * 2)
        self.assertEqual([r['attribution'] for r in results], ['SUT'] * 2)
        self.assertEqual(self.manifest(job, 1)['outcome']['status'], 'ABORTED')
        job2, results2, _ = self.run_condition(C5_S1, 2, fake_env={'FAKE_RESET_MODE': 'noop', 'FAKE_LOGIN_CART': '1'})
        self.assertEqual([r['interrupted_cause'] for r in results2], ['STARTING_STATE_NOT_REACHED'] * 2)
        self.check_bundles(job2, results2)


class Sut04Tests(AttemptCase):
    def test_api_to_web_is_verified_and_the_checkout_date_is_not_compared_on_the_web(self):
        job, results, ui = self.run_condition(C5_S4, 3)
        self.assertEqual(self.categories(results), [V] * 3)
        self.check_bundles(job, results)
        ident = self.record(job, 1)['identity']
        self.assertEqual(ident['compared_keys'], ['booking_count', 'firstname', 'lastname', 'checkin'])
        self.assertIn('checkout', ident['not_compared'])
        self.assertTrue(all(e['match'] for e in ident['comparison']))
        self.assertEqual(set(self.verification_writes(job, 1, ui)), {'GET'})

    def test_web_to_api_is_verified_with_every_key_including_both_dates(self):
        job, results, ui = self.run_condition(C6_S4, 3)
        self.assertEqual(self.categories(results), [V] * 3)
        self.check_bundles(job, results)
        ident = self.record(job, 2)['identity']
        self.assertEqual(ident['compared_keys'], ['booking_count', 'firstname', 'lastname', 'checkin', 'checkout'])
        self.assertEqual(ident['not_compared'], {})
        self.assertEqual(set(self.verification_writes(job, 2, ui)), {'GET'})
        self.assertEqual(self.manifest(job, 1)['establishment_mechanisms'], ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'])

    def test_the_names_and_dates_are_unique_per_execution_and_the_first_name_is_stable(self):
        job, results, _ = self.run_condition(C6_S4, 3)
        records = [self.record(job, i)['identity']['established'] for i in (1, 2, 3)]
        self.assertEqual(len({r['lastname'] for r in records}), 3)
        self.assertEqual(len({r['firstname'] for r in records}), 1)
        self.assertEqual(len({r['checkin'] for r in records}), 3)

    def test_an_admin_page_without_the_row_is_not_verified(self):
        job, results, _ = self.run_condition(C5_S4, 1, hide_rows=True)
        self.assertEqual(self.categories(results), ['NOT_VERIFIED'])
        self.assertIn('booking_count: established 1, observed 0', self.record(job, 1)['cause'])

    def test_a_row_without_the_check_in_date_names_that_key(self):
        job, results, _ = self.run_condition(C5_S4, 1, omit_checkin=True)
        self.assertEqual(self.categories(results), ['NOT_VERIFIED'])
        self.assertEqual([e['key'] for e in self.record(job, 1)['identity']['comparison'] if not e['match']], ['checkin'])

    def test_a_booking_with_other_dates_is_not_verified_on_the_api(self):
        job, results, _ = self.run_condition(C6_S4, 1, submit_checkin_shift=True)
        self.assertEqual(self.categories(results), ['NOT_VERIFIED'])
        self.assertEqual([e['key'] for e in self.record(job, 1)['identity']['comparison'] if not e['match']], ['checkin'])
        self.assertIn('checkin: established', self.record(job, 1)['cause'])

    def test_a_form_without_confirmation_is_an_establishment_failure(self):
        job, results, _ = self.run_condition(C6_S4, 1, no_confirmation=True)
        self.assertEqual(self.categories(results), ['ESTABLISHMENT_FAILED'])
        self.assertEqual(self.record(job, 1)['last_phase'], 'establishment-check')

    def test_an_admin_login_without_token_is_a_failed_reset(self):
        job, results, _ = self.run_condition(C5_S4, 1, login_fails=True)
        self.assertEqual(self.categories(results), ['INTERRUPTED'])
        self.assertEqual(results[0]['interrupted_cause'], 'RESET_FAILED')

    def test_a_reset_that_fails_is_an_interruption_and_the_job_goes_on(self):
        job, results, _ = self.run_condition(C5_S4, 3, fake_env={'FAKE_DELETE_MODE': 'fail'})
        self.assertEqual(self.categories(results), [V, 'INTERRUPTED', 'INTERRUPTED'])
        self.assertEqual([r['interrupted_cause'] for r in results[1:]], ['RESET_FAILED'] * 2)
        self.check_bundles(job, results)
        m = self.manifest(job, 2)
        self.assertEqual((m['outcome']['status'], m['outcome']['matches_expected']), ('ABORTED', False))
        self.assertIn('interrupted_cause=RESET_FAILED', m['notes'])

    def test_a_reset_that_did_not_hold_is_seen_by_the_starting_state_check(self):
        job, results, _ = self.run_condition(C6_S4, 3, fake_env={'FAKE_DELETE_MODE': 'noop'})
        self.assertEqual(self.categories(results), [V, 'INTERRUPTED', 'INTERRUPTED'])
        self.assertEqual([r['interrupted_cause'] for r in results[1:]], ['STARTING_STATE_NOT_REACHED'] * 2)
        self.check_bundles(job, results)


class StubRealization(attempt.Realization):
    """Fails or raises in the block named by BLOCK; used to check the phase mapping and the attribution."""
    SPEC = common.Spec('API', 'api', ['API_RESET'], ['API_SEED'], [('api', 'api')], True)
    BLOCK, HOW = None, None

    def block(self, run, name, phase):
        if self.BLOCK != name:
            return
        with run.step(phase, name) as rec:
            if self.HOW == 'raise':
                raise RuntimeError('harness fault')
            if self.HOW == 'watchdog':
                raise common.Watchdog('the execution exceeded its budget')
            rec['outcome'] = 'FAILURE'

    def reset(self, run):
        self.block(run, 'reset', 'reset')

    def check_start(self, run):
        self.block(run, 'check', 'starting-state')

    def establish(self, run):
        self.block(run, 'establish', 'establishment')

    def establish_check(self, run):
        self.block(run, 'establish_check', 'establishment-check')

    def verify(self, run):
        self.block(run, 'verify', 'verification')


class PhaseMappingTests(AttemptCase):
    def check(self, block, how, label, attribution, cause=None):
        job = make_job(C5_S4, 1, 1)
        cls = type('S', (StubRealization,), {'BLOCK': block, 'HOW': how})
        results = attempt.run_job(job, cls(job))
        self.assertEqual((results[0]['category'], results[0]['interrupted_cause'], results[0]['attribution']), (label, cause, attribution), (block, how))
        m = self.manifest(job, 1)
        self.assertEqual(mini_jsonschema.validate(m, self.schema), [], m)
        return m

    def test_every_block(self):
        self.check('reset', 'raise', 'RUNNER_ERROR', 'TOOLING')
        self.check('reset', 'fail', 'INTERRUPTED', 'SUT', 'RESET_FAILED')
        self.check('check', 'raise', 'RUNNER_ERROR', 'TOOLING')
        self.check('check', 'fail', 'INTERRUPTED', 'SUT', 'STARTING_STATE_NOT_REACHED')
        self.check('establish', 'raise', 'RUNNER_ERROR', 'TOOLING')
        self.check('establish', 'fail', 'ESTABLISHMENT_FAILED', 'SUT')
        self.check('establish_check', 'raise', 'RUNNER_ERROR', 'TOOLING')
        self.check('establish_check', 'fail', 'ESTABLISHMENT_FAILED', 'SUT')
        self.check('verify', 'raise', 'RUNNER_ERROR', 'TOOLING')
        m = self.check('verify', 'fail', 'NOT_VERIFIED', 'SUT')
        self.assertEqual(m['outcome']['status'], 'FAILURE')
        m = self.check(None, None, V, 'SUT')
        self.assertEqual((m['outcome']['status'], m['outcome']['matches_expected']), ('SUCCESS', True))

    def test_the_watchdog_is_an_interruption_with_its_cause_in_every_block(self):
        for block in ('reset', 'check', 'establish', 'establish_check', 'verify'):
            with self.subTest(block):
                m = self.check(block, 'watchdog', 'INTERRUPTED', 'TOOLING', 'WATCHDOG')
                self.assertEqual(m['outcome']['status'], 'ABORTED')

    def test_a_bundle_that_cannot_be_written_leaves_a_runner_error_record(self):
        job = make_job(C5_S4, 1, 1)
        real = type('S', (StubRealization,), {})(job)
        original = common.build_manifest
        calls = []

        def broken(*a, **k):
            calls.append(1)
            if len(calls) == 1:
                raise OSError('disk full')
            return original(*a, **k)
        common.build_manifest = broken
        try:
            results = attempt.run_job(job, real)
        finally:
            common.build_manifest = original
        self.assertEqual((results[0]['category'], results[0]['attribution']), ('RUNNER_ERROR', 'TOOLING'))
        m = self.manifest(job, 1)
        self.assertEqual((m['outcome']['status'], m['outcome']['outcome_category']), ('ERROR', 'RUNNER_ERROR'))
        self.assertTrue(self.record(job, 1)['cause'].startswith('BUNDLE_NOT_WRITTEN'))


class IdentityHelpers(unittest.TestCase):
    def test_jwt_claim_reads_the_payload_without_verifying_and_refuses_what_is_not_a_jwt(self):
        token = fake_sut.make_jwt('someone', 'abc123')
        self.assertEqual(common.jwt_claim(token, 'sid'), 'abc123')
        self.assertIsNone(common.jwt_claim(token, 'absent'))
        for bad in (None, '', 'not-a-token', 'a.b.c', 'a.' + base64.urlsafe_b64encode(b'[1]').decode() + '.c'):
            self.assertIsNone(common.jwt_claim(bad, 'sid'), bad)

    def test_compare_marks_an_absent_key_as_no_match(self):
        out = common.compare({'a': 1, 'b': 2}, {'a': 1}, ['a', 'b'])
        self.assertEqual([e['match'] for e in out], [True, False])
        self.assertIn('b: established 2, observed None', common.mismatch_text(out))

    def test_digest_is_not_the_value(self):
        self.assertNotIn('abc123', common.digest('abc123'))
        self.assertEqual(common.digest('abc123'), common.digest('abc123'))


class RefusalTests(unittest.TestCase):
    def check(self, condition, record_class, executions, workflow_ref=''):
        os.environ.update({'CONDITION_ID': condition, 'ASSIGNED_SUT': 'SUT-' + condition.split('-')[2][3:], 'EXECUTOR_PROMPT_VERSION': 'p',
                           'OUTPUT_DIR': tempfile.mkdtemp(), 'PROVENANCE_JSON': 'x', 'RUNTIME_ENVIRONMENT_JSON': 'y', 'RECORD_CLASS': record_class,
                           'GITHUB_WORKFLOW_REF': workflow_ref})
        os.environ.pop('EXECUTIONS', None)
        if executions is not None:
            os.environ['EXECUTIONS'] = str(executions)
        return run_mod.check(common.Env(), config.load())[1]

    def test_refusals(self):
        ref = 'o/r/.github/workflows/e07-measured-execution.yml@refs/heads/main'
        self.assertIn('only inside .github/workflows/e07-measured-execution.yml', self.check(C5_S4, 'MEASURED_EXPERIMENT', None))
        self.assertIn('only inside', self.check(C5_S4, 'MEASURED_EXPERIMENT', None, 'o/r/.github/workflows/e04-measured-execution.yml@x'))
        self.assertIsNone(self.check(C5_S4, 'MEASURED_EXPERIMENT', None, ref))
        self.assertIsNone(self.check(C5_S4, 'MEASURED_EXPERIMENT', 50, ref))
        self.assertIn('N = 50', self.check(C5_S4, 'MEASURED_EXPERIMENT', 10, ref))
        self.assertIn('EXECUTIONS between 1 and 3', self.check(C5_S4, 'DRY_RUN', 5))
        self.assertIn('EXECUTIONS between 1 and 3', self.check(C5_S4, 'DRY_RUN', None))
        self.assertIsNone(self.check(C5_S4, 'DRY_RUN', 2))
        self.assertIn('EXECUTIONS between 1 and 50', self.check(C5_S4, 'DEVELOPMENT', 51))
        self.assertIsNone(self.check(C5_S4, 'DEVELOPMENT', 50))
        self.assertIn('RECORD_CLASS', self.check(C5_S4, 'SMOKE', 2))
        self.assertIn('is not a condition', self.check('E07-CS005-SUT03-API-WEB', 'DRY_RUN', 2))
        self.assertIn('is not a condition', self.check('E07-CS005-SUT05-API-WEB', 'DRY_RUN', 2))

    def test_a_condition_of_another_sut_is_refused(self):
        os.environ.update({'CONDITION_ID': C5_S4, 'ASSIGNED_SUT': 'SUT-01', 'EXECUTOR_PROMPT_VERSION': 'p', 'OUTPUT_DIR': tempfile.mkdtemp(),
                           'PROVENANCE_JSON': 'x', 'RUNTIME_ENVIRONMENT_JSON': 'y', 'RECORD_CLASS': 'DRY_RUN', 'EXECUTIONS': '1'})
        self.assertIn('does not belong to SUT-01', run_mod.check(common.Env(), config.load())[1])

    def test_every_realization_is_configured_and_listed(self):
        every = {c for m in (sut01, sut04) for c in m.REALIZATIONS}
        listed = {c['condition_id'] for c in config.load()['conditions']}
        self.assertEqual(every, listed)
        self.assertEqual(len(listed), 4)
        self.assertTrue(all(cls.SPEC.configured for m in (sut01, sut04) for cls in m.REALIZATIONS.values()))


if __name__ == '__main__':
    unittest.main()
