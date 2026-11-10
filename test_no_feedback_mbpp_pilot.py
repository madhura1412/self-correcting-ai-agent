"""Pilot: test no-feedback correction on 10 original MBPP initial failures.
Run in the self-correcting-ai-agent project root with Ollama available.
Does not overwrite any original results.
"""
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from feedback import correct_code
from executor import execute_mbpp_code
from load_mbpp import load_mbpp_problems

SOURCE = Path('results/mbpp_results_100.csv')
RUN_ID = '20261001_183513'
OUTPUT = Path('results/no_feedback_mbpp_pilot.csv')
N = 10

with SOURCE.open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))

initial = {r['problem_id']: r for r in rows
           if r['run_id'] == RUN_ID and r['feedback_strategy'] == 'baseline'
           and str(r['attempt']) == '1'}
failed_ids = [pid for pid, row in initial.items()
              if row['success'].strip().lower() not in ('true', '1')]
selected = failed_ids[:N]
if len(selected) < N:
    raise RuntimeError(f'Found only {len(selected)} initial failures; check CSV and run ID.')

problems = {p['problem_id']: p for p in load_mbpp_problems(100)}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
fieldnames = ['timestamp', 'problem_id', 'initial_success', 'correction_success',
              'execution_time', 'previous_code', 'corrected_code', 'error']
completed = set()
if OUTPUT.exists():
    with OUTPUT.open(encoding='utf-8-sig', newline='') as f:
        completed = {r['problem_id'] for r in csv.DictReader(f)}

with OUTPUT.open('a', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if OUTPUT.stat().st_size == 0:
        writer.writeheader()
    for index, pid in enumerate(selected, 1):
        if pid in completed:
            print(f'[{index}/{N}] Skipping saved {pid}')
            continue
        p = problems[pid]
        previous_code = initial[pid]['code']
        problem_text = p['prompt']
        if p['required_call']:
            problem_text += ('\n\nRequired function call: ' + p['required_call'])
        print(f'[{index}/{N}] Correcting {pid} without feedback...', flush=True)
        corrected = correct_code(
            problem=problem_text,
            previous_code=previous_code,
            feedback_strategy='no_feedback',
            error='', test_feedback=''
        )
        result = execute_mbpp_code(corrected, p['tests'], p['test_imports'], timeout=5)
        writer.writerow({
            'timestamp': datetime.now().isoformat(timespec='seconds'),
            'problem_id': pid, 'initial_success': False,
            'correction_success': result['success'],
            'execution_time': round(result['execution_time'], 4),
            'previous_code': previous_code, 'corrected_code': corrected,
            'error': result['error']
        })
        f.flush()
        print(f'    {"PASS" if result["success"] else "FAIL"}', flush=True)

with OUTPUT.open(encoding='utf-8-sig', newline='') as f:
    saved = {r['problem_id']: r for r in csv.DictReader(f) if r['problem_id'] in selected}
passes = sum(r['correction_success'].lower() == 'true' for r in saved.values())
print(f'\nPilot result: {passes}/{len(saved)} corrected successfully.')
print(f'Saved: {OUTPUT}')
