"""E03-CS001-SUT04-API (README section 4.5). DRAFT (operation OP-PREP-E03).

For SUT-04, instance.json surfaces.api is the booking service and surfaces.auth the auth service.
"""
import datetime
import hashlib
import os
import re

from . import common, instance

MODALITY, PLATFORM = 'API', 'api'
RESET_MECHANISMS = ['API_RESET']
ESTABLISHMENT_MECHANISMS = ['PREDEFINED_ACCOUNT', 'API_SEED']
EXPECTED = 'after DELETE /booking/{id}, GET /booking/{id} answers 404'
CITATIONS = ['experiments/scenario-mappings/CS-001.yaml (SUT-04 entry)', 'SUT04-EV-0003', 'SUT04-EV-0006', 'SUT04-EV-0008',
             'booking/src/main/java/com/automationintesting/service/BookingService.java:58-81@d36bd3f']


def components(run):
    return instance.components(run, [('api', 'api'), ('auth', 'auth')])


def unique(run_id):
    """Run-unique guest names and far-future dates derived from the run id (recorded in precondition.json)."""
    d = hashlib.sha256(run_id.encode()).digest()
    letters = ''.join(chr(ord('a') + b % 26) for b in d[:16])
    checkin = datetime.date(2031, 1, 1) + datetime.timedelta(days=int.from_bytes(d[16:20], 'big') % 3000)
    return {'firstname': 'E' + letters[:7], 'lastname': 'R' + letters[7:15], 'checkin': checkin.isoformat(),
            'checkout': (checkin + datetime.timedelta(days=1)).isoformat(), 'email': f'e03.{letters[:10]}@example.com', 'phone': '01234567890'}


def rescrub(run, rel):
    """Run.http writes the login transcript before the token is known to the scrubber, and SUT-04's token is not a JWT:
    rewrite that transcript through the scrubber once the token is registered (DEVELOPMENT run DV0011; README section 12)."""
    path = os.path.join(run.out, rel)
    with open(path, encoding='utf-8') as f:
        text = f.read()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(run.scrub(text))


def login(run, auth):
    with run.step('precondition', 'POST /auth/login with the seeded admin account', ['PREDEFINED_ACCOUNT']) as s:
        r = run.http('POST', f'{auth}/auth/login', {'username': 'admin', 'password': 'password'}, label='sut04-login')
        s['evidence'].append(r.evidence)
        m = re.search(r'token=([^;]+)', next((v for k, v in r.headers.items() if k.lower() == 'set-cookie'), '') or '')
        token = m.group(1) if m else None
        run.scrub.secret(token)
        rescrub(run, r.evidence)
        s['observation'] = {'status': r.status, 'token_cookie_received': bool(token)}
        if r.status != 200 or not token:
            s['outcome'] = 'FAILURE'
    return token


def bookings(run, booking, token, label):
    r = run.http('GET', f'{booking}/booking/?roomid=1', headers={'Cookie': f'token={token}'}, label=label)
    try:
        items = r.json().get('bookings') if r.status == 200 else None
    except ValueError:
        items = None
    return r, items


def mine(items, u):
    return [b for b in (items or []) if b.get('firstname') == u['firstname'] and b.get('lastname') == u['lastname']
            and str((b.get('bookingdates') or {}).get('checkin', '')).startswith(u['checkin'])]


def starting_state(run, booking, token, u):
    with run.step('declared-starting-state', 'GET /booking/?roomid=1 before the establishment') as s:
        r, items = bookings(run, booking, token, 'sut04-bookings-start')
        s['evidence'].append(r.evidence)
        s['observation'] = {'status': r.status, 'bookings_in_room_1': None if items is None else len(items), 'bookings_with_the_run_names': len(mine(items, u)),
                            'run_unique_values': u}
        if items is None:
            s['outcome'] = 'FAILURE'
    run.declare_starting_state("room 1 holds no booking with this run's guest names and dates", CITATIONS, s['observation'], s['observation']['bookings_with_the_run_names'] == 0)


def delete(run, booking, token, bid):
    with run.action('reset action', 'DELETE /booking/{id} with the token') as a:
        r = run.http('DELETE', f'{booking}/booking/{bid}', headers={'Cookie': f'token={token}'}, label='sut04-delete')
        a['evidence'].append(r.evidence)
        a['observation'] = {'status': r.status, 'error': r.error, 'booking_id': bid}
        a['outcome'] = 'SUCCESS' if r.status == 202 else 'FAILURE'


def run(run):
    auth, booking = instance.base(run.instance, 'auth'), instance.base(run.instance, 'api')
    u = unique(run.env.run_id)
    token = login(run, auth)
    starting_state(run, booking, token, u)
    bid = None
    with run.step('establishment', 'POST /booking/ for room 1 with the run-unique names and dates, without email and phone', ['API_SEED']) as s:
        r = run.http('POST', f'{booking}/booking/', {'roomid': 1, 'firstname': u['firstname'], 'lastname': u['lastname'], 'depositpaid': False,
                                                     'bookingdates': {'checkin': u['checkin'], 'checkout': u['checkout']}}, label='sut04-create')
        s['evidence'].append(r.evidence)
        try:
            bid = r.json().get('bookingid') if r.status == 201 else None
        except ValueError:
            bid = None
        s['observation'] = {'status': r.status, 'booking_id': bid}
        if bid is None:
            s['outcome'] = 'FAILURE'
    with run.step('pre-reset-verification', 'GET /booking/{id} answers 200') as s:
        r = run.http('GET', f'{booking}/booking/{bid}', headers={'Cookie': f'token={token}'}, label='sut04-get-pre-reset')
        s['evidence'].append(r.evidence)
        s['observation'] = {'status': r.status}
        if r.status != 200:
            s['outcome'] = 'FAILURE'
    delete(run, booking, token, bid)
    status = None
    with run.action('API action', 'GET /booking/{id} with the token') as a:
        r = run.http('GET', f'{booking}/booking/{bid}', headers={'Cookie': f'token={token}'}, label='sut04-get-after-reset')
        a['evidence'].append(r.evidence)
        status = r.status
        a['observation'] = {'status': r.status, 'error': r.error}
        a['outcome'] = 'SUCCESS' if r.status is not None else 'FAILURE'
    if status is None:
        return common.Result('INCONCLUSIVE', EXPECTED, 'no response to the post-reset read', RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
    return common.Result('SUCCESS' if status == 404 else 'FAILURE', EXPECTED, f'GET /booking/{bid} answered {status}', RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
