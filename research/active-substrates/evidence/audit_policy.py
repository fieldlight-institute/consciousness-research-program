import argparse,importlib.util,json,tempfile
from pathlib import Path
root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
assert not args.output.exists(), 'Refuse to overwrite an existing audit'
temporary=tempfile.TemporaryDirectory()
s=(root/'simulate.py').read_text()
s=s.replace('    events = []','    audit = dict(candidate_decisions=0,single_candidate=0,single_site=0,ranking_changed=0,duplicate_arrivals=0,expired_arrivals=0)\n    events = []',1)
s=s.replace("                counters['collisions'] += 1", "                counters['collisions'] += 1\n                audit['duplicate_arrivals' if job_id in completed else 'expired_arrivals'] += 1")
s=s.replace('            if choices:', '''            if choices:
                audit['candidate_decisions'] += 1
                audit['single_candidate'] += int(len(choices)==1)
                audit['single_site'] += int(len({c[3]['site'] for c in choices})==1)
                original_choice=max(choices,key=lambda c:c[:3])[3]['id']
                unpenalized=max(choices,key=lambda c:(1/(1+c[5]+a['cost']),c[1],c[2]))[3]['id']
                audit['ranking_changed'] += int(original_choice != unpenalized)''')
s=s.replace('    return result, dict(', "    result['audit'] = audit\n    return result, dict(")
path=Path(temporary.name)/'instrumented_original.py';path.write_text(s)
spec=importlib.util.spec_from_file_location('instrumented_original',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=json.loads((root/'pilot/all-seeds.json').read_text())
rows=[]
for seed in range(10):
 for c in ['B','C','C-no-propagation']:
  row,_=m.simulate(seed,c,96)
  old=next(r for r in original if r['seed']==seed and r['condition']==c and r['budget']==96)
  assert all(row[k]==v for k,v in old.items()),(seed,c)
  rows.append(dict(seed=seed,condition=c,**row['audit']))
summary={}
for c in ['B','C','C-no-propagation']:
 rs=[r for r in rows if r['condition']==c]
 sums={k:sum(r[k] for r in rs) for k in rs[0] if k not in ['seed','condition']}
 summary[c]=dict(**sums,single_candidate_fraction=sums['single_candidate']/sums['candidate_decisions'],single_site_fraction=sums['single_site']/sums['candidate_decisions'],ranking_changed_fraction=sums['ranking_changed']/sums['candidate_decisions'])
args.output.write_text(json.dumps(dict(scope='Existing pilot seeds 0-9, budget 96. All original output fields match preserved rows exactly; diagnostics only.',rows=rows,summary=summary),indent=2))
print(json.dumps(summary,indent=2))

temporary.cleanup()
