"""Observe resource use without changing the frozen extraction request or scorer."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def sample():
    values = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        if key in {'MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree'}:
            values[key + 'KiB'] = int(value.split()[0])
    rss = 0
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            exe = (proc / 'exe').resolve().as_posix()
            if '/ollama/' not in exe and not exe.endswith('/ollama'):
                continue
            for line in (proc / 'status').read_text().splitlines():
                if line.startswith('VmRSS:'):
                    rss += int(line.split()[1])
        except (OSError, ValueError):
            continue
    return {'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            **values, 'ollamaRssSumKiB': rss}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', choices=['baseline', 'qwen-recommended'], default='baseline')
    parser.add_argument('--think', action='store_true')
    parser.add_argument('--prompt-schema', action='store_true')
    parser.add_argument('--max-tokens', type=int, default=800)
    parser.add_argument('--timeout', type=int, default=360)
    parser.add_argument('--case', dest='case_id')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    monitor_path = args.output.with_name(args.output.stem + '-resources.json')
    stop = threading.Event()
    samples = []
    failures = []

    def monitor():
        while not stop.is_set():
            try:
                samples.append(sample())
                monitor_path.write_text(json.dumps({'samples': samples, 'errors': failures}, indent=2) + '\n')
            except (OSError, ValueError) as exc:
                failures.append(str(exc))
            stop.wait(5)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    extra = ['--max-tokens', str(args.max_tokens), '--timeout', str(args.timeout), '--profile', args.profile]
    if args.prompt_schema:
        extra.append('--prompt-schema')
    if args.think:
        extra.append('--think')
    if args.case_id:
        extra.extend(['--case', args.case_id])
    try:
        result = subprocess.run([sys.executable, '-u', str(ROOT / 'scripts/benchmark_spinoff_llm.py'),
                                 '--model', args.model, '--output', str(args.output), *extra], check=False)
    finally:
        stop.set()
        thread.join(timeout=10)
    resources = {'samples': samples, 'errors': failures,
                 'samplingSeconds': 5, 'inferenceExitCode': result.returncode,
                 'note': 'Sampled RSS sum can double-count shared pages; system available memory and swap include other runner processes. Not an exact memory peak.'}
    if samples:
        resources.update(maxOllamaRssSumKiB=max(s['ollamaRssSumKiB'] for s in samples),
                         minSystemAvailableKiB=min(s['MemAvailableKiB'] for s in samples),
                         maxSystemSwapUsedKiB=max(s['SwapTotalKiB'] - s['SwapFreeKiB'] for s in samples))
    monitor_path.write_text(json.dumps(resources, indent=2) + '\n')
    print('BENCHMARK_RESOURCES ' + json.dumps({k: v for k, v in resources.items() if k != 'samples'}), flush=True)
    if args.output.exists():
        # Preserve the complete original report in downloadable job logs too.
        print('BENCHMARK_REPORT ' + json.dumps(json.loads(args.output.read_text()), ensure_ascii=False), flush=True)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
