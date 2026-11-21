"""E06-cross-platform-parity executor: one condition, N executions, one bundle per execution (entry point: python3 -m executor.run).

DRAFT (operation OP-PREP-E06-EXECUTOR). Not frozen, not locked, not dispatched. The loop follows the E07 model (one invocation runs the
executions of one condition in sequence and writes every bundle completely before the next one starts). No execution is retried: an
execution that did not arrive keeps its reason, and the next execution starts from a clean state (a fresh browser context on the web;
an uninstall and a new session on Android). A refusal of the configuration writes no record and exits non-zero.
"""
import json
import os
import sys
import traceback

from . import android, classify, common, config, identity, web

COMPONENTS = {
    'SUT-01-web': {'component_id': 'SUT-01-web', 'repository': 'https://github.com/gsanchezm/OmniPizza', 'commit_sha': '9ca37674d374e9303912e259641ee86baf3aabe1',
                   'endpoint': 'https://omnipizza-frontend.onrender.com', 'provenance_status': 'PINNED_SOURCE; HOSTED_MAPPING_UNVERIFIED'},
    'SUT-01-android': {'component_id': 'SUT-01-android', 'repository': 'https://github.com/gsanchezm/OmniPizza', 'commit_sha': '3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a',
                       'release': 'v1.1.8', 'backend_origin': 'https://omnipizza-backend.onrender.com', 'provenance_status': 'PINNED_RELEASE; HOSTED_MAPPING_UNVERIFIED'},
    'SUT-02-web': {'component_id': 'SUT-02-web', 'repository': 'https://github.com/saucelabs/sample-app-web', 'commit_sha': '60fdd634bb111c092282fa07977513a0a7765593',
                   'endpoint': 'https://www.saucedemo.com/', 'provenance_status': 'PINNED_SOURCE; HOSTED_MAPPING_UNVERIFIED'},
    'SUT-02-android': {'component_id': 'SUT-02-android', 'repository': 'https://github.com/saucelabs/my-demo-app-android', 'commit_sha': '36b012eecdf6a2b488b9504e16b3d0c3ca9a0e7b',
                       'release': '2.2.0', 'provenance_status': 'PINNED_RELEASE'},
}
EXPECTED_OUTCOME = ('the actor reaches the authenticated catalogue of the ecosystem and the identity of the first catalogue position is read '
                    '(identity_oracle item_identity; arrival only when the switch says arrival_only)')
WEB_BUDGET_MS = 180000
ANDROID_BUDGET_MS = 180000


class ConfigurationRefused(Exception):
    """The executor refuses the configuration before any execution: no record is written."""


def _component_key(c):
    return {'WEB': f"{c['sut_id']}-web", 'ANDROID': f"{c['sut_id']}-android"}[c['surface']]


def components_of(c):
    """The schema shape of the component the condition touches (schemas/run-manifest.schema.v2.json, sut_provenance.components)."""
    d = COMPONENTS[_component_key(c)]
    return [{'component': d['component_id'], 'repository': d.get('repository'), 'commit_sha_or_release': d.get('commit_sha') or d.get('release'),
             'endpoint': d.get('endpoint') or d.get('backend_origin')}]


def component_provenance_note(c):
    return 'component provenance: ' + str(COMPONENTS[_component_key(c)].get('provenance_status'))


class WebExecutor:
    """The web condition: one Chromium for the job, one browser context per execution."""

    def __init__(self, env, cfg, c, scrub):
        self.env, self.c, self.scrub = env, c, scrub
        self.tools = {}
        self.browser = web.Browser(self.tools)

    def run_one(self, run):
        username, password = config.credentials(self.c)
        page = self.browser.new_page()
        try:
            if self.c['sut_id'] == 'SUT-01':
                facts = web.sut01_web(page, self.browser.tracker.events, (username, password), web.VIEWPORT['width'])
            else:
                facts = web.sut02_web(page, self.browser.tracker.events, (username, password))
        finally:
            self.browser.close_context()
        return observation(run, facts, self.c, self.env, screenshot=facts.get('screenshot_png'), dom=facts.get('dom_html'),
                           extra={'network-log': facts.get('network_events')})

    def toolchain(self):
        return {'web_runner': self.tools.get('web_runner'), 'browser': self.tools.get('browser'), 'executor_runtime': common.python_runtime()}

    def close(self):
        self.browser.close()


class AndroidExecutor:
    """The Android condition: a clean install and a new Appium session per execution, through the Node harness."""

    def __init__(self, env, cfg, c, scrub):
        self.env, self.c, self.scrub = env, c, scrub
        self.record_versions = {}
        self.apk_sha256 = android.verify_apk(env.apk_path, c['apk']['sha256'])

    def run_one(self, run):
        username, password = config.credentials(self.c)
        scrub = self.scrub
        scrub.secret(password)
        removal = android.uninstall(self.env, self.c['app_package'])
        run.log('uninstall', **removal)
        record = android.run_harness(self.env, scrub, self.c, run.index, username=username, password=password,
                                     app_package=self.c['app_package'], launch=self.c.get('launch') if isinstance(self.c.get('launch'), dict) else {},
                                     budget_ms=ANDROID_BUDGET_MS)
        for k, v in (record.get('observed_versions') or {}).items():
            self.record_versions.setdefault(k, v)
        facts = {'surface': 'android', 'sut_id': self.c['sut_id'], 'sign_in_submitted': record.get('sign_in_submitted'),
                 'page_loaded': record.get('app_started'), 'backend_observed': False, 'error_text': record.get('error_text'),
                 'login_request_seen': False, 'catalogue_seen': False, 'login_status': None, 'catalogue_status': None,
                 'arrived': bool(record.get('arrived')), 'steps': record.get('steps') or [], 'harness_fault': record.get('fault'),
                 'uninstall': removal}
        source = record.get('page_source')
        facts['page_source_kept'] = bool(source)
        identity_value = None
        if facts['arrived'] and self.c['identity_oracle'] == 'item_identity':
            identity_value, read_note = read_identity_from_source(self.c['sut_id'], source, record)
            facts['identity_read_note'] = read_note
            facts['identity_raw'] = identity_value
        facts['identity'] = identity_value
        screenshot = android.screenshot_bytes(record)
        shell = {k: v for k, v in record.items() if k not in ('page_source', 'screenshot_png_base64')}
        return observation(run, facts, self.c, self.env, screenshot=screenshot, dom=source, extra={'harness-record': shell},
                           dom_name='page-source', dom_ext='xml')

    def toolchain(self):
        v = self.record_versions
        return {'appium_core': {'tool': 'Appium', 'version': v.get('appium') or '3.7.0 (pin; observed value not returned by the harness)'},
                'android_driver': {'tool': 'appium-uiautomator2-driver', 'version': v.get('uiautomator2') or '8.7.0 (pin)'},
                'node': {'tool': 'Node.js', 'version': v.get('node')},
                'android_emulator': {'tool': 'Android emulator via ReactiveCircus/android-emulator-runner at a421e43855164a8197daf9d8d40fe71c6996bb0d', 'version': 'API 35 google_apis x86_64 pixel_7'},
                'executor_runtime': common.python_runtime()}

    def close(self):
        pass


def read_identity_from_source(sut_id, source, record):
    """The identity of the first catalogue position, parsed again from the kept page source; a disagreement with the harness reading is noted."""
    try:
        if sut_id == 'SUT-01':
            cards = identity.parse_android_card_source(source)
            value = identity.first_identity('SUT-01', cards)
            harness = [identity.pizza_id_from_card_label(x) for x in record.get('card_labels') or []]
            harness = [h for h in harness if h]
            note = 'parsed from the page source' + ('' if harness[:1] == [value] else '; the harness reading differs from the page source parse')
            return value, note
        titles = identity.parse_android_titles_source(source)
        value = identity.first_identity('SUT-02', titles)
        note = 'parsed from the page source' + ('' if (record.get('titles') or [None])[0] == value else '; the harness reading differs from the page source parse')
        return value, note
    except ValueError as e:
        return None, f'identity unreadable: {e}'


def observation(run, facts, c, env, *, screenshot, dom, extra, dom_name='dom-snapshot', dom_ext='html'):
    """Writes the evidence of one execution and returns what classify needs (arrival, identity, reason, facts)."""
    run.log('observation', arrived=facts.get('arrived'), identity=facts.get('identity'), sign_in_state=facts.get('sign_in_state'))
    if dom:
        run.text(dom_name, dom, dom_ext)
    if screenshot:
        run.binary('screenshot', screenshot, 'png')
    for name, obj in extra.items():
        if obj is not None:
            run.jsonfile(name, obj)
    keep = {k: v for k, v in facts.items() if k not in ('screenshot_png', 'dom_html', 'network_events')}
    run.jsonfile('facts', keep)
    return {'facts': facts, 'arrived': bool(facts.get('arrived')), 'identity': facts.get('identity') if env.expected_identity_oracle == 'item_identity' else None,
            'identity_raw': facts.get('identity_raw') if env.expected_identity_oracle == 'item_identity' else None}


def execute_one(env, scrub, cfg, c, index, driver):
    """One execution: run it, classify it, write its run-manifest.json last. Returns the per-execution summary record."""
    run = common.Run(env, scrub, index)
    fault = None
    observed = None
    try:
        observed = driver.run_one(run)
    except Exception as e:  # noqa: BLE001 - every fault of the executor, browser, client, or session is a RUNNER fault
        fault = f'{e.__class__.__name__}: {e}'
        run.log('runner-fault', traceback=traceback.format_exc()[-2000:])
    arrived = bool(observed and observed['arrived'])
    identity_value = observed['identity'] if observed else None
    harness_fault = observed['facts'].get('harness_fault') if observed and not arrived else None
    if fault is None and harness_fault:
        # a fault of the Appium session or of the harness that did not let the execution arrive is a RUNNER fault (vocabulary of config.py)
        fault = f"harness fault: {harness_fault.get('class')}: {harness_fault.get('message')}"
    reason = None
    if not arrived and fault is None:
        reason = classify.not_arrived_reason(observed['facts'])
    record = classify.classify(identity_oracle=env.expected_identity_oracle, arrived=arrived, identity=identity_value, reason=reason,
                               runner_fault=fault)
    run.log('run-end', category=record['category'], reason=record['reason'], attribution=record['attribution'])
    run.close()
    notes = [f"category={record['category']}", f"attribution={record['attribution']}", component_provenance_note(c)]
    if record['reason']:
        notes.append(f"reason={record['reason']}")
    if fault:
        notes.append('runner_fault=' + fault)
    if env.expected_identity_oracle == 'arrival_only':
        notes.append('identity oracle arrival_only: the identity is not read by design (DP-3 fallback recorded before the START)')
    outcome = classify.manifest_outcome(EXPECTED_OUTCOME, record)
    environment_type = c['environment_type']
    manifest = common.build_manifest(run, condition=c, outcome=outcome, environment_type=environment_type,
                                     platform_name=c['platform'], components=components_of(c),
                                     toolchain=driver.toolchain(), related_evidence=c.get('evidence_ids') or [], notes=notes,
                                     reset_mechanisms=['SESSION_RESET'], establishment_mechanisms=['UI_FLOW'])
    common.write_manifest(run, manifest)
    return {'run_id': run.run_id, 'execution_index': index, 'category': record['category'], 'reason': record['reason'],
            'attribution': record['attribution'], 'arrived': record['arrived'], 'identity': record['identity_read'],
            'identity_raw': observed.get('identity_raw') if observed else None}


def summarize(env, cfg, c, planned, results):
    counts, reasons, attributions = {}, {}, {}
    for r in results:
        counts[r['category']] = counts.get(r['category'], 0) + 1
        if r['reason']:
            reasons[r['reason']] = reasons.get(r['reason'], 0) + 1
        key = f"{r['category']}|{r['attribution']}"
        attributions[key] = attributions.get(key, 0) + 1
    return {'record': 'condition summary (counts only; no interpretation; parity is not computed here)', 'condition': c['condition_id'],
            'sut_id': c['sut_id'], 'surface': c['surface'], 'record_class': env.record_class, 'attempt': env.attempt,
            'canonical_scenario_id': c['canonical_scenario_id'], 'identity_oracle': env.expected_identity_oracle,
            'executions_planned': planned, 'executions_run': len(results), 'categories': counts, 'reasons': reasons,
            'category_by_attribution': attributions, 'executions': results}


def execute_condition(env, scrub, cfg, c, driver, planned):
    """Runs the executions 1 to planned of one condition with the given driver; writes the condition summary last."""
    results = []
    try:
        for index in range(1, planned + 1):
            result = execute_one(env, scrub, cfg, c, index, driver)
            results.append(result)
            print(f"{result['run_id']}: {result['category']}" + (f" ({result['reason']})" if result['reason'] else ''), flush=True)
    finally:
        driver.close()
        summary = summarize(env, cfg, c, planned, results)
        with open(os.path.join(env.output_dir, 'condition-summary.json'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(scrub(json.dumps(summary, indent=2, ensure_ascii=False)))
    return summary


def prepare(environ=None):
    """Checks the configuration and returns (env, cfg, condition, planned). Raises ConfigurationRefused or config.ConfigError."""
    env = common.Env(environ)
    cfg = config.load(env.conditions_file)
    if env.attempt != config.ATTEMPT:
        raise ConfigurationRefused('only attempt 1 is executed (protocol/repeatability-determinism-v1.md; D-E06-6)')
    if env.record_class not in config.RECORD_CLASSES:
        raise ConfigurationRefused(f'record class {env.record_class!r} is not allowed')
    if env.record_class == 'MEASURED_EXPERIMENT' and not env.prompt_version:
        # repository rule 9 (prompts/README.md rule 5): a null prompt version only for a human-executed run, never for a measured execution
        raise ConfigurationRefused('a measured execution needs the frozen prompt version (EXECUTOR_PROMPT_VERSION)')
    c = config.condition(cfg, env.condition)
    if env.expected_identity_oracle != c['identity_oracle']:
        raise ConfigurationRefused(f'the identity oracle of {c["condition_id"]} is {c["identity_oracle"]!r}, the configuration names {env.expected_identity_oracle!r}')
    if env.expected_identity_oracle not in config.IDENTITY_ORACLE_VALUES:
        raise ConfigurationRefused('EXPECTED_IDENTITY_ORACLE is not an allowed value')
    if os.path.exists(os.path.join(env.output_dir, 'condition-summary.json')):
        raise ConfigurationRefused('the output directory already holds a condition summary; attempts are immutable')
    os.makedirs(env.output_dir, exist_ok=True)
    planned = config.planned_executions(env.record_class, cfg)
    return env, cfg, c, planned


def make_driver(env, cfg, c, scrub):
    _username, password = config.credentials(c)
    scrub.secret(password)
    if c['surface'] == 'WEB':
        return WebExecutor(env, cfg, c, scrub)
    return AndroidExecutor(env, cfg, c, scrub)


def main(environ=None):
    try:
        env, cfg, c, planned = prepare(environ)
    except (ConfigurationRefused, config.ConfigError, KeyError, ValueError) as e:
        print(f'e06 executor refused: {e}', file=sys.stderr)
        return 2
    scrub = common.Scrubber(env)
    try:
        driver = make_driver(env, cfg, c, scrub)
    except android.ApkError as e:
        print(f'e06 executor refused: {e}', file=sys.stderr)
        return 2
    execute_condition(env, scrub, cfg, c, driver, planned)
    return 0


if __name__ == '__main__':
    sys.exit(main())
