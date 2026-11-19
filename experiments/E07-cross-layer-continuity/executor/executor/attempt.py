"""E07-cross-layer-continuity executor: the realization interface and the attempt loop.

DRAFT (operation OP-PREP-E07-04). One job runs the N executions of one condition sequentially on one shared instance (the E05 model B,
decision D-02, carried over; decision D-E07-8). One execution is the block order reset, starting-state check, establishment (source layer),
establishment check (source layer, read-only), verification (the other layer, read-only), record. A block that does not hold stops that execution
with its pre-declared category and the job goes on with the next execution (protocol/repeatability-determinism-v1.md, section 5, rules 4 to 6);
only a failure of the job itself stops the job. Every execution writes its bundle completely, run-manifest.json last, before the next one starts."""
import json
import os
import signal
import traceback

from . import classify, common, config, instance


class Realization:
    """One condition's realization. Subclasses set SPEC and implement the blocks; `carry` holds what an execution leaves for the next
    one (a token, an id): state that the reset or the starting-state check reads, never state that makes a block pass."""
    SPEC = None
    DECLARED_KEYS = ()  # the identity_keys text of the conditions file that this realization implements (checked before the run)
    KEYS = ()           # the identity keys compared on the verification layer, in order
    NOT_COMPARED = {}   # a declared key that the verification layer does not show, with the reason (D-E07-9: it is not used)

    def __init__(self, job):
        self.job = job
        self.carry = {}

    def start_identity(self, run):
        """Start of an execution: the identity record of the attempt, filled by the establishment check and by the verification."""
        run.identity = {'declared_keys': list(self.job.c['identity_keys']), 'compared_keys': list(self.KEYS), 'not_compared': dict(self.NOT_COMPARED),
                        'established': {}, 'observed': {}, 'comparison': []}

    def conclude(self, run, rec, observed, **observation):
        """The verification's last act: compare every declared key with what the verification layer showed. A key that is absent or different
        puts the step in FAILURE (NOT_VERIFIED); `observation` is what the step records beside the comparison."""
        comparison = common.compare(run.identity['established'], observed, self.KEYS)
        run.identity['observed'], run.identity['comparison'] = observed, comparison
        differs = common.mismatch_text(comparison)
        rec['observation'] = {'differs': differs or None, **{k: v for k, v in (rec.get('observation') or {}).items() if k != 'differs'}, **observation}
        if differs:
            rec['outcome'] = 'FAILURE'

    def open(self):
        """Once per job, before the first execution (a realization starts its browser here)."""

    def bind(self, run):
        """Start of an execution (a realization gives the execution a new browser context here)."""

    def reset(self, run):
        raise NotImplementedError

    def check_start(self, run):
        raise NotImplementedError

    def establish(self, run):
        """Establishment on the source layer."""
        raise NotImplementedError

    def establish_check(self, run):
        """Read-only check on the source layer that the unit is established; records what was established in run.identity."""
        raise NotImplementedError

    def verify(self, run):
        """Read-only observation of the unit on the verification layer and the comparison of every declared identity key."""
        raise NotImplementedError

    def end(self, run):
        """End of an execution, whatever its outcome (a realization writes its network and console logs here)."""

    def close(self):
        """End of the job."""

    def components(self, run):
        return instance.components(run, list(self.SPEC.components))


def _arm(seconds):
    """Per-execution budget: armed only when run.py installed the handler (a test or a bare import has none, and the default action would kill the process)."""
    if callable(signal.getsignal(signal.SIGALRM)):
        signal.alarm(seconds)


def failure_outcome(job, f):
    label, interrupted_cause = classify.label_for_failure(f.phase, f.interrupted, f.watchdog)
    return common.Outcome(label, None, cause=f.cause, attribution=classify.attribution(f.interrupted, False), interrupted_cause=interrupted_cause)


def _write_bundle(job, real, run, outcome):
    manifest_outcome = classify.manifest_outcome(job.c, outcome.label, outcome.observed or outcome.cause)
    run.write_records(outcome, job.c)
    run.copy_provenance()
    run.log('run-end', category=outcome.label, interrupted_cause=outcome.interrupted_cause, attribution=outcome.attribution)
    run.close()  # executor.log is complete before the manifest hashes it
    notes = [f'attribution={outcome.attribution}'] + ([f'interrupted_cause={outcome.interrupted_cause}'] if outcome.interrupted_cause else [])
    manifest = common.build_manifest(run, manifest_outcome, real.SPEC, real.components(run), notes)
    common.write_manifest(run, manifest)


def _stub(job, real, index, reason):
    """An execution that began and left no bundle gets a record of the category RUNNER_ERROR, attributed TOOLING (a bundle that cannot be
    written is a fault of the executor or of the infrastructure; the five categories of D-E07-10 have no other place for it). The record is
    written only when the ordinary bundle could not be written; if it fails too, the job reports it and exits non-zero. Its cause starts with
    BUNDLE_NOT_WRITTEN."""
    run = common.Run(job, index)
    try:
        outcome = common.Outcome('RUNNER_ERROR', None, cause=f'BUNDLE_NOT_WRITTEN: {reason}', attribution='TOOLING')
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
            real.establish_check(run)
            real.verify(run)
            outcome = common.Outcome(config.SUCCESS_CATEGORY, 'continuity verified: every declared identity key and attribute matched on the verification layer')
        except common.PhaseFailure as f:
            outcome = failure_outcome(job, f)
        except Exception as e:  # noqa: BLE001 - the watchdog or a harness fault between two blocks: an interruption of the phase running
            run.log('error', traceback=traceback.format_exc())
            phase = run.phase or 'reset'
            outcome = failure_outcome(job, common.PhaseFailure(phase, f'interrupted between blocks in {phase}: {e.__class__.__name__}: {e}',
                                                               interrupted=True, watchdog=isinstance(e, common.Watchdog)))
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
    counts, causes, attributions = {}, {}, {}
    for r in results:
        counts[r['category']] = counts.get(r['category'], 0) + 1
        if r['interrupted_cause']:
            causes[r['interrupted_cause']] = causes.get(r['interrupted_cause'], 0) + 1
        key = f'{r["category"]}|{r["attribution"]}'
        attributions[key] = attributions.get(key, 0) + 1
    return {'record': 'condition summary (counts only; no interpretation)', 'condition': job.env.condition, 'sut': job.env.sut,
            'record_class': job.env.record_class, 'attempt': job.env.attempt, 'canonical_scenario_id': job.c['canonical_scenario_id'],
            'source_layer': job.c['source_layer'], 'verification_layer': job.c['verification_layer'],
            'executions_planned': job.planned, 'executions_run': len(results), 'categories': counts, 'interrupted_causes': causes,
            'category_by_attribution': attributions, 'executions': results, 'notes': job.notes}


def run_job(job, real):
    """Run the executions first..last of the condition. Returns the list of per-execution results."""
    results = []
    real.open()
    try:
        for index in range(job.first, job.last + 1):
            outcome = execute(job, real, index)
            results.append({'run_id': job.env.run_id(index), 'category': outcome.label, 'interrupted_cause': outcome.interrupted_cause,
                            'attribution': outcome.attribution})
            print(f'{job.env.run_id(index)}: {outcome.label}{" (" + outcome.interrupted_cause + ")" if outcome.interrupted_cause else ""} ({outcome.attribution})',
                  flush=True)
    finally:
        real.close()
        instance.collect_logs(job, os.path.join(job.env.output_dir, 'sut-logs'))
        summary = summarize(job, results)
        with open(os.path.join(job.env.output_dir, 'condition-summary.json'), 'w', encoding='utf-8') as f:
            f.write(job.scrub(json.dumps(summary, indent=2, ensure_ascii=False)))
    return results
