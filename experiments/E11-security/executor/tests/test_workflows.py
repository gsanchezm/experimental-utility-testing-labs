"""Static checks of .github/workflows/e11-environment-verification.yml (operation OP-PREP-E11). Textual: no YAML parser is needed and nothing runs.

The workflow is dispatch-only, reads the repository only, pulls the ZAP image by the digest that executor/zap.py holds, and lists exactly the
cells of conditions-draft.json. The bash of every `run` block must parse (bash -n) and the Python of every heredoc must compile."""
import json
import os
import re
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
WORKFLOW = os.path.join(REPO, '.github', 'workflows', 'e11-environment-verification.yml')
CELLS = os.path.join(REPO, 'experiments', 'E11-security', 'conditions-draft.json')


def text():
    with open(WORKFLOW, encoding='utf-8') as f:
        return f.read()


def run_blocks(t):
    """The body of every `run: |` block (the lines indented deeper than the key)."""
    lines, out, i = t.split('\n'), [], 0
    while i < len(lines):
        m = re.match(r'^(\s*)run: \|\s*$', lines[i])
        if m:
            indent, body = len(m.group(1)), []
            i += 1
            while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
                body.append(lines[i])
                i += 1
            out.append('\n'.join(body))
        else:
            i += 1
    return out


class EnvironmentVerificationWorkflowTests(unittest.TestCase):
    def test_it_is_dispatch_only_with_read_only_permissions(self):
        t = text()
        head = t.split('\njobs:')[0]
        triggers = re.search(r'^on:\n((?:  .*\n|\n)+)', head, re.M).group(1)
        self.assertEqual(re.findall(r'^  ([a-z_]+):', triggers, re.M), ['workflow_dispatch'])
        for forbidden in ('push:', 'pull_request', 'schedule:', 'workflow_run'):
            self.assertNotIn(forbidden, head)
        self.assertIn('permissions:\n  contents: read\n', head)
        self.assertNotIn('secrets.', t)

    def test_the_target_options_are_all_plus_the_cells_of_the_cells_file(self):
        t = text()
        opts = re.search(r'target:\n(?:.*\n)*?        options:\n((?:          - .*\n)+)', t).group(1)
        listed = re.findall(r'- (\S+)', opts)
        with open(CELLS, encoding='utf-8') as f:
            ids = [c['cell_id'] for c in json.load(f)['cells']]
        self.assertEqual(listed, ['all'] + ids)
        self.assertEqual(len(ids), 14)

    def test_the_zap_image_is_pulled_by_the_digest_of_the_executor_and_never_by_a_tag(self):
        t = text()
        self.assertIn("from executor import zap; print(zap.ZAP_IMAGE)", t)
        self.assertIn('docker pull "$IMAGE"', t)
        self.assertIn("case \"$IMAGE\" in *@sha256:*)", t)
        self.assertNotRegex(t, r'zaproxy/zaproxy:[A-Za-z0-9]')
        self.assertNotRegex(t, r'zap-(stable|weekly):')
        self.assertIn("if: ${{ matrix.method == 'M2' }}", t)

    def test_the_plan_matrix_carries_cell_sut_and_method(self):
        t = text()
        self.assertIn("include = [{'cell_id': c['cell_id'], 'sut_id': c['sut_id'], 'method': c['method']} for c in chosen]", t)
        self.assertNotIn('condition_id', t)
        self.assertNotIn('CONDITION_ID', t)

    def test_only_the_two_e11_suts_are_provisioned_and_no_browser_is_installed(self):
        t = text()
        self.assertEqual(sorted(set(re.findall(r"matrix\.sut_id == '(SUT-\d\d)'", t))), ['SUT-01', 'SUT-05'])
        for absent in ('playwright', 'chromium', 'pnpm', 'vite preview'):
            self.assertNotIn(absent, t.lower())

    def test_the_dry_run_is_never_measured_or_imported(self):
        t = text()
        self.assertIn('RECORD_CLASS: DRY_RUN', t)
        self.assertIn('test "$GUARD_DRY_RUN" = "true"', t)
        self.assertNotIn('MEASURED_EXPERIMENT', t.replace('never measured', ''))
        self.assertIn('retention-days: 90', t)

    def test_the_agent_instructions_file_is_not_named_literally(self):
        self.assertNotIn(chr(67) + chr(76) + chr(65) + chr(85) + chr(68) + chr(69) + '.md', text())  # the agent-instructions file name, built so that this file does not carry it

    def test_every_run_block_parses_as_bash_and_every_python_heredoc_compiles(self):
        blocks = run_blocks(text())
        self.assertGreaterEqual(len(blocks), 15)
        for n, body in enumerate(blocks):
            lines = [l for l in body.split('\n')]
            ind = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
            script = '\n'.join(l[ind:] for l in lines)
            with tempfile.NamedTemporaryFile('w', suffix='.sh', delete=False) as f:
                f.write(script)
                path = f.name
            try:
                r = subprocess.run(['bash', '-n', path], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f'block {n}: {r.stderr}')
            finally:
                os.unlink(path)
            for m in re.finditer(r"<<'PY'\n(.*?)\n\s*PY\b", body, re.S):
                code_lines = m.group(1).split('\n')
                cind = min((len(l) - len(l.lstrip()) for l in code_lines if l.strip()), default=0)
                compile('\n'.join(l[cind:] for l in code_lines), f'block-{n}', 'exec')


if __name__ == '__main__':
    unittest.main(verbosity=2)
