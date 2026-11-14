"""E05-determinism executor: the realization interface and the attempt loop.

DRAFT (operation OP-PREP-E05). One job runs the N executions of one condition sequentially on one shared instance (D-02, model B). One
execution is the block order of design brief s.2.1: reset, starting-state check, establishment, target-state verification, stimulus,
classification, record. A block that does not hold stops that execution with its pre-declared category and the job goes on with the
next execution (protocol/repeatability-determinism-v1.md, section 5, rules 4 to 6); only a failure of the job itself stops the job.
Every execution writes its bundle completely, run-manifest.json last, before the next one starts."""
import json
import os
import signal
import traceback

from . import classify, common, instance


class Realization:
    """One condition's realization. Subclasses set SPEC and implement the blocks; `carry` holds what an execution leaves for the next
    one (a token, an id): state that the reset or the starting-state check reads, never state that makes a block pass."""
    SPEC = None

    def __init__(self, job):
        self.job = job
        self.carry = {}

    def open(self):
        """Once per job, before the first execution (a web condition starts its browser here)."""

    def bind(self, run):
        """Start of an execution."""

    def reset(self, run):
        raise NotImplementedError

    def check_start(self, run):
        raise NotImplementedError

    def establish(self, run):
        raise NotImplementedError

    def verify_target(self, run):
        raise NotImplementedError

    def stimulus(self, run):
        """Send the one predeclared stimulus (calling run.mark_stimulus_sent() first) and return what was observed, as a dict."""
        raise NotImplementedError

    def classify(self, run, obs):
        """Return (label, observed text). The label is one of the condition's declared stimulus categories, projected mechanically."""
        raise NotImplementedError

    def end(self, run):
        """End of an execution, whatever its outcome (a web condition writes its network and console logs here)."""

    def close(self):
        """End of the job."""

    def components(self, run):
        return instance.components(run, list(self.SPEC.components))


def _arm(seconds):
    """Per-execution budget: armed only when run.py installed the handler (a test or a bare import has none, and the default action would kill the process)."""
    if callable(signal.getsignal(signal.SIGALRM)):
        signal.alarm(seconds)


def failure_outcome(job, f):
    label = classify.label_for_failure(f.phase, f.interrupted)
    return common.Outcome(label, None, cause=f.cause, attribution=classify.attribution(f.tooling, False))


def _write_bundle(job, real, run, outcome):
    manifest_outcome = classify.manifest_outcome(job.cfg, job.c, outcome.label, outcome.observed or outcome.cause)
    run.write_records(outcome, job.c)
    run.copy_provenance()
    run.log('run-end', category=outcome.label, attribution=outcome.attribution)
    run.close()  # executor.log is complete before the manifest hashes it
    manifest = common.build_manifest(run, manifest_outcome, real.SPEC, real.components(run), [f'attribution={outcome.attribution}'])
    common.write_manifest(run, manifest)


def _stub(job, real, index, reason):
    """D-09: an execution that began and left no bundle gets a stub record in T (STUB_NO_BUNDLE), counted against TSRR and E2E-ROR and never
    against CEOR. Written only when the ordinary bundle could not be written; if the stub fails too, the job reports it and exits non-zero."""
    run = common.Run(job, index)
    try:
        outcome = common.Outcome('STUB_NO_BUNDLE', None, cause=reason, attribution='SUT')
        _write_bundle(job, real, run, outcome)
    finally:
        run.close()
    return outcome


def execute(job, real, index):
    """One execution of the condition: returns the Outcome. The manifest of the execution exists whenever this function returns."""
    run = common.Run(job, index)
    outcome = None
    try:
        instance.write_evidence(run)
        real.bind(run)
        _arm(common.WATCHDOG_S)
        try:
            real.reset(run)
            real.check_start(run)
            real.establish(run)
            real.verify_target(run)
            obs = real.stimulus(run)
            with run.observe('classification', 'classify the stimulus observation') as rec:
                label, observed = real.classify(run, obs)
                rec['observation'] = {'category': label}
            label, note = classify.finalize_label(job.cfg, job.c, label)
            outcome = common.Outcome(label, observed, notes=[note] if note else [])
        except common.PhaseFailure as f:
            outcome = failure_outcome(job, f)
        except Exception as e:  # noqa: BLE001 - the watchdog or a harness fault between two blocks: an interruption of the phase running
            run.log('error', traceback=traceback.format_exc())
            phase = run.phase or 'reset'
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
