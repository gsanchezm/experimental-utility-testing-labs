"""E03-CS001-SUT04-WEB (README section 4.6; reset through the surface's own control, section 3 item 10). DRAFT (operation OP-PREP-E03).

The reset action is the run's booking row's own delete control; its DELETE request and the re-fetch belong to the control's
own handler, not to the experimenter. The reset mechanism stays API_RESET (the control issues the mapping's DELETE).
"""
import time

from . import common, instance, sut04_api, web

MODALITY, PLATFORM = 'Web UI Functional', 'web'
RESET_MECHANISMS = ['API_RESET']
ESTABLISHMENT_MECHANISMS = ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW']
EXPECTED = "after the row's delete control, the admin room page shows no row with the run's names and dates"
CITATIONS = ['experiments/scenario-mappings/CS-001.yaml (SUT-04 entry)', 'SUT04-EV-0003', 'SUT04-EV-0004', 'SUT04-EV-0006', 'SUT04-EV-0008',
             'assets/src/components/admin/BookingListing.tsx:27-37,107-116@d36bd3f']
NOTE = ('reset_mechanisms API_RESET: the reset is triggered through the web surface own control (the booking row delete control), '
        'which issues the mapping DELETE /booking/{id}; the frozen vocabulary has no token for a reset triggered through a UI control, '
        'and APP_DATA_CLEAR would misdescribe a server-side delete')


def components(run):
    return instance.components(run, [('web', 'web'), ('api', 'api')])


def rows(b, u):
    texts = b.page.locator('div.detail.booking-1').all_inner_texts()
    return texts, [t for t in texts if u['firstname'] in t and u['lastname'] in t and u['checkin'] in t]


def run(run):
    site, booking = instance.base(run.instance, 'web'), instance.base(run.instance, 'api')
    u = sut04_api.unique(run.env.run_id)
    b = web.Browser(run)
    try:
        with run.step('precondition', 'admin web login at {web}/admin (the token cookie the web app forwards to the booking service)', ['PREDEFINED_ACCOUNT']) as s:
            status = b.goto(site + '/admin')
            b.page.locator('#username').fill('admin')
            b.page.locator('#password').fill('password')
            b.page.locator('#doLogin').click()
            b.page.wait_for_url('**/admin/rooms', timeout=web.NAV_TIMEOUT_MS)
            token = next((c['value'] for c in b.context.cookies() if c.get('name') == 'token'), None)
            run.scrub.secret(token)
            s['observation'] = {'status': status, 'url': b.page.url, 'token_cookie_present': bool(token)}
            if not token:
                s['outcome'] = 'FAILURE'
        sut04_api.starting_state(run, booking, token, u)
        bid = None
        with run.step('establishment', 'web booking form at {web}/reservation/1 with the run-unique names and dates', ['DIRECT_ROUTE', 'UI_FLOW']) as s:
            status = b.goto(f"{site}/reservation/1?checkin={u['checkin']}&checkout={u['checkout']}")
            b.page.locator('#doReservation').click()
            b.page.locator('.room-firstname').fill(u['firstname'])
            b.page.locator('.room-lastname').fill(u['lastname'])
            b.page.locator('.room-email').fill(u['email'])
            b.page.locator('.room-phone').fill(u['phone'])
            b.page.get_by_role('button', name='Reserve Now').click()
            b.page.get_by_text('Booking Confirmed').wait_for(state='visible', timeout=web.NAV_TIMEOUT_MS)
            run.capture(s, b.shot, 'sut04-web-booking-confirmed')
            r, items = sut04_api.bookings(run, booking, token, 'sut04-web-bookings-after-establishment')
            s['evidence'].append(r.evidence)
            found = sut04_api.mine(items, u)
            bid = found[0].get('bookingid') if len(found) == 1 else None
            s['observation'] = {'status': status, 'booking_id': bid, 'matching_bookings': len(found)}
            if bid is None:
                s['outcome'] = 'FAILURE'
        with run.step('pre-reset-verification', "{web}/admin/room/1 lists the run's row") as s:
            b.goto(site + '/admin/room/1')
            b.page.locator('div.detail.booking-1').filter(has_text=u['firstname']).filter(has_text=u['lastname']).first.wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            texts, mine = rows(b, u)
            s['observation'] = {'rows': len(texts), 'rows_with_the_run_names': len(mine)}
            if len(mine) != 1:
                s['outcome'] = 'FAILURE'
            run.capture(s, b.shot, 'sut04-web-pre-reset')
        mark = None
        with run.action('reset action', "click the run's booking row's own delete control (span.fa-trash.bookingDelete)") as a:
            row = b.page.locator('div.detail.booking-1').filter(has_text=u['firstname']).filter(has_text=u['lastname']).first
            mark = time.monotonic()
            with b.page.expect_response(lambda r: r.request.method == 'DELETE' and '/api/booking/' in r.url, timeout=web.NAV_TIMEOUT_MS) as info:
                row.locator('span.bookingDelete').click()
            resp = info.value
            a['observation'] = {'delete_request': f'DELETE {resp.url}', 'delete_status': resp.status, 'booking_id': bid}
            a['outcome'] = 'SUCCESS' if 200 <= resp.status < 300 else 'FAILURE'
            run.capture(a, lambda: resp.text()[:200], key='delete_body')
        found = None
        with run.action('UI action', "read the booking rows after the control's own re-fetch has answered") as a:
            # The re-fetch has answered when its chain's final non-3xx response arrived (GET /api/booking/?roomid=1 answers 308 to the
            # path without the slash); then 500 ms without a new network event (bounded by the settle budget of README section 10).
            t0, chain, final = time.monotonic(), [], None
            while time.monotonic() - t0 < web.ACTION_TIMEOUT_MS / 1000:
                chain = [n for n in b.responses_since(mark or 0, 'GET', '/api/booking') if 'roomid=1' in n['url']]
                final = next((n for n in chain if not 300 <= n['status'] < 400), None)
                if final:
                    break
                b.page.wait_for_timeout(250)
            q0, seen, since = time.monotonic(), len(b.net), time.monotonic()
            while time.monotonic() - q0 < web.SETTLE_TIMEOUT_MS / 1000 and time.monotonic() - since < 0.5:
                b.page.wait_for_timeout(100)
                if len(b.net) != seen:
                    seen, since = len(b.net), time.monotonic()
            quiet = {'quiet_500ms': time.monotonic() - since >= 0.5, 'elapsed_s': round(time.monotonic() - q0, 3)}
            settle = b.settle()
            texts, found = rows(b, u)
            a['observation'] = {'refetch_answered': final is not None, 'refetch_chain': [n['status'] for n in chain],
                                'refetch_final_status': final['status'] if final else None, 'quiet_wait': quiet, 'rows': len(texts),
                                'rows_with_the_run_names': len(found), 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut04-web-after-reset')
            run.capture(a, b.dom, 'sut04-web-room-text')
    finally:
        b.close()
    notes = [NOTE, 'the guest form sends email and phone; the message the source posts for them is outside the oracle']
    if found is None:
        return common.Result('INCONCLUSIVE', EXPECTED, 'the booking rows could not be read', RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS, notes)
    return common.Result('SUCCESS' if not found else 'FAILURE', EXPECTED, f"rows with the run's names and dates after the reset: {len(found)}",
                         RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS, notes)
