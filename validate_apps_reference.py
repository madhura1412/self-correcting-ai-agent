"""Validate the local Docker evaluator using APPS reference solutions.

Run in the project root after installing datasets and starting Docker Desktop.
This reads reference solutions only for evaluator validation, never for LLM prompts.
"""
import json
from pathlib import Path
from datasets import load_dataset
from apps_evaluator import evaluate

LOCAL = Path('results/apps_competition_20.jsonl')
REPORT = Path('results/apps_reference_validation.json')
SOURCE = 'metr-evals/apps'
TARGET = 3


def parse_solutions(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            return []
    return [s for s in value if isinstance(s, str) and s.strip()] if isinstance(value, list) else []


def main():
    if not LOCAL.exists():
        raise SystemExit(f'Missing {LOCAL}; place your downloaded JSONL in results/')
    local = {int(p['problem_id']): p for line in LOCAL.read_text(encoding='utf-8').splitlines()
             if line.strip() for p in [json.loads(line)]}
    if len(local) != 20:
        print(f'Note: local file has {len(local)} unique problems (expected 20).')
    print('Looking up reference solutions in APPS test split...')
    rows = load_dataset(SOURCE, split='test', streaming=True)
    results = []
    for row in rows:
        pid = int(row['problem_id'])
        if pid not in local:
            continue
        solutions = parse_solutions(row.get('solutions'))
        if not solutions:
            print(f'APPS {pid}: no reference solution available; skipping')
            continue
        p = local[pid]
        if p['input_output'].get('fn_name'):
            print(f'APPS {pid}: call-based format; skipping')
            continue
        print(f'\nValidating APPS {pid} with {len(solutions)} available references...')
        best = None
        # Try at most three references to limit Docker execution cost.
        for index, solution in enumerate(solutions[:3], start=1):
            try:
                outcome = evaluate(p, solution)
            except (ValueError, RuntimeError) as exc:
                print('Evaluator error:', exc)
                continue
            print(f'  Reference {index}: {outcome["passed_tests"]}/{outcome["total_tests"]} tests passed')
            if best is None or outcome['passed_tests'] > best['passed_tests']:
                best = {**outcome, 'reference_index': index}
            if outcome['passed']:
                break
        if best:
            results.append({'problem_id': pid, 'reference_index': best['reference_index'],
                            'passed': best['passed'], 'passed_tests': best['passed_tests'],
                            'total_tests': best['total_tests'], 'tests': best['tests']})
        if len(results) >= TARGET:
            break
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'\nSaved validation report: {REPORT}')
    print(f'Validated {len(results)} real APPS problems; '
          f'{sum(x["passed"] for x in results)} fully passed with a reference solution.')
    if not results:
        print('No reference solutions were available for selected problems. '
              'Do not treat this as evaluator validation.')
    elif any(not x['passed'] for x in results):
        print('Some reference solutions failed. Inspect the saved report before LLM evaluation.')


if __name__ == '__main__':
    main()
