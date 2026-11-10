"""Freeze and retain every run of the spatial adaptation extension."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import statistics
from study import simulate,CONDITIONS
ROOT=Path(__file__).resolve().parent
SOURCE_ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sources():return {p.name:sha(p) for p in [ROOT/n for n in ['SPECIFICATION.md','study.py','medium.py','test_medium.py','run.py']]}
def write(p,data):
    with p.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
def contrast(rows,a,b,metric):
    by={(r['seed'],r['condition']):r for r in rows};seeds=sorted({r['seed'] for r in rows})
    diff=[by[s,a][metric]-by[s,b][metric] for s in seeds];rng=random.Random(73023)
    boots=sorted(statistics.mean(rng.choices(diff,k=len(diff))) for _ in range(10000))
    return dict(a=a,b=b,metric=metric,mean=statistics.mean(diff),ci95=[boots[249],boots[9749]],n=len(seeds))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['freeze','pilot','evaluation']);args=parser.parse_args()
    if args.phase=='freeze':
        previous={str(p.relative_to(ROOT.parent)):sha(p) for p in ROOT.parent.rglob('*') if p.is_file() and ROOT not in p.parents and '__pycache__' not in p.parts}
        lineage={str(SOURCE_ROOT/n):sha(SOURCE_ROOT/n) for n in ['01-computational-fascia.md','04-generative-participation.md']}
        write(ROOT/'freeze.json',dict(sources=sources(),preserved=previous,lineage=lineage,runtime=platform.python_version()));print('frozen');return
    frozen=json.loads((ROOT/'freeze.json').read_text());assert frozen['sources']==sources()
    def verify():
        for n,h in frozen['preserved'].items():assert sha(ROOT.parent/n)==h,n
        for n,h in frozen['lineage'].items():assert sha(Path(n))==h,n
    verify();out=ROOT/args.phase;out.mkdir(exist_ok=False)
    seeds=range(7000,7010) if args.phase=='pilot' else range(8000,8040)
    rows=[]
    for seed in seeds:
        for c in CONDITIONS:
            r,t=simulate(seed,c,detailed=seed==seeds.start);rows.append(r)
            if seed==seeds.start:write(out/f'trace-{c}.json',t)
    for seed in seeds:
        group=[r for r in rows if r['seed']==seed]
        for k in ['task_hash','eligible','primary_n','edge_updates','receipt_writes']:assert len({r[k] for r in group})==1
        assert all(r['prohibited_executions']==0 and r['agent_completions'][0]==0 for r in group)
        assert group[1]['primary_done']==group[3]['primary_done']
    write(out/'rows.json',rows)
    metrics=['primary_rate','replacement_rate','completed','collisions','travel','wasted_travel','reads','writes','edge_updates','receipt_writes','eligibility_reads','feedback_updates','relaxations','weight_min','weight_max','weight_mean']
    summary=dict(conditions={c:{m:statistics.mean(r[m] for r in rows if r['condition']==c) for m in metrics} for c in CONDITIONS},contrasts=[contrast(rows,'D','C','primary_rate'),contrast(rows,'D','D-frozen','primary_rate'),contrast(rows,'D','D-reset','replacement_rate')],source_hashes=sources())
    write(out/'summary.json',summary);verify()
    print(json.dumps(dict(phase=args.phase,episodes=len(rows),contrasts=summary['contrasts'],previous_files_verified=len(frozen['preserved']),original_specifications_verified=len(frozen['lineage'])),indent=2))
if __name__=='__main__':main()
