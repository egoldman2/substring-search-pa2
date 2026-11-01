"""Small checks for generated labels and the file-based command interface."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from experiment import configurations, instance

corpus = (ROOT / 'data/austen.txt').read_bytes()
for config in configurations():
    for seed in (41052, 41053, 41054):
        text, pattern, expected = instance(config, seed, corpus)
        if len(text) != config[1] or len(pattern) != config[2] or text.find(pattern) != expected:
            raise RuntimeError(f'bad generated instance: {config}, {seed}')

with tempfile.TemporaryDirectory() as directory:
    text_path, pattern_path = Path(directory) / 'text', Path(directory) / 'pattern'
    text_path.write_bytes(b'a\x00\xffb')
    for pattern, expected in ((b'\x00\xff', '1'), (b'', '0'), (b'xyz', 'npos')):
        pattern_path.write_bytes(pattern)
        for algorithm in ('naive', 'kmp'):
            run = subprocess.run([str(ROOT / 'build/search'), algorithm, str(text_path), str(pattern_path)],
                capture_output=True, text=True, check=True)
            if run.stdout.strip() != expected:
                raise RuntimeError('incorrect binary CLI result')
    invalid = subprocess.run([str(ROOT / 'build/search'), 'bad', str(text_path), str(pattern_path)], capture_output=True)
    missing = subprocess.run([str(ROOT / 'build/search'), 'kmp', str(text_path), directory + '/missing'], capture_output=True)
    if invalid.returncode != 2 or missing.returncode != 1:
        raise RuntimeError('CLI error status is wrong')
print('All 363 generated instances and binary CLI checks passed.')
