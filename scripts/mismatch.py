#!/usr/bin/env python3
"""Run the post-main controlled mismatch-position experiment."""
import csv
import io
import json
from pathlib import Path
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from experiment import ROOT, sha

output = ROOT / 'results/mismatch-2026-10-27'
output.mkdir(exist_ok=False)
metadata = json.loads((ROOT/'results/main-2026-10-27/environment.json').read_text())
metadata.update(started_utc=datetime.now(timezone.utc).isoformat(),
    source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    source_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)),
    command='python3 scripts/mismatch.py', status='running', instances=3, repetitions=9)
rows, manifest = [], []
start = time.monotonic()
try:
    with tempfile.TemporaryDirectory() as directory:
        text_path, pattern_path = Path(directory)/'text', Path(directory)/'pattern'
        for position in (0,1,7,31,127,511):
            for seed in (41052,41053,41054):
                a = 65 + seed % 20
                text = bytes([a])*65536
                pattern = bytes([a])*position + bytes([a+1]) + bytes([a])*(511-position)
                if text.find(pattern) != -1:
                    raise ValueError('expected absent controlled pattern')
                identifier=f'mismatch_{position}_{seed}'
                text_path.write_bytes(text); pattern_path.write_bytes(pattern)
                result=subprocess.run([str(ROOT/'build/benchmark'),str(text_path),str(pattern_path),'9',str(seed)],
                    capture_output=True,text=True,check=True,timeout=30)
                rows.extend(dict(instance_id=identifier,**r) for r in csv.DictReader(io.StringIO(result.stdout)))
                manifest.append(dict(instance_id=identifier,n=65536,m=512,position=position,seed=seed,
                    text_sha256=sha(text),pattern_sha256=sha(pattern),expected=-1,status='complete'))
    metadata['status']='complete'
finally:
    metadata['finished_utc']=datetime.now(timezone.utc).isoformat()
    metadata['wall_seconds']=time.monotonic()-start
    (output/'environment.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if rows:
        with (output/'raw.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
print(f'{len(manifest)} controlled instances complete')
