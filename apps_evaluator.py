"""APPS stdin/stdout evaluator using an isolated Docker container.

Requires Docker Desktop with Linux containers enabled. Never executes submitted
code directly on the host. This is a local experimental evaluator, not the
official APPS grading harness.
"""
import argparse
import json
import subprocess
from pathlib import Path

IMAGE = 'python:3.11-alpine'


def normalize(text):
    # Normalization for the local pilot; the official APPS judge may differ.
    return '\n'.join(line.rstrip() for line in text.strip().splitlines())


def run_case(code, stdin, timeout=5):
    cmd = [
        'docker', 'run', '--rm', '-i', '--network', 'none',
        '--memory', '256m', '--memory-swap', '256m',
        '--cpus', '1', '--pids-limit', '64',
        '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
        '--user', '65534:65534', '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m',
        IMAGE, 'python', '-I', '-B', '-c', code,
    ]
    try:
        result = subprocess.run(
            cmd,
            input=stdin.encode('utf-8'),
            capture_output=True,
            timeout=timeout + 12,
        )

        result.stdout = result.stdout.decode('utf-8', errors='replace')
        result.stderr = result.stderr.decode('utf-8', errors='replace')
    except subprocess.TimeoutExpired:
        return {'status': 'timeout', 'stdout': '', 'stderr': 'Container exceeded wall-clock limit'}
    except FileNotFoundError:
        return {'status': 'setup_error', 'stdout': '', 'stderr': 'Docker CLI not found'}
    if result.returncode != 0:
        return {'status': 'runtime_error', 'stdout': result.stdout, 'stderr': result.stderr[-1000:]}
    return {'status': 'ok', 'stdout': result.stdout, 'stderr': result.stderr[-1000:]}


def evaluate(problem, code):
    tests = problem['input_output']
    if isinstance(tests, str):
        tests = json.loads(tests)
    if tests.get('fn_name'):
        raise ValueError('Function-call APPS tests require a different evaluator; this evaluator supports stdin/stdout only')
    inputs, outputs = tests['inputs'], tests['outputs']
    if not inputs or len(inputs) != len(outputs):
        raise ValueError('Invalid test-case inputs/outputs')
    results = []
    for index, (inp, expected) in enumerate(zip(inputs, outputs), start=1):
        if not isinstance(inp, str) or not isinstance(expected, str):
            raise ValueError('This evaluator requires string stdin and stdout cases')
        execution = run_case(code, inp)
        passed = execution['status'] == 'ok' and normalize(execution['stdout']) == normalize(expected)
        results.append({
            'test': index, 'passed': passed, 'status': execution['status'],
            'expected': expected[:300], 'actual': execution['stdout'][:300],
            'stderr': execution['stderr'],
        })
        print(f"  Test {index}: {'PASS' if passed else 'FAIL'} ({execution['status']})")
        if execution['status'] == 'setup_error':
            raise RuntimeError(execution['stderr'])
    return {'problem_id': problem['problem_id'], 'passed': all(r['passed'] for r in results),
            'passed_tests': sum(r['passed'] for r in results), 'total_tests': len(results),
            'tests': results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='results/apps_competition_20.jsonl')
    parser.add_argument('--code', help='Python source file to evaluate')
    parser.add_argument('--problem-id', type=int, help='APPS problem ID')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    docker = subprocess.run(['docker', 'info', '--format', '{{.ServerVersion}}'],
                            capture_output=True, text=True, check=False)
    if docker.returncode != 0:
        raise SystemExit('Docker Desktop must be installed and running with Linux containers enabled.\n' + docker.stderr[-500:])
    print('Docker engine:', docker.stdout.strip())
    if args.self_test:
        fixture = {'problem_id': 'synthetic_addition', 'input_output': {
            'inputs': ['2 3\n', '10 25\n', '-4 7\n'],
            'outputs': ['5\n', '35\n', '3\n']}}
        correct = 'a,b=map(int,input().split());print(a+b)'
        wrong = 'a,b=map(int,input().split());print(a-b)'
        print('Validating evaluator with a known correct program:')
        positive = evaluate(fixture, correct)
        print('Validating evaluator with a known incorrect program:')
        negative = evaluate(fixture, wrong)
        if not positive['passed'] or negative['passed']:
            raise SystemExit('SELF TEST FAILED')
        print('SELF TEST PASSED: correct solution accepted; incorrect solution rejected')
        return
    if not args.code or args.problem_id is None:
        parser.error('Use --self-test or provide both --code and --problem-id')
    with open(args.dataset, encoding='utf-8') as f:
        problems = [json.loads(line) for line in f if line.strip()]
    matches = [p for p in problems if int(p['problem_id']) == args.problem_id]
    if len(matches) != 1:
        raise SystemExit('Problem ID not found or duplicated')
    code = Path(args.code).read_text(encoding='utf-8')
    outcome = evaluate(matches[0], code)
    print(json.dumps(outcome, indent=2))
    output_path = Path('results/apps_evaluator_last_result.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(outcome, indent=2), encoding='utf-8')
    print('Saved:', output_path)


if __name__ == '__main__':
    main()
