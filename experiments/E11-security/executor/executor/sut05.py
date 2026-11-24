"""E11 realizations on SUT-05 (Juice Shop, release v20.2.0 by the Packaged Distributions route): the twelve cells of the three conditions.

DRAFT (operation OP-PREP-E11). Blocks per execution: reset = restart of the instance process (ENVIRONMENT_RESTART: the challenge `solved` flags
live in the process, so a restart is a fresh instance), starting-state check = the oracle challenge of the cell is not solved, method = M1 (a
fixed request sequence, then the `solved` flag read from GET /api/Challenges) or M2 (one restricted ZAP run, zap.py), classification =
the matching rules of campaign-configuration-draft.md, section 4b. Payloads, control sequences and control endpoints come from the cells file
(`source_reading`, `matching_rules`, the `control_endpoint` of a CONTROL cell), which records the source reading V-10; nothing is chosen here.
"""
import json
import time
import urllib.parse

from . import attempt, common, instance, zap

SPEC = common.Spec('Security Testing', 'api', ['ENVIRONMENT_RESTART'], None, [('api', 'api')], True)
CONDITIONS = ('SQLI-LOGIN', 'SQLI-SEARCH', 'DIRLIST-FTP')
ORACLE_KEY = {'SQLI-LOGIN': 'loginAdminChallenge', 'SQLI-SEARCH': 'unionSqlInjectionChallenge', 'DIRLIST-FTP': 'directoryListingChallenge'}
M2_RULE = {'SQLI-LOGIN': '40018', 'SQLI-SEARCH': '40018', 'DIRLIST-FTP': '0'}
# the body of the seed request of a login-like M2 run: a request of the same shape as the endpoint accepts, never an attack
SEED_BODY = {'SQLI-LOGIN': {'email': 'user@example.org', 'password': 'x'}}
CONTROL_BODY = {'POST /api/Users': {'email': 'ctrl@example.org', 'password': 'Passw0rd!', 'passwordRepeat': 'Passw0rd!'}}


def _split(endpoint):
    """'GET /rest/user/security-question?email=' -> ('GET', '/rest/user/security-question', 'email=') (query part kept for the seed)."""
    method, rest = endpoint.split(' ', 1)
    parts = urllib.parse.urlsplit(rest)
    return method, parts.path, parts.query


class Sut05Cell(attempt.Realization):
    SPEC = SPEC
    LAUNCHER_FACTORY = zap.DockerLauncher  # replaced in tests by a launcher that starts nothing

    def __init__(self, job):
        super().__init__(job)
        self.cond = job.c['condition']
        self.control = job.c['kind'] == 'CONTROL'
        self.key = ORACLE_KEY[self.cond]

    def api(self):
        return instance.base(self.job.instance, 'api')

    def challenge(self, run, label):
        """GET /api/Challenges and return (response, solved flag of the cell's oracle key or None when it cannot be read)."""
        r = run.http('GET', f'{self.api()}/api/Challenges', label=label)
        solved = None
        if r.status == 200:
            try:
                for ch in r.json().get('data') or []:
                    if ch.get('key') == self.key:
                        solved = bool(ch.get('solved'))
            except ValueError:
                solved = None
        return r, solved

    def reset(self, run):
        with run.step('reset', 'restart the SUT process (SIGTERM to the process group, port refused, start in a new session and group, readiness)',
                      ['ENVIRONMENT_RESTART']) as rec:
            instance.restart(run, rec)
        self.carry = {}

    def check_start(self, run):
        with run.step('starting-state', f'GET /api/Challenges: the challenge {self.key} is not solved') as rec:
            r, solved = self.challenge(run, 'sut05-oracle-start')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status, 'oracle_key': self.key, 'solved': solved}
            if r.status != 200 or solved is not False:
                rec['outcome'] = 'FAILURE'


class M1(Sut05Cell):
    """M1 targeted check: a fixed request sequence, then the `solved` flag of the oracle challenge (SUT05-EV-0011).

    The flag of some challenges is written after the response (the union injection solves it in a follow-up query), so the oracle is read
    until it reads solved or ORACLE_WAIT_S elapse: the sequence is sent once, only the READ is repeated. The first and the last read are kept as
    evidence, the polls in between are counted. DRY_RUN round 1 showed the search payload working (every user in the response) with the
    flag still unsolved on the immediate read."""
    ORACLE_WAIT_S = 5.0
    ORACLE_POLL_S = 0.25

    def quiet_solved(self):
        """One oracle read that leaves no evidence file (an intermediate poll); None when it cannot be read."""
        try:
            with common._OPENER.open(common.urllib.request.Request(f'{self.api()}/api/Challenges', headers={'Accept': 'application/json'}), timeout=common.HTTP_TIMEOUT_S) as r:
                for ch in json.loads(r.read().decode('utf-8')).get('data') or []:
                    if ch.get('key') == self.key:
                        return bool(ch.get('solved'))
        except Exception:  # noqa: BLE001 - an unreadable intermediate poll is not an observation; the last read decides
            return None
        return None

    def sequence(self):
        sr, mc = self.job.cfg['source_reading'], self.job.cfg['source_reading']['m1_controls']
        base = self.api()
        c = self.cond
        if c == 'SQLI-LOGIN':
            body = mc[c] if self.control else sr['payloads'][c]
            return [('POST', f'{base}/rest/user/login', body)]
        if c == 'SQLI-SEARCH':
            q = mc[c] if self.control else sr['payloads'][c]
            return [('GET', f'{base}/rest/products/search?q={urllib.parse.quote(q, safe="")}', None)]
        paths = [mc[c]] if self.control else sr['payloads'][c]
        return [('GET', f'{base}{p}', None) for p in paths]

    def method(self, run):
        with run.observe('method', f'M1 sequence for {self.cond}{" (control)" if self.control else ""}, then GET /api/Challenges') as rec:
            steps = []
            for i, (m, url, body) in enumerate(self.sequence(), 1):
                run.mark_stimulus_sent()
                r = run.http(m, url, body, label=f'sut05-m1-{i}')
                rec['evidence'].append(r.evidence)
                steps.append({'method': m, 'path': urllib.parse.urlsplit(url).path, 'status': r.status, 'error': r.error})
            t0, polls = time.monotonic(), 1
            r, solved = self.challenge(run, 'sut05-oracle-first-read')
            rec['evidence'].append(r.evidence)
            while r.status == 200 and solved is False and time.monotonic() - t0 < self.ORACLE_WAIT_S:
                time.sleep(self.ORACLE_POLL_S)
                polls += 1
                if self.quiet_solved():
                    break
            if polls > 1:
                r, solved = self.challenge(run, 'sut05-oracle-last-read')
                rec['evidence'].append(r.evidence)
            obs = {'steps': steps, 'oracle_status': r.status, 'oracle_key': self.key, 'solved': solved, 'oracle_error': r.error,
                   'oracle_polls': polls, 'oracle_waited_s': round(time.monotonic() - t0, 3)}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if any(s['status'] is None for s in obs['steps']):
            return 'INTERRUPTED_', f'no response to a request of the sequence: {[s for s in obs["steps"] if s["status"] is None]}'
        if obs['oracle_status'] != 200 or obs['solved'] is None:
            return 'M1_RESPONSE_OTHER', f'the oracle could not be read (HTTP {obs["oracle_status"]}, error {obs["oracle_error"]})'
        if obs['solved']:
            return 'M1_ORACLE_FLIPPED', f'{self.key} solved after {[(s["method"], s["path"], s["status"]) for s in obs["steps"]]}'
        return 'M1_ORACLE_NOT_FLIPPED', f'{self.key} not solved after {[(s["method"], s["path"], s["status"]) for s in obs["steps"]]}'


class M2(Sut05Cell):
    """M2 restricted ZAP run: one rule, one seeded target. A CONDITION cell expects the rule on the condition's endpoint; a CONTROL cell
    counts alerts of the same rule on the control endpoint (an alert there is a false positive)."""

    def targets(self):
        """Return (seed request, scan target, expected rule id, expected method, expected path)."""
        base, mr = self.api(), self.job.cfg['matching_rules']
        rule = str(self.job.c.get('expected_m2_rule_id') or M2_RULE[self.cond])
        if self.control:
            method, path, query = _split(self.job.c['control_endpoint'])
            body = CONTROL_BODY.get(self.job.c['control_endpoint'])
            url = f'{base}{path}' + (f'?{query}ctrl%40example.org' if query == 'email=' else (f'?{query}' if query else ''))
        else:
            method, path = mr['expected_m2_method'][self.cond], mr['expected_m2_path'][self.cond]
            body = SEED_BODY.get(self.cond)
            url = f'{base}{path}' + ('?q=apple' if self.cond == 'SQLI-SEARCH' else '')
        text = None if body is None else json.dumps(body)
        seed = {'method': method, 'url': url, 'body': text, 'content_type': 'application/json'}
        target = {'method': method, 'url': url, 'body': text}
        return seed, target, rule, method, path

    def method(self, run):
        seed, target, rule, method, path = self.targets()
        with run.observe('method', f'M2 restricted ZAP run: rule {rule} on {method} {path}', ['ZAP_RESTRICTED_SCAN']) as rec:
            try:
                obs = zap.run_scan(run, rec, self.LAUNCHER_FACTORY(), {'rule_id': rule, 'seed_request': seed, 'scan_target': target})
            except zap.ZapError as e:
                obs = {'zap_error': e.code, 'message': str(e)}
            obs.update({'expected_rule': rule, 'expected_method': method, 'expected_path': path})
            alerts = obs.pop('alerts', None)
            if alerts is not None:
                counted, others = zap.match_alerts(alerts, rule, method, path)
                obs['counted'], obs['others'] = counted, others
                rec['evidence'].append(run.jsonfile('zap-alerts', alerts))
            if obs.get('zap_version'):
                self.job.tools['security'] = {'tool': 'OWASP ZAP', 'version': obs['zap_version']}
                self.job.tools['security_image'] = {'tool': zap.ZAP_IMAGE_REPOSITORY, 'version': zap.ZAP_AMD64_MANIFEST}
            if obs.get('addons_unchanged') is False:
                run.notes.append('the installed ZAP add-ons differ before and after the run')
            # the add-on lists stay in the observation: they are what manifests/toolchain-manifest.yaml, tools.security, will record
            rec['observation'] = {k: (v if k != 'others' else f'{len(v)} alert(s) recorded, not counted') for k, v in obs.items()}
        return obs

    def classify(self, run, obs):
        if obs.get('zap_error'):
            return obs['zap_error'], obs.get('message')
        n = len(obs['counted'])
        where = f'rule {obs["expected_rule"]}, {obs["expected_method"]} {obs["expected_path"]}'
        if n:
            return 'M2_EXPECTED_ALERT', f'{n} alert(s) of {where}; {len(obs["others"])} other alert(s) not counted'
        return 'M2_NO_EXPECTED_ALERT', f'no alert of {where}; {len(obs["others"])} other alert(s) not counted'


REALIZATIONS = {}
for _cond in CONDITIONS:
    for _ctrl in ('', '-CTRL'):
        REALIZATIONS[f'E11-SUT05-{_cond}-M1{_ctrl}'] = M1
        REALIZATIONS[f'E11-SUT05-{_cond}-M2{_ctrl}'] = M2
