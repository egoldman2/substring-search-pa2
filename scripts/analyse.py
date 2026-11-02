#!/usr/bin/env python3
"""Regenerate summaries and figures from retained measurements."""
import csv
import json
from collections import defaultdict
from pathlib import Path
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'results/main-2026-10-27'


def quartiles(values):
    return statistics.quantiles(values, n=4, method='inclusive')[::2]


def main():
    environment = json.loads((RUN / 'environment.json').read_text())
    if environment['status'] != 'complete' or environment['source_dirty']:
        raise ValueError('main measurements must be complete and use committed source')
    manifest = {x['instance_id']: x for x in json.loads((RUN / 'manifest.json').read_text())}
    raw = list(csv.DictReader((RUN / 'raw.csv').open()))
    groups = defaultdict(list)
    for row in raw:
        if row['correct'] != 'true':
            raise ValueError('incorrect row')
        if row['phase'] == 'timing':
            groups[row['instance_id'], row['algorithm']].append(row)
    instances, aggregated = [], defaultdict(list)
    for (identifier, algorithm), rows in groups.items():
        params = manifest[identifier]
        expected = 'npos' if params['expected'] < 0 else str(params['expected'])
        if len(rows) != 9 or any(x['result'] != expected for x in rows):
            raise ValueError('missing repetition or wrong result')
        samples = [float(x['elapsed_ns']) / int(x['batch']) for x in rows]
        q1, q3 = quartiles(samples)
        row = {k: params[k] for k in ('instance_id', 'family', 'n', 'm', 'alphabet', 'mode', 'seed')}
        row.update(algorithm=algorithm, median_ns=statistics.median(samples), q1_ns=q1, q3_ns=q3,
            preprocessing_comparisons=int(rows[0]['preprocessing_comparisons']),
            search_comparisons=int(rows[0]['search_comparisons']), repetitions=len(rows))
        if params['family'] == 'repeated' and params['mode'] == 'absent' and params['m'] > 1:
            n, m = params['n'], params['m']
            wanted = ((n-m+1)*m, 0) if algorithm == 'naive' else (2*n-m+1, 2*m-3)
            if (row['search_comparisons'], row['preprocessing_comparisons']) != wanted:
                raise ValueError('adversarial counter formula failed')
        instances.append(row)
        key = tuple(row[k] for k in ('family', 'n', 'm', 'alphabet', 'mode', 'algorithm'))
        aggregated[key].append(row)
    if len(instances) != 726:
        raise ValueError('incomplete main study')
    summary = []
    for key, rows in aggregated.items():
        if len(rows) != 3:
            raise ValueError('expected three instances')
        q1, q3 = quartiles([x['median_ns'] for x in rows])
        row = dict(zip(('family', 'n', 'm', 'alphabet', 'mode', 'algorithm'), key))
        row.update(median_ns=statistics.median(x['median_ns'] for x in rows), q1_ns=q1, q3_ns=q3,
            preprocessing_comparisons=statistics.median(x['preprocessing_comparisons'] for x in rows),
            search_comparisons=statistics.median(x['search_comparisons'] for x in rows), instances=3,
            repetitions_per_instance=9)
        summary.append(row)
    def write_csv(path, rows):
        with path.open('w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    write_csv(ROOT / 'results/instance-summary.csv', instances)
    write_csv(ROOT / 'results/summary.csv', summary)
    def get(family, n, m, alphabet, mode, algorithm):
        return next(r for r in summary if all(r[k] == v for k,v in
            zip(('family','n','m','alphabet','mode','algorithm'),(family,n,m,alphabet,mode,algorithm))))
    facts = {'instances':len(manifest), 'timed_batches':sum(len(x) for x in groups.values()),
        'raw_rows':len(raw), 'source_revision':environment['source_revision'][:7]}
    for tag, config in {'repeated512':('repeated',65536,512,1,'absent'),
        'repeated32':('repeated',262144,32,1,'absent'),
        'binary':('random',262144,32,2,'absent'),
        'random26':('random',262144,32,26,'absent'),
        'prose':('prose',262144,32,0,'absent'),
        'begin512':('repeated',65536,512,1,'begin')}.items():
        a, b = [get(*config, alg) for alg in ('naive','kmp')]
        for alg, row in (('naive',a),('kmp',b)):
            facts[f'{tag}_{alg}_us'] = f"{row['median_ns']/1000:.3f}"
            facts[f'{tag}_{alg}_iqr_us'] = f"{row['q1_ns']/1000:.3f}-{row['q3_ns']/1000:.3f}"
            facts[f'{tag}_{alg}_comparisons'] = f"{int(row['preprocessing_comparisons']+row['search_comparisons']):,}"
        facts[f'{tag}_speedup'] = f"{a['median_ns']/b['median_ns']:.2f}"
        facts[f'{tag}_comparison_ratio'] = f"{(a['preprocessing_comparisons']+a['search_comparisons'])/(b['preprocessing_comparisons']+b['search_comparisons']):.2f}"
    facts['capped_timed_batches'] = sum(int(x['batch']) == 65536 and float(x['elapsed_ns']) < 1e6
        for rows in groups.values() for x in rows)
    (ROOT / 'results/facts.json').write_text(json.dumps(facts, indent=2)+'\n')
    plt.rcParams.update({'font.size':11, 'axes.spines.top':False, 'axes.spines.right':False,
        'savefig.dpi':180, 'svg.hashsalt':'substring-search'})
    colours = {'naive':'#225a95','kmp':'#bd4a2d'}
    def lines(ax, configs, xvalues, ylabel='Time per search (microseconds)'):
        for alg in ('naive','kmp'):
            rows = [get(*config,alg) for config in configs]
            ys = [r['median_ns']/1000 for r in rows]
            ax.errorbar(xvalues,ys,yerr=[[y-r['q1_ns']/1000 for y,r in zip(ys,rows)],
                [r['q3_ns']/1000-y for y,r in zip(ys,rows)]],label=alg,color=colours[alg],marker='o',capsize=3)
        ax.set_xscale('log',base=2)
        ax.set_yscale('log')
        ax.set_ylabel(ylabel)
        ax.grid(alpha=.18)
    def save(fig, stem):
        fig.tight_layout()
        fig.savefig(ROOT/f'figures/{stem}.png')
        fig.savefig(ROOT/f'figures/{stem}.pdf',metadata={'CreationDate':None,'ModDate':None})
        plt.close(fig)
    sizes = (1024,16384,262144)
    fig,axes = plt.subplots(1,3,figsize=(13,4.1))
    for ax,(family,alphabet,title) in zip(axes,[('random',26,'Random, alphabet 26'),('repeated',1,'Repeated near-match'),('prose',0,'Ordinary prose')]):
        lines(ax,[(family,n,32,alphabet,'absent') for n in sizes],sizes)
        ax.set_title(title); ax.set_xlabel('Text length (bytes)')
    axes[0].legend()
    save(fig,'runtime-size')
    lengths = (1,8,32,128,512)
    fig,axes = plt.subplots(1,3,figsize=(13,4.1))
    for ax,(family,alphabet,title) in zip(axes,[('repeated',1,'Repeated near-match'),('periodic',2,'Periodic near-match'),('prose',0,'Ordinary prose')]):
        lines(ax,[(family,65536,m,alphabet,'absent') for m in lengths],lengths)
        ax.set_title(title); ax.set_xlabel('Pattern length (bytes)')
    axes[0].legend()
    save(fig,'runtime-pattern')
    fig,axes = plt.subplots(1,2,figsize=(11,4.2))
    for alg in ('naive','kmp'):
        rows=[get('repeated',65536,m,1,'absent',alg) for m in lengths]
        axes[0].plot(lengths,[r['search_comparisons']+r['preprocessing_comparisons'] for r in rows],marker='o',label=alg,color=colours[alg])
        rows=[get('repeated',65536,m,1,'begin',alg) for m in lengths]
        axes[1].plot(lengths,[r['preprocessing_comparisons'] for r in rows],marker='o',label=alg,color=colours[alg])
    for ax in axes:
        ax.set_xscale('log',base=2); ax.set_xlabel('Pattern length (bytes)'); ax.set_ylabel('Byte equality tests per search'); ax.grid(alpha=.18)
    axes[0].set_yscale('log'); axes[0].set_title('Absent: total comparisons'); axes[0].legend()
    axes[1].set_title('Beginning match: preprocessing only')
    save(fig,'comparisons')
    fig,ax=plt.subplots(figsize=(8,4.4))
    alphabets=(2,4,26,256)
    timing,counts=[],[]
    for alphabet in alphabets:
        a,b=[get('random',262144,32,alphabet,'absent',alg) for alg in ('naive','kmp')]
        timing.append(a['median_ns']/b['median_ns'])
        counts.append((a['search_comparisons']+a['preprocessing_comparisons'])/(b['search_comparisons']+b['preprocessing_comparisons']))
    ax.plot(alphabets,timing,'o-',label='Runtime ratio'); ax.plot(alphabets,counts,'s-',label='Comparison ratio')
    ax.axhline(1,color='gray',linewidth=.8); ax.set_xscale('log',base=2)
    ax.set_xlabel('Random alphabet size'); ax.set_ylabel('Naive / KMP'); ax.legend(); ax.grid(alpha=.18)
    save(fig,'alphabet-ratios')
    table=['# Main results','', 'Times are medians of three instance medians. Each instance has nine timed batches.',
        'IQR spans the three instance medians using inclusive linear interpolation. Units: microseconds per search.',
        '', '| Configuration | Naive median (IQR) | KMP median (IQR) | Naive / KMP time |', '| --- | --- | --- | --- |']
    for tag,label in [('repeated512','Repeated absent, n=65,536 m=512'),('repeated32','Repeated absent, n=262,144 m=32'),
        ('binary','Random alphabet 2 absent, n=262,144 m=32'),('random26','Random alphabet 26 absent, n=262,144 m=32'),
        ('prose','Prose absent, n=262,144 m=32'),('begin512','Repeated beginning, n=65,536 m=512')]:
        table.append(f"| {label} | {facts[tag+'_naive_us']} ({facts[tag+'_naive_iqr_us']}) | {facts[tag+'_kmp_us']} ({facts[tag+'_kmp_iqr_us']}) | {facts[tag+'_speedup']} |")
    (ROOT/'results/tables.md').write_text('\n'.join(table)+'\n')
    print(json.dumps(facts,indent=2))


if __name__ == '__main__':
    main()
