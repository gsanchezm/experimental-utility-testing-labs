"""E04 realizations on SUT-04: E04-SUT04-API-01, E04-SUT04-API-02 (api) and E04-SUT04-WEB-01 (web). DRAFT (operation OP-PREP-E04).

For SUT-04, instance.json surfaces.api is the booking service, surfaces.auth the auth service, surfaces.message the message service (the real one
on port 3006; manifests/source-reads-v2.yaml, F13 to F15) and surfaces.web the web app.

Blocks per attempt: reset = delete every booking of room 1 that carries this condition's guest names (found by listing, so that an attempt
interrupted before its own cleanup cannot leave a booking that nothing deletes), starting-state check = room 1 holds no booking with those names
(a reset that did not hold is therefore seen by the next attempt), establishment = the CS-001 booking, verification = it answers 200 (web: the
admin room page lists its row). For E04-SUT04-API-02 the verification also reads the message count that the E05 stimulus used as its baseline;
it is kept as part of the E05 verification block (an open item of the START package). The stimulus blocks of the E05 counterparts (a second
booking request; the message read after an accepted booking) are removed.

Guest names and dates are fixed per condition (a function of the condition id), not of the attempt id: with attempt-unique names the
starting-state check would hold trivially after a failed reset (E05 IMPLEMENTATION-NOTES.md, point 13).
"""
import datetime
import hashlib
import re

from . import attempt, common, instance, web

ROOM = 1
PHONE = '01234567890'  # 11 characters: the message service accepts 11 to 21 (source-reads-v2.yaml, F15)
SPEC_API = common.Spec('API', 'api', ['API_RESET'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api'), ('auth', 'auth')], True)
SPEC_API_MSG = common.Spec('API', 'api', ['API_RESET'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api'), ('auth', 'auth'), ('message', 'message')], True)
SPEC_WEB = common.Spec('Web UI Functional', 'web', ['API_RESET'], ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'], [('web', 'web'), ('api', 'api')], True)


def unique(condition_id):
    """Guest names, dates, and contact values of one condition: stable across its executions (derived from the condition id)."""
    d = hashlib.sha256(('E04|' + condition_id).encode()).digest()
    letters = ''.join(chr(ord('a') + b % 26) for b in d[:16])
    checkin = datetime.date(2031, 1, 1) + datetime.timedelta(days=int.from_bytes(d[16:20], 'big') % 3000)
    later = checkin + datetime.timedelta(days=10)
    return {'firstname': 'E' + letters[:7], 'lastname': 'R' + letters[7:15], 'checkin': checkin.isoformat(),
            'checkout': (checkin + datetime.timedelta(days=1)).isoformat(),
            's_firstname': 'S' + letters[:7], 's_lastname': 'T' + letters[7:15], 's_checkin': later.isoformat(),
            's_checkout': (later + datetime.timedelta(days=1)).isoformat(), 'email': f'e05.{letters[:10]}@example.com', 'phone': PHONE}


def is_mine(b, u):
    """A booking of room 1 that this condition made: the CS-001 booking, or a booking under the stimulus guest names of the E05 counterpart (the reset is kept as in E05)."""
    pairs = ((u['firstname'], u['lastname']), (u['s_firstname'], u['s_lastname']))
    return (b.get('firstname'), b.get('lastname')) in pairs


class Sut04(attempt.Realization):
    SPEC = SPEC_API

    def __init__(self, job):
        super().__init__(job)
        self.u = unique(job.env.condition)

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

    def create_booking(self, run, token, first, last, checkin, checkout, label, contact=False):
        body = {'roomid': ROOM, 'firstname': first, 'lastname': last, 'depositpaid': False, 'bookingdates': {'checkin': checkin, 'checkout': checkout}}
        if contact:
            body.update({'email': self.u['email'], 'phone': self.u['phone']})
        r = run.http('POST', f'{self.api()}/booking/', body, headers={'Cookie': f'token={token}'}, label=label)
        try:
            bid = r.json().get('bookingid') if r.status == 201 else None
        except ValueError:
            bid = None
        return r, bid

    def reset(self, run):
        with run.step('reset', "DELETE /booking/{id} for every booking of room 1 with this condition's guest names", ['API_RESET']) as rec:
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
            mine = [b for b in items if is_mine(b, self.u)]
            obs.update({'bookings_in_room_1': len(items), 'bookings_to_delete': [b.get('bookingid') for b in mine], 'delete_statuses': {}})
            for b in mine:
                d = self.delete_booking(run, token, b.get('bookingid'))
                rec['evidence'].append(d.evidence)
                obs['delete_statuses'][str(b.get('bookingid'))] = d.status if d.status is not None else d.error
                if d.status != 202:
                    rec['outcome'] = 'FAILURE'

    def check_start(self, run):
        with run.step('starting-state', "GET /booking/?roomid=1: no booking with this condition's guest names") as rec:
            r, items = self.list_bookings(run, self.carry['token'], 'sut04-bookings-start')
            rec['evidence'].append(r.evidence)
            mine = [b for b in (items or []) if is_mine(b, self.u)]
            rec['observation'] = {'status': r.status, 'bookings_in_room_1': None if items is None else len(items),
                                  'bookings_with_the_condition_names': len(mine), 'names_and_dates': self.u}
            if items is None or mine:
                rec['outcome'] = 'FAILURE'

    def establish(self, run):
        with run.step('establishment', 'POST /booking/ for room 1 with the condition guest names, without email and phone', ['API_SEED']) as rec:
            r, bid = self.create_booking(run, self.carry['token'], self.u['firstname'], self.u['lastname'], self.u['checkin'], self.u['checkout'],
                                         'sut04-create')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status, 'booking_id': bid}
            if bid is None:
                rec['outcome'] = 'FAILURE'
            self.carry['bid'] = bid

    def verify_target(self, run):
        with run.step('verification', 'GET /booking/{id} answers 200') as rec:
            r = run.http('GET', f'{self.api()}/booking/{self.carry["bid"]}', headers={'Cookie': f'token={self.carry["token"]}'}, label='sut04-get-target-state')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status}
            if r.status != 200:
                rec['outcome'] = 'FAILURE'


class Api01(Sut04):
    """E04-SUT04-API-01 (establishment-only). Reset, starting-state check, establishment and verification are those of E05-SUT04-API-01; the stimulus (a booking with dates that overlap the target booking) is removed."""


class Api02(Sut04):
    """E04-SUT04-API-02 (establishment-only). Verification includes the message-count baseline of E05-SUT04-API-02 (open item); the stimulus (an accepted booking and the message read) is removed."""
    SPEC = SPEC_API_MSG

    def message_count(self, run, label):
        r = run.http('GET', f'{instance.base(self.job.instance, "message")}/message/count', label=label)
        try:
            body = r.json() if r.status == 200 else None
        except ValueError:
            body = None
        value = body.get('count') if isinstance(body, dict) else body
        count = value if isinstance(value, int) and not isinstance(value, bool) else None
        return r, count

    def verify_target(self, run):
        super().verify_target(run)
        with run.step('verification', 'GET {message}/message/count answers with a count (the baseline of the E05 stimulus)') as rec:
            r, count = self.message_count(run, 'sut04-message-count-before')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status, 'count': count}
            if count is None:
                rec['outcome'] = 'FAILURE'
            self.carry['message_before'] = count


class Web01(Sut04):
    """E04-SUT04-WEB-01 (establishment-only): admin login, delete of the condition bookings through the web control, the booking through the web form and the admin room page; the stimulus (a second reservation with overlapping dates) is removed."""
    SPEC = SPEC_WEB

    def open(self):
        self.b = web.Browser(self.job)

    def bind(self, run):
        self.b.bind(run)

    def end(self, run):
        self.b.flush()

    def close(self):
        self.b.close()

    @property
    def site(self):
        return instance.base(self.job.instance, 'web')

    def rows(self):
        texts = self.b.page.locator('div.detail.booking-1').all_inner_texts()
        return texts, [t for t in texts if (self.u['firstname'] in t and self.u['lastname'] in t) or (self.u['s_firstname'] in t and self.u['s_lastname'] in t)]

    def web_login(self, run):
        b = self.b
        status = b.goto(self.site + '/admin')
        b.settle()  # a logged-in session is redirected by the page itself; a navigation started meanwhile is aborted (first DRY_RUN, ERR_ABORTED)
        if b.page.locator('#username').count():
            b.page.locator('#username').fill('admin')
            b.page.locator('#password').fill('password')
            b.page.locator('#doLogin').click()
            b.page.wait_for_url('**/admin/rooms', timeout=web.NAV_TIMEOUT_MS)
        token = next((c['value'] for c in b.context.cookies() if c.get('name') == 'token'), None)
        run.scrub.secret(token)
        return status, token

    def reset(self, run):
        with run.step('reset', "admin web login, then the delete control of every booking row of room 1 with this condition's guest names", ['API_RESET']) as rec:
            status, token = self.web_login(run)
            obs = {'status': status, 'url': self.b.page.url, 'token_cookie_present': bool(token)}
            rec['observation'] = obs
            if not token:
                rec['outcome'] = 'FAILURE'
                return
            self.carry = {'token': token}
            self.b.goto(self.site + '/admin/room/1')
            self.b.settle()
            texts, mine = self.rows()
            obs.update({'rows': len(texts), 'rows_to_delete': len(mine), 'delete_statuses': []})
            for _ in range(len(mine)):
                row = self.b.page.locator('div.detail.booking-1').filter(has_text=self.u['firstname']).first
                if not row.count():
                    row = self.b.page.locator('div.detail.booking-1').filter(has_text=self.u['s_firstname']).first
                with self.b.page.expect_response(lambda r: r.request.method == 'DELETE' and '/api/booking/' in r.url, timeout=web.NAV_TIMEOUT_MS) as info:
                    row.locator('span.bookingDelete').click()
                obs['delete_statuses'].append(info.value.status)
                if not 200 <= info.value.status < 300:
                    rec['outcome'] = 'FAILURE'
                self.b.settle()
            run.capture(rec, self.b.shot, 'sut04-web-after-reset')

    def establish(self, run):
        u, b = self.u, self.b
        with run.step('establishment', 'web booking form at {web}/reservation/1 with the condition guest names and dates', ['DIRECT_ROUTE', 'UI_FLOW']) as rec:
            status = b.goto(f"{self.site}/reservation/1?checkin={u['checkin']}&checkout={u['checkout']}")
            b.page.locator('#doReservation').click()
            b.page.locator('.room-firstname').fill(u['firstname'])
            b.page.locator('.room-lastname').fill(u['lastname'])
            b.page.locator('.room-email').fill(u['email'])
            b.page.locator('.room-phone').fill(u['phone'])
            b.page.get_by_role('button', name='Reserve Now').click()
            confirmed = b.visible(b.page.get_by_text('Booking Confirmed'), web.NAV_TIMEOUT_MS)
            run.capture(rec, b.shot, 'sut04-web-booking-confirmed')
            rec['observation'] = {'status': status, 'confirmation_visible': confirmed}
            if not confirmed:
                rec['outcome'] = 'FAILURE'

    def verify_target(self, run):
        b = self.b
        with run.step('verification', "{web}/admin/room/1 lists the CS-001 booking row") as rec:
            b.goto(self.site + '/admin/room/1')
            shown = b.visible(b.page.locator('div.detail.booking-1').filter(has_text=self.u['firstname']).filter(has_text=self.u['lastname']))
            texts, mine = self.rows()
            rec['observation'] = {'row_visible': shown, 'rows': len(texts), 'rows_with_the_condition_names': len(mine)}
            if not shown or len(mine) != 1:
                rec['outcome'] = 'FAILURE'
            run.capture(rec, b.shot, 'sut04-web-target-state')


REALIZATIONS = {'E04-SUT04-API-01': Api01, 'E04-SUT04-API-02': Api02, 'E04-SUT04-WEB-01': Web01}
