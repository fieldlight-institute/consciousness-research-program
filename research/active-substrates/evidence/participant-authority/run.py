"""Frozen factorial, independent donor replay, and pilot-based sample planning."""
import json,hashlib,platform,statistics,random,sys,math
from pathlib import Path
from study import simulate,CONDITIONS
ROOT=Path(__file__).resolve().parent
SOURCE=Path(__file__).resolve().parents[2]/'04-generative-participation.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def sources():return {p.name:sha(p) for p in ROOT.iterdir() if p.suffix in ('.py','.md') and p.name!='RESULTS.md'}
def interval(diff):
    rng=random.Random(73023);boots=sorted(statistics.mean(rng.choices(diff,k=len(diff))) for _ in range(10000))
    return dict(mean=statistics.mean(diff),ci95=[boots[249],boots[9749]],n=len(diff))
def differences(rows,kind):
    by={(r['seed'],r['condition']):r for r in rows};seeds=sorted({r['seed'] for r in rows})
    value=lambda s,c:by[s,c]['primary_rate']
    if kind=='primary':return [value(s,'R1A1')-value(s,'Yoked') for s in seeds]
    if kind=='interaction':return [value(s,'R1A1')-value(s,'R1A0')-value(s,'R0A1')+value(s,'R0A0') for s in seeds]
    return [value(s,'R1A1')-value(s,'R0A0') for s in seeds]
def main():
    phase=sys.argv[1];assert phase in ('freeze','pilot','size','evaluation')
    if phase=='freeze':
        preserved={str(p.relative_to(ROOT.parent)):sha(p) for p in ROOT.parent.rglob('*') if p.is_file() and ROOT not in p.parents and '__pycache__' not in p.parts}
        write(ROOT/'freeze.json',dict(sources=sources(),preserved=preserved,lineage={str(SOURCE):sha(SOURCE)},runtime=platform.python_version()));print('frozen',len(preserved));return
    frozen=json.loads((ROOT/'freeze.json').read_text());assert sources()==frozen['sources']
    def verify():
        for n,h in frozen['preserved'].items():assert sha(ROOT.parent/n)==h,n
        for n,h in frozen['lineage'].items():assert sha(Path(n))==h,n
    verify()
    if phase=='size':
        rows=json.loads((ROOT/'pilot/rows.json').read_text());sd=statistics.stdev(differences(rows,'primary'));raw=math.ceil(((1.96+.84)*sd/.005)**2);n=min(200,max(40,raw))
        out=dict(pilot_sd=sd,planning_difference=.005,nominal_power=.8,uncapped_n=raw,n=n,capped=raw>200,pilot_hash=sha(ROOT/'pilot/rows.json'),source_hashes=sources());write(ROOT/'sample-size.json',out);print(json.dumps(out,indent=2));return
    out=ROOT/phase;out.mkdir(exist_ok=False)
    if phase=='pilot':seeds=range(13000,13010)
    else:
        plan=json.loads((ROOT/'sample-size.json').read_text());assert plan['pilot_hash']==sha(ROOT/'pilot/rows.json');assert plan['source_hashes']==sources();seeds=range(14000,14000+plan['n'])
    rows=[];donors=[]
    for seed in seeds:
        dr,dt=simulate(seed+100000,'R1A1',detailed=True);donors.append(dr)
        write(out/f'donor-couplings-{seed}.json',dict(seed=seed+100000,couplings=dt['couplings']))
        if seed==seeds.start:write(out/'donor-first-trace.json',dt)
        group=[]
        for c in CONDITIONS:
            r,t=simulate(seed,c,detailed=True,replay=dt['couplings'] if c=='Yoked' else None);rows.append(r);group.append(r)
            write(out/f'completions-{seed}-{c}.json',[e for e in t['events'] if e['action']=='complete'])
            if seed==seeds.start:write(out/f'trace-{c}.json',t)
            if c=='Yoked':assert t['couplings']==dt['couplings']
        for k in ('task_hash','eligible','primary_n','edge_updates','reserved_scan_slots'):assert len({r[k] for r in group})==1
        for k in group[0]:
            if k!='condition':assert group[0][k]==group[1][k],k
        assert all(r['prohibited_executions']==0 and r['agent_completions'][0]==0 for r in group+[dr])
        print(seed,flush=True)
    write(out/'rows.json',rows);write(out/'donors.json',donors)
    metrics=['primary_rate','completed','travel','collisions','wasted_travel','coupling_changes','agreement_records','window_entries_scanned','reserved_scan_slots','reliability_summaries','boundary_read_multiplications','boundary_deposit_multiplications','feedback_updates','relaxations']
    summary=dict(conditions={c:{m:statistics.mean(r[m] for r in rows if r['condition']==c) for m in metrics} for c in CONDITIONS},contrasts={kind:interval(differences(rows,kind)) for kind in ('primary','interaction','adaptive_vs_fixed')},source_hashes=sources())
    write(out/'summary.json',summary);verify();print(json.dumps(dict(phase=phase,recipient_episodes=len(rows),donor_episodes=len(donors),contrasts=summary['contrasts'],preserved=len(frozen['preserved'])),indent=2))
if __name__=='__main__':main()
