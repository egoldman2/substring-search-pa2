#!/usr/bin/env python3
"""Generate fixed instances and run the C++ timing driver."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import tempfile
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def configurations(smoke=False):
    if smoke:
        return [('random', 1024, 32, 26, mode) for mode in ('begin', 'end', 'absent')] + [
            ('repeated', 4096, 32, 1, 'absent'), ('periodic', 4096, 32, 2, 'absent'),
            ('prose', 4096, 32, 0, 'end')]
    rows = []
    for n in (1024, 16384, 262144):
        for alphabet in (2, 4, 26, 256):
            for mode in ('begin', 'end', 'absent'):
                rows.append(('random', n, 32, alphabet, mode))
        for family, alphabet in (('repeated', 1), ('periodic', 2), ('prose', 0)):
            for mode in ('begin', 'end', 'absent'):
                rows.append((family, n, 32, alphabet, mode))
    for m in (1, 8, 32, 128, 512):
        for family, alphabet in (('random', 26), ('repeated', 1), ('periodic', 2), ('prose', 0)):
            for mode in ('begin', 'end', 'absent'):
                if family == 'random' and m == 1 and mode != 'begin':
                    continue
                rows.append((family, 65536, m, alphabet, mode))
    return rows


def instance(config, seed, corpus):
    family, n, m, alphabet, mode = config
    rng = random.Random(seed)
    if family == 'random':
        for attempt in range(1000):
            text = bytes(rng.randrange(alphabet) for _ in range(n))
            pattern = bytes(rng.randrange(alphabet) for _ in range(m))
            if mode == 'begin' or text.find(pattern) < 0:
                break
        else:
            raise ValueError('could not construct absent random pattern')
    elif family == 'repeated':
        # vary byte values while preserving the exact adversarial structure
        a = 65 + seed % 20
        text, pattern = bytes([a]) * n, bytes([a]) * (m - 1) + bytes([a + 1])
    elif family == 'periodic':
        unit = bytes([65 + seed % 20, 97 + seed % 20])
        text = (unit * ((n + 1) // 2))[:n]
        pattern = (unit * ((m + 1) // 2))[:m - 1] + b'!'
    else:
        offset = (seed - 41052) * 977 % len(corpus)
        window = corpus[offset:] + corpus[:offset]
        text = (window * (n // len(window) + 1))[:n]
        pattern = text[:max(0, m - 1)] + b'\x00'
    if mode == 'begin':
        # periodic and repeated successes keep their structural prefix
        if family in ('periodic', 'repeated', 'prose'):
            pattern = text[:m]
        text = pattern + text[m:]
    elif mode == 'end':
        text = text[:-m] + pattern
    expected = {'begin': 0, 'end': n - m, 'absent': -1}[mode]
    if text.find(pattern) != expected:
        raise ValueError(f'incorrect first-position label: {config}, seed {seed}')
    return text, pattern, expected


def run(args):
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    corpus = (ROOT / 'data/austen.txt').read_bytes()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT))
    compiler = os.environ.get('CXX', 'c++')
    metadata = {'started_utc': datetime.now(timezone.utc).isoformat(), 'source_revision': revision,
        'source_dirty': dirty, 'os': platform.platform(), 'machine': platform.machine(),
        'python': platform.python_version(), 'compiler': subprocess.check_output([compiler, '--version'], text=True),
        'flags': os.environ.get('CXXFLAGS', '-std=c++17 -Wall -Wextra -Wpedantic -O2'),
        'clock': 'std::chrono::steady_clock', 'unit': 'nanoseconds per batch',
        'corpus_sha256': sha(corpus), 'repetitions': args.repetitions, 'instances': args.instances,
        'batch_target_ns': 1000000, 'batch_cap': 65536, 'driver_timeout_seconds': 30,
        'run_budget_seconds': 900, 'command': vars(args), 'status': 'running'}
    try:
        metadata['cpu'] = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string'], text=True, stderr=subprocess.DEVNULL).strip()
        metadata['memory_bytes'] = subprocess.check_output(['sysctl', '-n', 'hw.memsize'], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        metadata['cpu'] = platform.processor() or 'unavailable'
        metadata['memory_bytes'] = 'unavailable'
    (output / 'environment.json').write_text(json.dumps(metadata, indent=2) + '\n')
    manifest = []
    start = time.monotonic()
    columns = ['instance_id', 'phase', 'algorithm', 'repetition', 'order', 'batch', 'elapsed_ns',
        'result', 'preprocessing_comparisons', 'search_comparisons', 'correct']
    try:
        with (output / 'raw.csv').open('w', newline='') as file, tempfile.TemporaryDirectory() as temporary:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            for config in configurations(args.smoke):
                for index in range(args.instances):
                    if time.monotonic() - start > 900:
                        raise TimeoutError('complete-run runtime budget reached')
                    seed = 41052 + index
                    text, pattern, expected = instance(config, seed, corpus)
                    identifier = '_'.join(map(str, config)) + f'_{seed}'
                    row = dict(zip(('family', 'n', 'm', 'alphabet', 'mode'), config))
                    row.update(instance_id=identifier, seed=seed, expected=expected,
                        text_sha256=sha(text), pattern_sha256=sha(pattern), status='pending')
                    manifest.append(row)
                    text_path, pattern_path = Path(temporary) / 'text', Path(temporary) / 'pattern'
                    text_path.write_bytes(text)
                    pattern_path.write_bytes(pattern)
                    result = subprocess.run([str(ROOT / 'build/benchmark'), str(text_path), str(pattern_path),
                        str(args.repetitions), str(seed)], capture_output=True, text=True, timeout=30, check=True)
                    for timing in csv.DictReader(io.StringIO(result.stdout)):
                        if timing['correct'] != 'true':
                            raise ValueError('incorrect benchmark result')
                        writer.writerow(dict(instance_id=identifier, **timing))
                    row['status'] = 'complete'
                    file.flush()
            metadata['status'] = 'complete'
    except Exception as error:
        metadata['status'] = 'failed'
        metadata['error'] = str(error)
        raise
    finally:
        metadata['finished_utc'] = datetime.now(timezone.utc).isoformat()
        metadata['wall_seconds'] = time.monotonic() - start
        (output / 'environment.json').write_text(json.dumps(metadata, indent=2) + '\n')
        (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'{len(manifest)} validated instances written to {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='new directory; existing evidence is never overwritten')
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--instances', type=int, choices=range(1, 11), default=3)
    parser.add_argument('--repetitions', type=int, choices=range(1, 101), default=9)
    run(parser.parse_args())
