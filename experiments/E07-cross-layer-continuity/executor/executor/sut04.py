"""E07 realizations on SUT-04: E07-CS005-SUT04-API-WEB (CS-005, API to WEB) and E07-CS006-SUT04-WEB-API (CS-006, WEB to API). DRAFT (operation OP-PREP-E07-04).

The unit is one booking of room 1. The identity keys (decision D-E07-9) are the run-unique guest names and the check-in and check-out dates; the
bookingid is not a key (the web does not show it) and is used only to find the booking for the reset. For SUT-04, instance.json surfaces.api is the
booking service, surfaces.auth the auth service and surfaces.web the web app.

Sources: the E04 realization of E04-SUT04-API-01 and E04-SUT04-WEB-01 (itself the E03 blocks 4.5 and 4.6; SUT04-EV-0002, -0003, -0006, -0008, -0018,
-0028), copied by value: the API login (POST /auth/login, token cookie), the listing of room 1 (GET /booking/?roomid=1), the booking (POST /booking/ without
email and phone), the delete (DELETE /booking/{id}, 202), the admin web login (#username, #password, #doLogin, redirect to /admin/rooms), the reservation
route (/reservation/1?checkin=..&checkout=.., #doReservation, .room-firstname, .room-lastname, .room-email, .room-phone, 'Reserve Now', 'Booking
Confirmed') and the admin room page (/admin/room/1, rows `div.detail.booking-1`).

Per attempt: reset = delete through the booking API every booking of room 1 whose first name is this condition's first name (stable across the
executions of the condition, so that a booking left by an earlier execution is found and deleted, and a reset that did not hold is seen by the next
starting-state check), then the admin login in the new browser context; starting-state check = room 1 holds no booking with that first name. The last
name, the dates and the contact values of an execution are derived from its run id (unique per execution and attempt).

Admin room page (API to WEB): the E03 module reads the rows and matches the guest names and the check-in date in the row text (sut04_web.py). DRY_RUN
round 1 (run 44529314764, evidence sut04-web-admin-rows) showed that the row also lists the check-out date, so the check-out date is observable on the
WEB layer and is compared there as well (D-E07-15: the identity keys of D-E07-9 are compared in both directions). The number of bookings that carry the
names is compared on both layers.
"""
import datetime
import hashlib
import re

from . import attempt, common, instance, web

ROOM = 1
PHONE = '01234567890'  # 11 characters: the message service accepts 11 to 21 (manifests/source-reads-v2.yaml, F15)
DECLARED = ['run-unique guest names', 'check-in and check-out dates of room 1']
KEYS_API = ['booking_count', 'firstname', 'lastname', 'checkin', 'checkout']
KEYS_WEB = list(KEYS_API)
SPEC_API_WEB = common.Spec('API', 'api', ['API_RESET'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('web', 'web'), ('api', 'api'), ('auth', 'auth')], True)
SPEC_WEB_API = common.Spec('Web UI Functional', 'web', ['API_RESET'], ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'],
                           [('web', 'web'), ('api', 'api'), ('auth', 'auth')], True)


def unique(condition_id, run_id):
    """The guest names and dates of one execution: the first name is stable across the executions of the condition (derived from the condition id);
    the last name, the dates and the email are derived from the run id."""
    c = hashlib.sha256(('E07|' + condition_id).encode()).digest()
    r = hashlib.sha256(('E07|' + run_id).encode()).digest()
    first = 'E' + ''.join(chr(ord('a') + b % 26) for b in c[:7])
    last_letters = ''.join(chr(ord('a') + b % 26) for b in r[:8])
    checkin = datetime.date(2031, 1, 1) + datetime.timedelta(days=int.from_bytes(r[8:12], 'big') % 3000)
    return {'firstname': first, 'lastname': 'R' + last_letters, 'checkin': checkin.isoformat(),
            'checkout': (checkin + datetime.timedelta(days=1)).isoformat(), 'email': f'e07.{last_letters}@example.com', 'phone': PHONE}


class Sut04Ui:
    """The web leg of the SUT-04 conditions: Playwright. Every method returns plain data. A test substitutes an object with the same methods
    (tests/test_attempt.py, FakeSut04Ui), because no browser is installed in the static tests."""

    def __init__(self, job):
        self.b = web.Browser(job)
        self.site = instance.base(job.instance, 'web')
        self.run = None

    def bind(self, run):
        self.run = run
        self.b.bind(run)

    def end(self, run):
        self.b.flush()

    def close(self):
        self.b.close()

    def picture(self, run, rec, name):
        run.capture(rec, self.b.shot, name)

    def admin_login(self):
        """Log in through the admin form in the new context. Returns (page status, token cookie or None); the cookie is registered with the scrubber."""
        b = self.b
        status = b.goto(self.site + '/admin')
        b.settle()  # a logged-in session is redirected by the page itself; a navigation started meanwhile is aborted (E04 first DRY_RUN, ERR_ABORTED)
        if b.page.locator('#username').count():
            b.page.locator('#username').fill('admin')
            b.page.locator('#password').fill('password')
            b.page.locator('#doLogin').click()
            b.page.wait_for_url('**/admin/rooms', timeout=web.NAV_TIMEOUT_MS)
        token = next((c['value'] for c in b.context.cookies() if c.get('name') == 'token'), None)
        self.run.scrub.secret(token)
        return status, token

    def submit_reservation(self, u):
        """The booking form of the reservation route, with the guest names, dates and contact values; submitted, not awaited."""
        b = self.b
        status = b.goto(f"{self.site}/reservation/{ROOM}?checkin={u['checkin']}&checkout={u['checkout']}")
        if status != 200:
            return {'status': status, 'submitted': False}
        b.page.locator('#doReservation').click()
        b.page.locator('.room-firstname').fill(u['firstname'])
        b.page.locator('.room-lastname').fill(u['lastname'])
        b.page.locator('.room-email').fill(u['email'])
        b.page.locator('.room-phone').fill(u['phone'])
        b.page.get_by_role('button', name='Reserve Now').click()
        return {'status': status, 'submitted': True}

    def confirmation_visible(self):
        return self.b.visible(self.b.page.get_by_text('Booking Confirmed'), web.NAV_TIMEOUT_MS)

    def admin_room_rows(self):
        """Read-only: the text of every booking row of room 1 on the admin room page (a read after the page and the network are quiet)."""
        b = self.b
        status = b.goto(f'{self.site}/admin/room/{ROOM}')
        b.visible(b.page.locator('div.detail.booking-1'))  # False is an observation (no row shown)
        b.settle()
        return status, b.page.locator('div.detail.booking-1').all_inner_texts()


class Sut04(attempt.Realization):
    DECLARED_KEYS = DECLARED

    def __init__(self, job):
        super().__init__(job)
        self.marker = unique(job.env.condition, 'marker')['firstname']
        self.u = None
        self.ui = None

    # ---- the web leg ----------------------------------------------------------------------------------------------
    def make_ui(self):
        return Sut04Ui(self.job)

    def open(self):
        self.ui = self.make_ui()

    def bind(self, run):
        self.u = unique(run.env.condition, run.run_id)
        self.start_identity(run)
        self.ui.bind(run)

    def end(self, run):
        self.ui.end(run)

    def close(self):
        if self.ui is not None:
            self.ui.close()

    # ---- the API leg ----------------------------------------------------------------------------------------------
    def api(self):
        return instance.base(self.job.instance, 'api')

    def login(self, run, label='sut04-login'):
        """POST /auth/login with the seeded admin account; the token cookie is registered with the scrubber and the transcript rewritten."""
        r = run.http('POST', f'{instance.base(self.job.instance, "auth")}/auth/login', {'username': 'admin', 'password': 'password'}, label=label)
        m = re.search(r'token=([^;]+)', next((v for k, v in r.headers.items() if k.lower() == 'set-cookie'), '') or '')
        token = m.group(1) if m else None
        run.scrub.secret(token)
        run.rescrub(r.evidence)
        return r, token

    def list_bookings(self, run, token, label):
        r = run.http('GET', f'{self.api()}/booking/?roomid={ROOM}', headers={'Cookie': f'token={token}'}, label=label)
        try:
            items = r.json().get('bookings') if r.status == 200 else None
        except ValueError:
            items = None
        return r, items

    def delete_booking(self, run, token, bid):
        return run.http('DELETE', f'{self.api()}/booking/{bid}', headers={'Cookie': f'token={token}'}, label=f'sut04-delete-{bid}')

    def mine(self, items):
        """The bookings of room 1 that this condition made (its first name)."""
        return [b for b in (items or []) if b.get('firstname') == self.marker]

    def api_booking(self, items):
        """The identity attributes of the bookings of this execution that the API layer shows."""
        hits = [b for b in (items or []) if b.get('firstname') == self.u['firstname'] and b.get('lastname') == self.u['lastname']]
        first = hits[0] if hits else {}
        dates = first.get('bookingdates') or {}
        return {'booking_count': len(hits), 'firstname': first.get('firstname'), 'lastname': first.get('lastname'),
                'checkin': dates.get('checkin'), 'checkout': dates.get('checkout')}

    # ---- blocks ---------------------------------------------------------------------------------------------------
    def reset(self, run):
        with run.step('reset', "DELETE /booking/{id} for every booking of room 1 with this condition's first name", ['API_RESET']) as rec:
            r, token = self.login(run)
            rec['evidence'].append(r.evidence)
            obs = {'login_status': r.status, 'token_cookie_received': bool(token)}
            rec['observation'] = obs
            if r.status != 200 or not token:
                rec['outcome'] = 'FAILURE'
                return
            self.carry = {'token': token}
            r, items = self.list_bookings(run, token, 'sut04-bookings-before-reset')
            rec['evidence'].append(r.evidence)
            if items is None:
                obs['list_status'] = r.status
                rec['outcome'] = 'FAILURE'
                return
            mine = self.mine(items)
            obs.update({'bookings_in_room_1': len(items), 'bookings_to_delete': [b.get('bookingid') for b in mine], 'delete_statuses': {}})
            for b in mine:
                d = self.delete_booking(run, token, b.get('bookingid'))
                rec['evidence'].append(d.evidence)
                obs['delete_statuses'][str(b.get('bookingid'))] = d.status if d.status is not None else d.error
                if d.status != 202:
                    rec['outcome'] = 'FAILURE'
        with run.step('reset', 'admin login in the new browser context (the admin web session of the web layer)', ['PREDEFINED_ACCOUNT']) as rec:
            status, token = self.ui.admin_login()
            rec['observation'] = {'status': status, 'token_cookie_present': bool(token)}
            if not token:
                rec['outcome'] = 'FAILURE'

    def check_start(self, run):
        with run.step('starting-state', "GET /booking/?roomid=1: no booking with this condition's first name") as rec:
            r, items = self.list_bookings(run, self.carry['token'], 'sut04-bookings-start')
            rec['evidence'].append(r.evidence)
            mine = self.mine(items)
            rec['observation'] = {'status': r.status, 'bookings_in_room_1': None if items is None else len(items),
                                  'bookings_with_the_condition_first_name': len(mine), 'names_and_dates_of_the_execution': self.u}
            if items is None or mine:
                rec['outcome'] = 'FAILURE'

    def established_record(self):
        return {'booking_count': 1, 'firstname': self.u['firstname'], 'lastname': self.u['lastname'], 'checkin': self.u['checkin'],
                'checkout': self.u['checkout']}


class ApiWeb(Sut04):
    """E07-CS005-SUT04-API-WEB: establishment through the booking API (POST /booking/), verification on the admin room page of the web app."""
    SPEC = SPEC_API_WEB
    KEYS = KEYS_WEB

    def establish(self, run):
        u = self.u
        with run.step('establishment', 'POST /booking/ for room 1 with the guest names and dates of the execution, without email and phone (API layer)',
                      ['API_SEED']) as rec:
            body = {'roomid': ROOM, 'firstname': u['firstname'], 'lastname': u['lastname'], 'depositpaid': False,
                    'bookingdates': {'checkin': u['checkin'], 'checkout': u['checkout']}}
            r = run.http('POST', f'{self.api()}/booking/', body, headers={'Cookie': f'token={self.carry["token"]}'}, label='sut04-create')
            try:
                bid = r.json().get('bookingid') if r.status == 201 else None
            except ValueError:
                bid = None
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status, 'booking_id': bid}
            self.carry['bid'] = bid
            if bid is None:
                rec['outcome'] = 'FAILURE'

    def establish_check(self, run):
        u = self.u
        with run.step('establishment-check', 'GET /booking/{id} answers 200 with the guest names and dates of the execution (API layer, read-only)') as rec:
            r = run.http('GET', f'{self.api()}/booking/{self.carry["bid"]}', headers={'Cookie': f'token={self.carry["token"]}'}, label='sut04-get-established')
            rec['evidence'].append(r.evidence)
            try:
                body = r.json() if r.status == 200 else {}
            except ValueError:
                body = {}
            dates = body.get('bookingdates') or {}
            rec['observation'] = {'status': r.status}
            run.identity['established'] = self.established_record()
            if not (r.status == 200 and body.get('firstname') == u['firstname'] and body.get('lastname') == u['lastname']
                    and dates.get('checkin') == u['checkin'] and dates.get('checkout') == u['checkout']):
                rec['outcome'] = 'FAILURE'

    def verify(self, run):
        u = self.u
        with run.step('verification', '{web}/admin/room/1 lists one row with the guest names and the check-in and check-out dates of the execution (WEB layer, read-only)') as rec:
            status, texts = self.ui.admin_room_rows()
            hits = [t for t in texts if u['firstname'] in t and u['lastname'] in t]
            first = hits[0] if hits else ''
            observed = {'booking_count': len(hits), 'firstname': u['firstname'] if hits else None, 'lastname': u['lastname'] if hits else None,
                        'checkin': u['checkin'] if hits and u['checkin'] in first else None,
                        'checkout': u['checkout'] if hits and u['checkout'] in first else None}
            rec['evidence'].append(run.text('sut04-web-admin-rows', '\n---\n'.join(texts)))
            self.ui.picture(run, rec, 'sut04-web-admin-room')
            self.conclude(run, rec, observed, page_status=status, rows=len(texts))


class WebApi(Sut04):
    """E07-CS006-SUT04-WEB-API: establishment through the reservation form of the web app, verification on the booking listing of room 1."""
    SPEC = SPEC_WEB_API
    KEYS = KEYS_API

    def establish(self, run):
        with run.step('establishment', 'web booking form at {web}/reservation/1 with the guest names and dates of the execution (WEB layer)',
                      ['DIRECT_ROUTE', 'UI_FLOW']) as rec:
            rec['observation'] = self.ui.submit_reservation(self.u)
            if not rec['observation'].get('submitted'):
                rec['outcome'] = 'FAILURE'

    def establish_check(self, run):
        with run.step('establishment-check', "the web app shows 'Booking Confirmed' (WEB layer, read-only)") as rec:
            confirmed = self.ui.confirmation_visible()
            self.ui.picture(run, rec, 'sut04-web-booking-confirmed')
            rec['observation'] = {'confirmation_visible': confirmed}
            run.identity['established'] = self.established_record()
            if not confirmed:
                rec['outcome'] = 'FAILURE'

    def verify(self, run):
        with run.step('verification', 'GET /booking/?roomid=1: one booking with the guest names, check-in and check-out dates of the execution (API layer, read-only)') as rec:
            r, items = self.list_bookings(run, self.carry['token'], 'sut04-bookings-verification')
            rec['evidence'].append(r.evidence)
            observed = self.api_booking(items) if items is not None else {}
            self.conclude(run, rec, observed, status=r.status, transport_error=r.error)


REALIZATIONS = {'E07-CS005-SUT04-API-WEB': ApiWeb, 'E07-CS006-SUT04-WEB-API': WebApi}
