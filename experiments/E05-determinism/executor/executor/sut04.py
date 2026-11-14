"""E05 realizations on SUT-04: E05-SUT04-API-01, E05-SUT04-API-02 (api) and E05-SUT04-WEB-01 (web). DRAFT (operation OP-PREP-E05).

For SUT-04, instance.json surfaces.api is the booking service, surfaces.auth the auth service, surfaces.message the message service (the real one
on port 3006; manifests/source-reads-v2.yaml, F13 to F15) and surfaces.web the web app.

Blocks per execution: reset = delete every booking of room 1 that carries this condition's guest names (found by listing, so that an execution
interrupted before its own cleanup cannot leave a booking that nothing deletes), starting-state check = room 1 holds no booking with those
names (a reset that did not hold is therefore seen by the next execution), establishment = the CS-001 booking, verification = it answers 200
(web: the admin room page lists its row), stimulus = a second booking request (overlapping dates for API-01 and WEB-01, so rejected-only;
an accepted booking with email and phone and non-overlapping dates for API-02, followed by a read of the message count).

Guest names and dates are fixed per condition (a function of the condition id), not of the run id: with run-unique names the starting-state
check would hold trivially after a failed reset (IMPLEMENTATION-NOTES.md, point 13)."""
import datetime
import hashlib
import re
import time

from . import attempt, common, instance, web

ROOM = 1
PHONE = '01234567890'  # 11 characters: the message service accepts 11 to 21 (source-reads-v2.yaml, F15)
MESSAGE_WAIT_S, MESSAGE_POLL_S = 5.0, 0.5
SPEC_API = common.Spec('API', 'api', ['API_RESET'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api'), ('auth', 'auth')], True)
SPEC_API_MSG = common.Spec('API', 'api', ['API_RESET'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api'), ('auth', 'auth'), ('message', 'message')], True)
SPEC_WEB = common.Spec('Web UI Functional', 'web', ['API_RESET'], ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'], [('web', 'web'), ('api', 'api')], True)


def unique(condition_id):
    """Guest names, dates, and contact values of one condition: stable across its executions (derived from the condition id)."""
    d = hashlib.sha256(('E05|' + condition_id).encode()).digest()
    letters = ''.join(chr(ord('a') + b % 26) for b in d[:16])
    checkin = datetime.date(2031, 1, 1) + datetime.timedelta(days=int.from_bytes(d[16:20], 'big') % 3000)
    later = checkin + datetime.timedelta(days=10)
    return {'firstname': 'E' + letters[:7], 'lastname': 'R' + letters[7:15], 'checkin': checkin.isoformat(),
            'checkout': (checkin + datetime.timedelta(days=1)).isoformat(),
            's_firstname': 'S' + letters[:7], 's_lastname': 'T' + letters[7:15], 's_checkin': later.isoformat(),
            's_checkout': (later + datetime.timedelta(days=1)).isoformat(), 'email': f'e05.{letters[:10]}@example.com', 'phone': PHONE}


def is_mine(b, u):
    """A booking of room 1 that this condition made: the CS-001 booking or a stimulus booking (either set of guest names)."""
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
            r = run.http('GET', f'{self.api()}/booking/{self.carry["bid"]}', headers={'Cookie': f'token={self.carry["token"]}'}, label='sut04-get-pre-stimulus')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status}
            if r.status != 200:
                rec['outcome'] = 'FAILURE'


class Api01(Sut04):
    """Stimulus: POST /booking/ for room 1 with overlapping dates, no email or phone (F09: HTTP 409 with no body)."""

    def stimulus(self, run):
        with run.observe('stimulus', 'POST /booking/ for room 1 with dates that overlap the CS-001 booking') as rec:
            run.mark_stimulus_sent()
            r, bid = self.create_booking(run, self.carry['token'], self.u['s_firstname'], self.u['s_lastname'], self.u['checkin'], self.u['checkout'],
                                         'sut04-stimulus-booking')
            rec['evidence'].append(r.evidence)
            obs = {'status': r.status, 'error': r.error, 'body_bytes': len(r.body), 'booking_id': bid}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if obs['status'] == 409 and obs['body_bytes'] == 0:
            return 'S_CONFLICT_REJECTED', 'HTTP 409 with no body'
        if obs['status'] == 201:
            return 'S_CREATED_UNEXPECTED', f'HTTP 201, booking id {obs["booking_id"]}'
        return 'S_OTHER_STATUS', f'HTTP {obs["status"]}, {obs["body_bytes"]} body bytes'


class Api02(Sut04):
    """Stimulus: an accepted booking with email and phone on non-overlapping dates (D-03 follow-up); its message is read through the real
    message service (GET {message}/message/count). The message record that the service keeps is residual state and is never deleted."""
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
        with run.step('verification', 'GET {message}/message/count answers with a count (the baseline of the stimulus)') as rec:
            r, count = self.message_count(run, 'sut04-message-count-before')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status, 'count': count}
            if count is None:
                rec['outcome'] = 'FAILURE'
            self.carry['message_before'] = count

    def stimulus(self, run):
        with run.observe('stimulus', 'POST /booking/ for room 1 with email and phone on non-overlapping dates, then read the message count') as rec:
            run.mark_stimulus_sent()
            r, bid = self.create_booking(run, self.carry['token'], self.u['s_firstname'], self.u['s_lastname'], self.u['s_checkin'], self.u['s_checkout'],
                                         'sut04-stimulus-booking', contact=True)
            rec['evidence'].append(r.evidence)
            obs = {'status': r.status, 'error': r.error, 'booking_id': bid, 'message_before': self.carry.get('message_before')}
            rec['observation'] = obs
            if r.status is not None and 200 <= r.status < 300:
                waited, after = 0.0, None
                while True:
                    c, after = self.message_count(run, 'sut04-message-count-after')
                    rec['evidence'].append(c.evidence)
                    if after is None or after > obs['message_before'] or waited >= MESSAGE_WAIT_S:
                        break
                    time.sleep(MESSAGE_POLL_S)
                    waited += MESSAGE_POLL_S
                obs.update({'message_after': after, 'message_wait_s': waited})
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if not 200 <= obs['status'] < 300:
            return 'S_BOOKING_NON_2XX', f'HTTP {obs["status"]}'
        after, before = obs.get('message_after'), obs.get('message_before')
        if after is None:
            return 'S_MESSAGE_COUNT_UNREADABLE', f'HTTP {obs["status"]}; the message count after the stimulus could not be read'
        if after - before == 1:
            return 'S_MESSAGE_RECORD_PRESENT', f'HTTP {obs["status"]}; message count {before} -> {after}'
        if after == before:
            return 'S_MESSAGE_RECORD_ABSENT', f'HTTP {obs["status"]}; message count {before} -> {after} after {obs["message_wait_s"]} s'
        return 'S_MESSAGE_COUNT_UNEXPECTED', f'HTTP {obs["status"]}; message count {before} -> {after}'


class Web01(Sut04):
    """Web: the admin login, the booking form, and the admin room page of the E03 SUT-04 web realization (executor README 4.6)."""
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
            run.capture(rec, b.shot, 'sut04-web-pre-stimulus')

    def stimulus(self, run):
        u, b = self.u, self.b
        with run.observe('stimulus', 'second reservation through the web form for room 1 with dates that overlap the CS-001 booking') as rec:
            b.goto(f"{self.site}/reservation/1?checkin={u['checkin']}&checkout={u['checkout']}")
            b.page.locator('#doReservation').click()
            b.page.locator('.room-firstname').fill(u['s_firstname'])
            b.page.locator('.room-lastname').fill(u['s_lastname'])
            b.page.locator('.room-email').fill(u['email'])
            b.page.locator('.room-phone').fill(u['phone'])
            run.mark_stimulus_sent()
            post = None
            try:
                with b.page.expect_response(lambda r: r.request.method == 'POST' and '/api/booking' in r.url, timeout=web.NAV_TIMEOUT_MS) as info:
                    b.page.get_by_role('button', name='Reserve Now').click()
                post = info.value.status
            except Exception as e:  # noqa: BLE001 - no answer to the form post is an observation; the DOM is still read
                rec['post_error'] = f'{e.__class__.__name__}'
            settle = b.settle()
            confirmed = b.page.get_by_text('Booking Confirmed').count() > 0
            form_remains = b.page.locator('.room-firstname').count() > 0
            body_text = b.page.locator('body').inner_text(timeout=web.ACTION_TIMEOUT_MS)
            page_state = 'form_remains' if form_remains else ('error_page' if "couldn\u2019t load" in body_text or "couldn't load" in body_text else 'other')
            run.capture(rec, b.shot, 'sut04-web-after-stimulus')
            run.capture(rec, b.dom, 'sut04-web-stimulus-text')
            obs = {'post_status': post, 'confirmation_visible': confirmed, 'form_remains': form_remains, 'page_state': page_state, 'settle': settle}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['confirmation_visible']:
            return 'S_BOOKING_CONFIRMED', f'confirmation shown; form post answered {obs["post_status"]}'
        if obs['post_status'] == 409:
            # F09: a conflict answers 409 with no body. The page state afterwards (form still shown, or the framework error page that the
            # first DRY_RUN showed, F10 corrected) is evidence in the observation and in the screenshot, not part of the category.
            return 'S_NO_CONFIRMATION_SHOWN', f'form post answered 409 and no confirmation is shown; page state {obs["page_state"]}'
        return 'S_OTHER', f'no confirmation; form post answered {obs["post_status"]}; page state {obs["page_state"]}'


REALIZATIONS = {'E05-SUT04-API-01': Api01, 'E05-SUT04-API-02': Api02, 'E05-SUT04-WEB-01': Web01}
