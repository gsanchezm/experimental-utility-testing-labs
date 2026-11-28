"""E10-visual executor: the realization interface and the attempt loop.

DRAFT (operation OP-PREP-E10), derived from the E08 attempt loop. One job runs the N executions of one condition sequentially on one shared
instance. One execution is the block order starting-state check, method (for each view of the condition the captures A, B and A2 in that
fixed order, each in a fresh browser context with its own activation of the account, then the two comparisons A against B and A against A2),
classification, record. A block that does not hold stops that execution with its pre-declared category and the job goes on with the next
execution; only a failure of the job itself stops the job. Every execution writes its bundle completely, run-manifest.json last, before the
next one starts."""
import json
import os
import signal
import traceback

from . import capture, classify, common, compare, config, instance, web


class Realization:
    """One condition's realization. Subclasses set SPEC and implement check_start and activate (and navigate when the default is not enough);
    `carry` holds what one execution keeps for its own later blocks (the tokens of the activation check), never state that makes a block
    pass; it is emptied at the start of the execution."""
    SPEC = None

    def __init__(self, job):
        self.job = job
        self.carry = {}
        self.b = None

    @property
    def site(self):
        return instance.base(self.job.instance, 'web')

    def open(self):
        """Once per job, before the first execution: the browser starts here."""
        self.b = web.Browser(self.job)

    def bind(self, run):
        """Start of an execution."""
        self.carry = {}
        self.b.ensure(run)
        comparator = getattr(self.job, 'comparator', None)
        if comparator is not None:
            comparator.clear()

    def check_start(self, run):
        raise NotImplementedError

    def activate(self, run, s, account, label):
        """The activation of the account in the capture's fresh context (a login), before the measured navigation. Returns the activation
        record; raises PhaseFailure with label START_ACTIVATION_NOT_CONFIRMED when the activation is not confirmed."""
        raise NotImplementedError

    def navigate(self, run, s, view):
        """The measured navigation of the capture: a full document load of the view's route. Returns the HTTP status."""
        return s.goto(self.site + view['route'], wait_until='commit')

    def state(self, role):
        return self.job.c['state_a'] if role in ('A', 'A2') else self.job.c['state_b']

    @staticmethod
    def begin_measurement(run):
        """The boundary of attribution (D-16): an exception before the first measured navigation of the execution is TOOLING."""
        if not run.stimulus_sent:
            run.mark_stimulus_sent()

    def capture_view(self, run, view, role):
        """One capture of one view in a fresh context. Returns the capture record (the PNG bytes in record['png'])."""
        label = f'{view["view_id"]}-{role}'
        account = self.state(role)['account']
        s = self.b.session(run, label)
        try:
            activation = self.activate(run, s, account, label)
            run.jsonfile(f'{label}-activation', activation)
            self.begin_measurement(run)
            status = self.navigate(run, s, view)
            steps = capture.run_steps(s.page, view.get('steps'))
            rec = capture.capture_page(s.page, view, role, self.job.cfg)
            rec.update({'label': label, 'account': account, 'route': view['route'], 'navigation_status': status, 'final_url': s.page.url, 'steps_done': steps})
            rec['evidence'] = {'png': run.binary(f'{label}-capture', rec['png'], 'png'), 'json': None}
            rec['evidence']['json'] = run.jsonfile(f'{label}-capture', capture.record_for_json(rec))
            s.flush_logs()
            return rec
        finally:
            s.close()

    def compare_pair(self, run, view, cap_a, cap_other, pair):
        """The comparison of A against B (pair 'AB') or against A2 (pair 'AA2'); None when a capture is not usable (no content, a timed capture
        taken too late): the classification then reports it."""
        for cap in (cap_a, cap_other):
            if not cap['ready_ok'] or cap.get('timed_ok') is False:
                return None
        result = self.job.comparator.compare(cap_a['png'], cap_other['png'])
        if not result['dimension_mismatch']:
            result['evidence_diff'] = run.binary(f'{view["view_id"]}-{pair}-diff', result['diff_png'], 'png')
        return result

    def method(self, run):
        views = []
        for view in self.job.c['views']:
            caps = {role: self.capture_view(run, view, role) for role in self.job.cfg['capture_order']}
            views.append({'view': view, 'captures': caps, 'AB': self.compare_pair(run, view, caps['A'], caps['B'], 'AB'),
                          'AA2': self.compare_pair(run, view, caps['A'], caps['A2'], 'AA2')})
        return views

    def end(self, run):
        """End of an execution, whatever its outcome."""

    def close(self):
        """End of the job."""
        if self.b is not None:
            self.b.close()

    def components(self, run):
        return instance.components(run, list(self.SPEC.components))


def _capture_summary(rec):
    return {k: v for k, v in rec.items() if k not in ('png', 'elements', 'settle', 'steps_done')}


def _comparison_summary(cmp_):
    if cmp_ is None:
        return None
    return {k: v for k, v in cmp_.items() if k not in ('mask', 'diff_png')}


def _arm(seconds):
    """Per-execution budget: armed only when run.py installed the handler (a test or a bare import has none, and the default action would kill the process)."""
    if callable(signal.getsignal(signal.SIGALRM)):
        signal.alarm(seconds)


def failure_outcome(job, f):
    label = classify.label_for_failure(f)
    return common.Outcome(label, None, cause=f.cause, attribution=classify.attribution(f.tooling, label))


def _write_bundle(job, real, run, outcome):
    manifest_outcome = classify.manifest_outcome(job.cfg, job.c, outcome.label, outcome.observed or outcome.cause)
    run.write_records(outcome, job.c)
    run.copy_provenance()
    run.log('run-end', category=outcome.label, attribution=outcome.attribution)
    run.close()  # executor.log is complete before the manifest hashes it
    manifest = common.build_manifest(run, manifest_outcome, real.SPEC, real.components(run), [f'attribution={outcome.attribution}'],
                                     behavior_class=job.c['behavior_class'])
    common.write_manifest(run, manifest)


def _stub(job, real, index, reason):
    """An execution that began and left no bundle gets a stub record (STUB_NO_BUNDLE), kept in the condition's counts. Written only when the
    ordinary bundle could not be written; if the stub fails too, the job reports it and exits non-zero."""
    run = common.Run(job, index)
    try:
        outcome = common.Outcome('STUB_NO_BUNDLE', None, cause=reason, attribution='SUT')
        _write_bundle(job, real, run, outcome)
    finally:
        run.close()
    return outcome


def _instrument_record(job, thr):
    comparator = getattr(job, 'comparator', None)
    pin = {k: v for k, v in (comparator.pin if comparator else {}).items() if k != 'module_path'}
    return {'capture_version': capture.CAPTURE_VERSION, 'viewport': capture.VIEWPORT, 'comparison_tool': 'pixelmatch', 'pixelmatch_version': compare.PIXELMATCH_VERSION,
            'pixelmatch_pin_used': pin, 'pixelmatch_options': compare.PIXELMATCH_OPTIONS,
            'node_version': comparator.node_version if comparator else None, 'runner_sha256': comparator.runner_sha256 if comparator else None,
            'thresholds': thr}


def execute(job, real, index):
    """One execution of the condition: returns the Outcome. The manifest of the execution exists whenever this function returns."""
    run = common.Run(job, index)
    outcome = None
    try:
        instance.write_evidence(run)
        thr = config.thresholds(job.cfg, job.c)
        run.jsonfile('instrument', _instrument_record(job, thr))
        real.bind(run)
        _arm(common.WATCHDOG_S)
        try:
            real.check_start(run)
            with run.observe('method', 'captures A, B and A2 of every view, and the comparisons A against B and A against A2') as rec:
                views = real.method(run)
                rec['observation'] = {'views': [{'view_id': v['view']['view_id'], 'captures': {r: _capture_summary(c) for r, c in v['captures'].items()},
                                                 'AB': _comparison_summary(v['AB']), 'AA2': _comparison_summary(v['AA2'])} for v in views]}
            with run.observe('classification', 'classify the comparisons by the rule of the condition') as rec:
                label, detail = classify.evaluate(job.c, job.cfg, thr, views)
                observed = classify.observed_text(detail)  # before the per-comparison records leave the detail
                for v in detail['views']:
                    for pair in ('AB', 'AA2'):
                        if v.get(pair) is not None:
                            run.jsonfile(f'{v["view_id"]}-{pair}-comparison', v.pop(pair))
                        else:
                            v.pop(pair, None)
                run.jsonfile('detection', detail)
                rec['observation'] = {'category': label}
            label, note = classify.finalize_label(job.cfg, job.c, label)
            outcome = common.Outcome(label, observed, notes=[note] if note else [],
                                     attribution=classify.attribution(False, label))
        except common.PhaseFailure as f:
            outcome = failure_outcome(job, f)
        except Exception as e:  # noqa: BLE001 - the watchdog or a harness fault between two blocks: an interruption of the phase running
            run.log('error', traceback=traceback.format_exc())
            phase = run.phase or 'starting-state'
            outcome = failure_outcome(job, common.PhaseFailure(phase, f'interrupted between blocks in {phase}: {e.__class__.__name__}: {e}',
                                                               interrupted=True, tooling=not run.stimulus_sent))
        finally:
            _arm(0)
        try:
            real.end(run)
        except Exception as e:  # noqa: BLE001 - evidence only
            run.notes.append(f'end of execution: {e.__class__.__name__}: {e}')
        _write_bundle(job, real, run, outcome)
        return outcome
    except Exception as e:  # noqa: BLE001 - the bundle itself could not be written
        run.close()
        reason = f'the bundle of {run.run_id} could not be completed: {e.__class__.__name__}: {e}'
        print(reason, flush=True)
        return _stub(job, real, index, reason)


def summarize(job, results):
    counts, phases, attributions = {}, {}, {}
    for r in results:
        counts[r['category']] = counts.get(r['category'], 0) + 1
        phases[r['phase']] = phases.get(r['phase'], 0) + 1
        key = f'{r["category"]}|{r["attribution"]}'
        attributions[key] = attributions.get(key, 0) + 1
    return {'record': 'condition summary (counts only; no interpretation)', 'condition': job.env.condition, 'sut': job.env.sut,
            'record_class': job.env.record_class, 'attempt': job.env.attempt, 'executions_planned': job.planned,
            'executions_run': len(results), 'categories': counts, 'phases': phases, 'category_by_attribution': attributions,
            'executions': results, 'notes': job.notes}


def run_job(job, real):
    """Run the executions first..last of the condition. Returns the list of per-execution results."""
    results = []
    real.open()
    try:
        for index in range(job.first, job.last + 1):
            outcome = execute(job, real, index)
            results.append({'run_id': job.env.run_id(index), 'category': outcome.label, 'phase': classify.phase(outcome.label),
                            'attribution': outcome.attribution})
            print(f'{job.env.run_id(index)}: {outcome.label} ({outcome.attribution})', flush=True)
    finally:
        real.close()
        instance.collect_logs(job, os.path.join(job.env.output_dir, 'sut-logs'))
        summary = summarize(job, results)
        with open(os.path.join(job.env.output_dir, 'condition-summary.json'), 'w', encoding='utf-8') as f:
            f.write(job.scrub(json.dumps(summary, indent=2, ensure_ascii=False)))
    return results
