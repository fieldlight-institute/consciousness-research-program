"""Freeze once; refuse overwrites; preserve source and specification identities."""
import argparse
import hashlib
import json
import random
import statistics
from pathlib import Path
from study import simulate, CONDITIONS
ROOT=Path(__file__).resolve().parent

def identities():
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in ['SPECIFICATION.md','study.py','run.py','../simulate.py']}

def summarize(rows):
    by={(r['seed'],r['condition']):r for r in rows}
    result={'conditions':{},'contrasts':[]}
    for c in CONDITIONS:
        rs=[r for r in rows if r['condition']==c]
        result['conditions'][c]={k:statistics.mean(r[k] for r in rs)
            for k,v in rs[0].items() if isinstance(v,(int,float)) and k!='seed'}
    for control in ['site-veto','no-veto','skill-site-veto']:
        ds=[r['primary_rate']-by[r['seed'],control]['primary_rate'] for r in rows if r['condition']=='job-veto']
        rng=random.Random(493)
        boots=sorted(statistics.mean(rng.choices(ds,k=len(ds))) for _ in range(5000))
        result['contrasts'].append(dict(treatment='job-veto',control=control,n=len(ds),difference=statistics.mean(ds),ci_low=boots[124],ci_high=boots[4874]))
    return result

def validate(rows):
    for seed in sorted({r['seed'] for r in rows}):
        rs=[r for r in rows if r['seed']==seed]
        assert len(rs)==4
        for key in ['task_hash','primary_n','eligible']:
            assert len({r[key] for r in rs})==1,(seed,key)
        for r in rs:
            assert r['prohibited_executions']==0 and r['agent_completions'][0]==0
            assert r['collisions']==r['duplicate_arrivals']+r['expired_arrivals']
            assert 0<=r['primary_done']<=r['primary_n']
            assert r['scalar_reads']==5*r['record_reads']

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['freeze','pilot','evaluation']);args=p.parse_args()
    frozen=ROOT/'freeze.json'
    if args.phase=='freeze':
        with frozen.open('x') as f: json.dump(identities(),f,indent=2)
    else:
        assert identities()==json.loads(frozen.read_text()),'Frozen source changed'
        if args.phase=='evaluation':
            pilot=json.loads((ROOT/'pilot'/'all-seeds.json').read_text());validate(pilot)
            assert json.loads((ROOT/'pilot'/'manifest.json').read_text())['identities']==identities()
        seeds=range(200,210) if args.phase=='pilot' else range(1000,1040)
        out=ROOT/args.phase;out.mkdir(exist_ok=False)
        (out/'manifest.json').write_text(json.dumps(dict(phase=args.phase,seeds=list(seeds),identities=identities()),indent=2))
        rows=[]
        for seed in seeds:
            for c in CONDITIONS:
                row,trace=simulate(seed,c,detailed=seed==seeds.start)
                rows.append(row)
                if seed==seeds.start: (out/f'trace-{c}.json').write_text(json.dumps(trace))
            print(f'{args.phase} seed {seed} complete',flush=True)
        validate(rows)
        assert simulate(seeds.start,'job-veto')[0]==next(r for r in rows if r['seed']==seeds.start and r['condition']=='job-veto')
        assert identities()==json.loads(frozen.read_text())
        (out/'all-seeds.json').write_text(json.dumps(rows,indent=2))
        (out/'summary.json').write_text(json.dumps(summarize(rows),indent=2))
        print(json.dumps(summarize(rows)['contrasts'],indent=2))
