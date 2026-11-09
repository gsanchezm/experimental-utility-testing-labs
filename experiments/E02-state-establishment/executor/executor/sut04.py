"""E02 realizations for SUT-04 (Restful Booker Platform, web and api). DRAFT (operation OP-PREP-E02).

The endpoints, the seeded admin account, the run-unique guest data, the web selectors, and the booking-list read are those the
E03 executor used and verified on the pinned SUT-04 commit (experiments/E03-resetability/executor/README.md, sections 4.5 and
4.6, DEVELOPMENT runs DV0011 to DV0016, and the hosted DRY_RUN runs). The establish-side sequences and the counts are new
(experiments/E02-state-establishment/executor/README.md, section 4).
For SUT-04, instance.json surfaces.api is the booking service, surfaces.auth the auth service, and surfaces.web the web app.
"""
import datetime
import hashlib
import re

from . import common, instance, web

ADMIN = {'username': 'admin', 'password': 'password'}
ROWS = 'div.detail.booking-1'
CITATIONS_CS003 = ['experiments/scenario-mappings/CS-003.yaml (SUT-04 entry)', 'SUT04-EV-0001', 'SUT04-EV-0002', 'SUT04-EV-0003',
                   'SUT04-EV-0004', 'SUT04-EV-0006', 'SUT04-EV-0008', 'SUT04-EV-0018']
EXPECTED_API = 'after the create, GET /booking/{id} returns the booking with the run-unique guest names'
EXPECTED_WEB = 'after the reservation, the admin room page lists one booking with the run-unique names and check-in date'
MECH_API = ['PREDEFINED_ACCOUNT', 'API_SEED']
MECH_WEB = ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW']


def unique(run_id):
    """Run-unique guest names and far-future dates derived from the run id (the E03 derivation; recorded in precondition.json)."""
    d = hashlib.sha256(run_id.encode()).digest()
    letters = ''.join(chr(ord('a') + b % 26) for b in d[:16])
    checkin = datetime.date(2031, 1, 1) + datetime.timedelta(days=int.from_bytes(d[16:20], 'big') % 3000)
    return {'firstname': 'G' + letters[:7], 'lastname': 'S' + letters[7:15], 'checkin': checkin.isoformat(),
            'checkout': (checkin + datetime.timedelta(days=1)).isoformat(), 'email': f'e02.{letters[:10]}@example.com', 'phone': '01234567890'}


def components_api(run):
    return instance.components(run, [('api', 'api'), ('auth', 'auth')])


def components_web(run):
    return instance.components(run, [('web', 'web'), ('api', 'api'), ('auth', 'auth')])


def _json(r):
    try:
        return r.json() if r.status == 200 else None
    except ValueError:
        return None


def _body(r):
    """The parsed body whatever the status (the create answers 201)."""
    try:
        return r.json()
    except ValueError:
        return None


def _bookings(run, booking, token, label):
    """The booking list of room 1 with the token cookie (E03 README section 4.6); the response shape is the one the E03 executor read."""
    r = run.http('GET', f'{booking}/booking/?roomid=1', headers={'Cookie': f'token={token}'}, label=label)
    items = (_json(r) or {}).get('bookings') if r.status == 200 else None
    return r, items


def _same_guest(item, u):
    return isinstance(item, dict) and item.get('firstname') == u['firstname'] and item.get('lastname') == u['lastname']


def cs003_api(run):
    """CS-003, SUT-04 API. Counted: login (authentication; the token cookie comes back in Set-Cookie), the booking create without
    email and phone, and the verification read (3). The starting-state read follows the login (it needs the token)."""
    auth = instance.base(run.instance, 'auth')
    booking = instance.base(run.instance, 'api')
    u = unique(run.env.run_id)
    token = None
    with run.action('API action', 'POST {auth}/auth/login with the seeded admin account (authentication)', 'PREDEFINED_ACCOUNT') as a:
        r = run.http('POST', f'{auth}/auth/login', ADMIN, label='sut04-api-login')
        a['evidence'].append(r.evidence)
        m = re.search(r'token=([^;]+)', next((v for k, v in r.headers.items() if k.lower() == 'set-cookie'), '') or '')
        token = m.group(1) if m else None
        run.scrub.secret(token)
        a['observation'] = {'status': r.status, 'token_cookie_received': bool(token)}
        a['outcome'] = 'SUCCESS' if r.status == 200 and token else 'FAILURE'
    with run.step('declared-starting-state', 'GET {booking}/booking/?roomid=1 with the token: no booking with this run\'s guest names') as s:
        r, items = _bookings(run, booking, token, 'sut04-api-list-start')
        s['evidence'].append(r.evidence)
        same = [x for x in (items or []) if _same_guest(x, u)]
        s['observation'] = {'status': r.status, 'bookings_listed': len(items or []), 'bookings_with_run_names': len(same)}
    run.declare_starting_state('room 1 holds no booking with this run\'s guest names (booking/.../BookingController.java:23-28)',
                               CITATIONS_CS003, s['observation'], r.status == 200 and not same)
    booking_id = None
    with run.action('API action', 'POST {booking}/booking/ with the run-unique guest and dates, without email and phone (establishment)', 'API_SEED') as a:
        body = {'roomid': 1, 'firstname': u['firstname'], 'lastname': u['lastname'], 'depositpaid': False,
                'bookingdates': {'checkin': u['checkin'], 'checkout': u['checkout']}}
        r = run.http('POST', f'{booking}/booking/', body, label='sut04-api-create')
        a['evidence'].append(r.evidence)
        booking_id = (_body(r) or {}).get('bookingid') if r.status in (200, 201) else None
        a['observation'] = {'status': r.status, 'bookingid': booking_id}
        a['outcome'] = 'SUCCESS' if booking_id is not None else 'FAILURE'
    with run.action('API action', 'GET {booking}/booking/{id} with the token: read the booking (verification)', None, verification=True) as a:
        r = run.http('GET', f'{booking}/booking/{booking_id}', headers={'Cookie': f'token={token}'}, label='sut04-api-verify')
        a['evidence'].append(r.evidence)
        obs = _json(r)
        a['observation'] = {'status': r.status, 'firstname': (obs or {}).get('firstname'), 'lastname': (obs or {}).get('lastname')}
        a['outcome'] = 'SUCCESS' if obs is not None else 'FAILURE'
    ok = obs.get('firstname') == u['firstname'] and obs.get('lastname') == u['lastname']
    return common.Result('SUCCESS' if ok else 'FAILURE', EXPECTED_API, f'booking {booking_id}: names match {ok}', MECH_API)


def _rows(b, u):
    texts = b.page.locator(ROWS).all_inner_texts()
    return texts, [t for t in texts if u['firstname'] in t and u['lastname'] in t and u['checkin'] in t]


def _visible(b, text):
    try:
        b.page.get_by_text(text).wait_for(state='visible', timeout=web.NAV_TIMEOUT_MS)
        return True
    except Exception:  # noqa: BLE001 - not visible is an observation: the action's outcome is FAILURE
        return False


def _landed(b, pattern):
    try:
        b.page.wait_for_url(pattern, timeout=web.NAV_TIMEOUT_MS)
        return True
    except Exception:  # noqa: BLE001 - not landed is an observation: the action's outcome is FAILURE
        return False


def cs003_web(run):
    """CS-003, SUT-04 WEB. Counted: the admin page load (CS-003 entry step), admin login (three UI operations, authentication),
    the reservation page navigation, the booking form (open, four fields, Reserve Now), the admin room page navigation, and the
    verification read (13). The starting-state read follows the login (it needs the token)."""
    site = instance.base(run.instance, 'web')
    booking = instance.base(run.instance, 'api')
    u = unique(run.env.run_id)
    b = web.Browser(run)
    try:
        with run.action('navigation action', 'open {web}/admin, the admin login page (the first load of the run; counted, HD-15 default)', 'DIRECT_ROUTE') as a:
            status = b.goto(site + '/admin')
            a['observation'] = {'status': status}
            a['outcome'] = 'SUCCESS' if status == 200 else 'FAILURE'
        with run.action('UI action', 'fill the seeded admin username (authentication)', 'PREDEFINED_ACCOUNT') as a:
            b.page.locator('#username').fill(ADMIN['username'])
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'fill the seeded admin password (authentication)', 'PREDEFINED_ACCOUNT') as a:
            b.page.locator('#password').fill(ADMIN['password'])
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'submit the admin login; the route changes to /admin/rooms and the token cookie is set (authentication)', 'PREDEFINED_ACCOUNT') as a:
            b.page.locator('#doLogin').click()
            landed = _landed(b, '**/admin/rooms')
            token = next((c['value'] for c in b.context.cookies() if c.get('name') == 'token'), None)
            run.scrub.secret(token)
            a['observation'] = {'url': b.page.url, 'token_cookie_present': bool(token)}
            a['outcome'] = 'SUCCESS' if landed and token else 'FAILURE'
        with run.step('declared-starting-state', 'GET {booking}/booking/?roomid=1 with the token cookie: no booking with this run\'s guest names') as s:
            r, items = _bookings(run, booking, token, 'sut04-web-list-start')
            s['evidence'].append(r.evidence)
            same = [x for x in (items or []) if _same_guest(x, u)]
            s['observation'] = {'status': r.status, 'bookings_listed': len(items or []), 'bookings_with_run_names': len(same)}
        run.declare_starting_state('room 1 holds no booking with this run\'s guest names (booking/.../BookingController.java:23-28)',
                                   CITATIONS_CS003, s['observation'], r.status == 200 and not same)
        with run.action('navigation action', 'open the reservation page {web}/reservation/1 with the run-unique dates (DIRECT_ROUTE)', 'DIRECT_ROUTE') as a:
            status = b.goto(f"{site}/reservation/1?checkin={u['checkin']}&checkout={u['checkout']}")
            a['observation'] = {'status': status}
            a['outcome'] = 'SUCCESS' if status == 200 else 'FAILURE'
        with run.action('UI action', 'open the booking form (#doReservation)', 'UI_FLOW') as a:
            b.page.locator('#doReservation').click()
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'fill the guest first name', 'UI_FLOW') as a:
            b.page.locator('.room-firstname').fill(u['firstname'])
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'fill the guest last name', 'UI_FLOW') as a:
            b.page.locator('.room-lastname').fill(u['lastname'])
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'fill the guest email', 'UI_FLOW') as a:
            b.page.locator('.room-email').fill(u['email'])
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'fill the guest phone', 'UI_FLOW') as a:
            b.page.locator('.room-phone').fill(u['phone'])
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'click Reserve Now; the page shows Booking Confirmed (establishment)', 'UI_FLOW') as a:
            b.page.get_by_role('button', name='Reserve Now').click()
            confirmed = _visible(b, 'Booking Confirmed')
            a['observation'] = {'booking_confirmed_visible': confirmed}
            a['outcome'] = 'SUCCESS' if confirmed else 'FAILURE'
        with run.action('navigation action', 'open the admin room page {web}/admin/room/1 (DIRECT_ROUTE)', 'DIRECT_ROUTE') as a:
            status = b.goto(site + '/admin/room/1')
            a['observation'] = {'status': status}
            a['outcome'] = 'SUCCESS' if status == 200 else 'FAILURE'
        with run.action('UI action', 'read the admin room rows (verification)', None, verification=True) as a:
            settle = b.settle()
            texts, found = _rows(b, u)
            a['observation'] = {'rows_listed': len(texts), 'rows_with_run_names_and_checkin': len(found), 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut04-web-admin-room')
    finally:
        b.close()
    return common.Result('SUCCESS' if len(found) == 1 else 'FAILURE', EXPECTED_WEB,
                         f'rows with the run names and check-in date: {len(found)}', MECH_WEB)


SPEC = {
    'E02-CS003-SUT04-API': common.Spec('API', 'api', MECH_API, EXPECTED_API, components_api, True),
    'E02-CS003-SUT04-WEB': common.Spec('Web UI Functional', 'web', MECH_WEB, EXPECTED_WEB, components_web, True),
}
