"""E08-performance executor: the realization interface and the attempt loop.

DRAFT (operation OP-PREP-E08), derived from the E11 attempt loop. One job runs the N executions of one condition sequentially on one shared
instance. One execution is the block order starting-state check, method (three page loads in the rotating order of conditions-draft.json,
each in a fresh browser context), classification, record. A block that does not hold stops that execution with its pre-declared category
and the job goes on with the next execution; only a failure of the job itself stops the job. Every execution writes its bundle completely,
run-manifest.json last, before the next one starts."""
import json
import os
import signal
import traceback

from . import classify, common, config, instance, web


class Realization:
    """One condition's realization. Subclasses set SPEC and implement check_start and load; `carry` holds what one execution keeps for its
    own later blocks (the tokens of the activation check), never state that makes a block pass; it is emptied at the start of the execution."""
    SPEC = None

    def __init__(self, job):
        self.job = job
        self.carry = {}
        self.b = None

    def open(self):
        """Once per job, before the first execution: the browser starts here."""
        self.b = web.Browser(self.job)

    def bind(self, run):
        """Start of an execution."""
        self.carry = {}
        self.b.ensure(run)

    def check_start(self, run):
        raise NotImplementedError

    def load(self, run, role):
        """One page load (role D, Ba or Bb) in a fresh browser context: the activation of the account, the call run.mark_stimulus_sent() before
        the first measured navigation, the observation window, and the raw snapshot. Returns a dict with at least 'role', 'account', 'page',
        'status' and 'snapshot'."""
        raise NotImplementedError

    def method(self, run, order):
        loads = {}
        for role in order:
            loads[role] = self.load(run, role)
        return {'order': list(order), 'loads': loads}

    # ---- helpers shared by the realizations -----------------------------------------------------------------------------------------
    def next_label(self, role):
        self.carry['n_loads'] = self.carry.get('n_loads', 0) + 1
        return f'load{self.carry["n_loads"]}-{role}'

    def side(self, role):
        return self.job.c['degraded'] if role == 'D' else self.job.c['baseline']

    @staticmethod
    def begin_measurement(run):
        """The boundary of attribution (D-16): an exception before the first measured navigation of the execution is TOOLING."""
        if not run.stimulus_sent:
            run.mark_stimulus_sent()

    @staticmethod
    def wait_ready(session, keys, timeout_ms):
        """Wait until every watch key has a value in the page (a time or null) or the budget ends; a missing signal is an observation, not an exception."""
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        try:
            session.page.wait_for_function('(keys) => !!window.__e08 && keys.every((k) => window.__e08.ready[k] !== undefined)', arg=list(keys), timeout=timeout_ms)
            return True
        except PlaywrightTimeout:
            return False

    def finish_load(self, run, s, role, label, account, page, status, extra=None):
        """End of a load: the raw snapshot, a screenshot of the degraded load, the logs; returns the load record (the snapshot is kept in it)."""
        snap = s.snapshot()
        if snap is None:
            raise RuntimeError(f'{label}: the measurement script is not present in the document')
        snap['final_url'] = s.page.url
        snap_ev = run.jsonfile(f'{label}-probe', snap)
        shot = run.capture({'evidence': [], 'observation': {}}, s.shot, f'{label}-screenshot') if role == 'D' else None
        s.flush_logs()
        return {'role': role, 'label': label, 'account': account, 'page': page, 'navigation_status': status, 'final_url': snap['final_url'],
                'snapshot': snap, 'probe_evidence': snap_ev, 'screenshot': shot, **(extra or {})}

    def end(self, run):
        """End of an execution, whatever its outcome."""

    def close(self):
        """End of the job."""
        if self.b is not None:
            self.b.close()

    def components(self, run):
        return instance.components(run, list(self.SPEC.components))


def observed_text(c, detail, order):
    v = detail['values']

    def fmt(x):
        return 'none' if x is None else f'{x}'
    return (f'{c["metric"]} ({c["unit"]}): D={fmt(v["D"])}, Ba={fmt(v["Ba"])}, Bb={fmt(v["Bb"])}; delta D-Ba={fmt(detail["delta_D_minus_Ba"])}; '
            f'rule {c["rule"]["comparison"]} {c["rule"]["threshold"]}; detected={detail["detected"]}; '
            f'baseline_false_positive={detail["baseline_false_positive"]}; order={">".join(order)}'
            + (f'; absent={detail["absent_reasons"]}' if detail['absent_reasons'] else ''))


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


def _summarize_load(load):
    return {k: v for k, v in load.items() if k != 'snapshot'}


def execute(job, real, index):
    """One execution of the condition: returns the Outcome. The manifest of the execution exists whenever this function returns."""
    run = common.Run(job, index)
    outcome = None
    try:
        instance.write_evidence(run)
        order = config.order_for(job.cfg, index)
        real.bind(run)
        _arm(common.WATCHDOG_S)
        try:
            real.check_start(run)
            with run.observe('method', f'three page loads in the order {">".join(order)}') as rec:
                obs = real.method(run, order)
                rec['observation'] = {'order': obs['order'], 'loads': {r: _summarize_load(l) for r, l in obs['loads'].items()}}
            with run.observe('classification', 'classify the three snapshots by the rule of the condition') as rec:
                label, detail = classify.evaluate(job.c, {r: l['snapshot'] for r, l in obs['loads'].items()})
                detail['order'] = list(order)
                run.jsonfile('detection', detail)
                rec['observation'] = {'category': label}
            label, note = classify.finalize_label(job.cfg, job.c, label)
            outcome = common.Outcome(label, observed_text(job.c, detail, order), notes=[note] if note else [],
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
