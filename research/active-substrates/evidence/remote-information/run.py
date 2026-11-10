"""Freeze once, run each phase once; refuses overwriting evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics
from study import simulate, CONDITIONS
ROOT=Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def sources():
    return {str(p.relative_to(ROOT.parent)):sha(p) for p in [ROOT/'SPECIFICATION.md', ROOT/'study.py', ROOT/'run.py', ROOT/'test_study.py', ROOT.parent/'simulate.py',ROOT.parent/'claim-specificity/study.py']}
def dump(path,data):
    with path.open('x') as f: json.dump(data,f,indent=2); f.write('\n')
def contrast(rows,a,b,metric):
    lookup={(r['seed'],r['condition']):r for r in rows}; seeds=sorted({r['seed'] for r in rows})
    differences=[lookup[s,a][metric]-lookup[s,b][metric] for s in seeds]
    rng=random.Random(73021)
    samples=sorted(statistics.mean(rng.choices(differences,k=len(differences))) for _ in range(10000))
    return dict(a=a,b=b,metric=metric,mean=statistics.mean(differences),ci95=[samples[249],samples[9749]],paired_n=len(seeds))
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('phase',choices=['freeze','pilot','evaluation']); args=parser.parse_args()
    if args.phase=='freeze':
        # Preserve hashes of every preexisting study artifact except disposable Python caches.
        old={str(p.relative_to(ROOT.parent)):sha(p) for p in ROOT.parent.rglob('*') if p.is_file() and ROOT not in p.parents and '__pycache__' not in p.parts}
        dump(ROOT/'freeze.json',dict(sources=sources(),preserved=old)); print('frozen'); return
    frozen=json.loads((ROOT/'freeze.json').read_text()); assert sources()==frozen['sources'],'source drift'
    for name,expected in frozen['preserved'].items(): assert sha(ROOT.parent/name)==expected,name
    out=ROOT/args.phase; out.mkdir(exist_ok=False)
    seeds=range(3000,3010) if args.phase=='pilot' else range(4000,4040)
    rows=[]
    for seed in seeds:
        for condition in CONDITIONS:
            result,trace=simulate(seed,condition,detailed=seed==seeds.start)
            rows.append(result)
            if trace: dump(out/f'trace-{condition}.json',trace)
    for seed in seeds:
        group=[r for r in rows if r['seed']==seed]
        for field in ['task_hash','eligible','primary_n','replacement_n']: assert len({r[field] for r in group})==1,(seed,field)
        assert all(r['prohibited_executions']==0 and r['transmissions']<=12000 for r in group)
        assert group[2]['primary_done']==group[3]['primary_done']
    dump(out/'rows.json',rows)
    metrics=['primary_rate','replacement_rate','completed','collisions','travel','wasted_travel','remote_commitments','remote_successes','transmissions','payload_scalars','observation_scans','mailbox_scans','board_comparisons','credit_updates','peak_credit_cells']
    summary={c:{m:statistics.mean(r[m] for r in rows if r['condition']==c) for m in metrics} for c in CONDITIONS}
    dump(out/'summary.json',dict(conditions=summary,contrasts=[contrast(rows,'A-fixed','local','primary_rate'),contrast(rows,'A-credit','A-fixed','primary_rate'),contrast(rows,'A-credit','A-credit-reset','replacement_rate')],source_hashes=sources()))
    for name,expected in frozen['preserved'].items(): assert sha(ROOT.parent/name)==expected,name
    print(json.dumps(dict(phase=args.phase,episodes=len(rows),summary=summary,original_artifacts_verified=len(frozen['preserved'])),indent=2))
if __name__=='__main__': main()
