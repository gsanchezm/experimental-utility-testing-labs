"""Calibration of T_R and T_e of E10 from the baseline-against-baseline pairs (A against A2) of the DRY_RUN rounds under one implementation hash.
Reads only the *AA2-comparison.json files of the downloaded artifacts (never an A-against-B comparison). Uses the calibrate() of the executor.
Usage: calibrate_e10.py REPO ARTDIR [ARTDIR ...]   (each ARTDIR holds the four E10-DRY_RUN-<condition>-<n> artifact folders of one round)"""
import glob
import json
import os
import sys

repo = sys.argv[1]
sys.path.insert(0, os.path.join(repo, 'experiments', 'E10-visual', 'executor'))
from executor import classify  # noqa: E402

cfg = json.load(open(os.path.join(repo, 'experiments', 'E10-visual', 'conditions-draft.json'), encoding='utf-8'))
floors = cfg['rule']['floors']
factor = cfg['rule']['calibration_factor']
pairs = {}      # condition -> list of {'R','r'}
per_view = {}   # (condition, view) -> count
for art in sys.argv[2:]:
    for folder in sorted(glob.glob(os.path.join(art, 'E10-DRY_RUN-*'))):
        cond = os.path.basename(folder)[len('E10-DRY_RUN-'):].rsplit('-', 1)[0]
        for f in sorted(glob.glob(os.path.join(folder, 'executions', '*', 'evidence', '*AA2-comparison.json'))):
            d = json.load(open(f, encoding='utf-8'))
            assert d['pair'] == 'A against A2', f
            view = os.path.basename(f)[4:].rsplit('-AA2', 1)[0]
            pairs.setdefault(cond, []).append({'R': d['ratio'], 'r': [e['r'] for e in d.get('elements', [])]})
            per_view[(cond, view)] = per_view.get((cond, view), 0) + 1
out = {}
for cond in sorted(pairs):
    out[cond] = classify.calibrate(pairs[cond], floors, factor)
    print(cond, 'pairs', len(pairs[cond]), '->', {k: out[cond][k] for k in ('T_R', 'T_e', 'max_R_AA2', 'max_r_AA2')})
print('pairs per view:', {f'{c}/{v}': n for (c, v), n in sorted(per_view.items())})
print('min pairs per view:', min(per_view.values()))
json.dump({'floors': floors, 'factor': factor, 'conditions': out, 'pairs_per_view': {f'{c}/{v}': n for (c, v), n in sorted(per_view.items())}},
          open(os.environ.get('CAL_OUT', '/dev/stdout'), 'w'), indent=2)
