"""Portable, non-destructive reproduction of the released synthetic evidence.
Run --smoke for one held-out seed per simulation; --full for all retained rows.
Results are compared with the retained outputs; no files are overwritten.
"""
import argparse,hashlib,json,subprocess,sys,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SIMS=['baseline','adaptive-medium','remote-information','participant-authority','composite-reservations','reservation-replanning']
TESTS=['adaptive-medium','claim-specificity','remote-information','participant-authority','complementary-feasibility','attainable-service','reservation-lifecycle','composite-reservations','reservation-replanning','execution-delay']
def worker(name,full):
 p=ROOT if name=='baseline' else ROOT/name
 sys.path.insert(0,str(p))
 import importlib.util
 spec=importlib.util.spec_from_file_location('release_study',p/('simulate.py' if name=='baseline' else 'study.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 saved=json.loads((p/'evaluation'/('all-seeds.json' if name=='baseline' else 'rows.json')).read_text())
 if not full:saved=[r for r in saved if r['seed']==min(x['seed'] for x in saved)]
 donors={};count=0
 for row in saved:
  seed=row['seed']
  if name in ['composite-reservations','reservation-replanning']:
   ops,jobs=m.workload(seed)
   got=m.simulate(ops,jobs,row['policy']) if name=='composite-reservations' else m.simulate(ops,jobs,0 if row['policy']=='append' else 4)
   got=dict(seed=seed,policy=row['policy'],**got)
  else:
   kw={}
   if name=='baseline':kw['budget']=row['budget']
   if name=='participant-authority' and row['condition']=='Yoked':
    if seed not in donors:donors[seed]=m.simulate(seed+100000,'R1A1',detailed=True)[1]['couplings']
    kw['replay']=donors[seed]
   got=m.simulate(seed,row['condition'],**kw)[0]
  # JSON normalization handles tuples in schedules without changing numerical values.
  got=json.loads(json.dumps(got))
  assert got==row,(name,seed,{k:(row.get(k),got.get(k)) for k in set(row)|set(got) if row.get(k)!=got.get(k)})
  count+=1
 print(json.dumps({'study':name,'exact_rows':count,'mode':'full' if full else 'smoke'}),flush=True)
def main():
 a=argparse.ArgumentParser();a.add_argument('--full',action='store_true');a.add_argument('--smoke',action='store_true');a.add_argument('--worker',choices=SIMS);a.add_argument('--tests-only',action='store_true');a.add_argument('--finite-only',action='store_true');args=a.parse_args()
 if args.worker:return worker(args.worker,args.full)
 for d in ([] if args.finite_only else TESTS):subprocess.run([sys.executable,'-m','unittest','discover','-v'],cwd=ROOT/d,check=True)
 if args.tests_only:return
 for d in ([] if args.finite_only else SIMS):subprocess.run([sys.executable,__file__,'--worker',d,'--full' if args.full else '--smoke'],check=True)
 # Rebuild finite demonstrations and delay analyses in a disposable directory.
 # Retained dependencies are copied; each new freeze describes that copy.
 with tempfile.TemporaryDirectory(prefix='active-substrates-') as td:
  dst=Path(td)/'evidence';shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('__pycache__'))
  for d in ['complementary-feasibility','attainable-service','reservation-lifecycle','execution-delay','delay-feasibility']:
   p=dst/d
   if (p/'first-results').exists():shutil.rmtree(p/'first-results')
   if (p/'freeze.json').exists():(p/'freeze.json').unlink()
   if d in ['execution-delay','delay-feasibility']:
    subprocess.run([sys.executable,'run.py','freeze'],cwd=p,check=True,stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable,'run.py','run'],cwd=p,check=True,stdout=subprocess.DEVNULL)
   else:subprocess.run([sys.executable,'demo.py'],cwd=p,check=True,stdout=subprocess.DEVNULL)
   result='demonstrations.json' if d=='reservation-lifecycle' else 'summary.json'
   expected=json.loads((ROOT/d/'first-results'/result).read_text());got=json.loads((p/'first-results'/result).read_text());assert got==expected,d
   print(json.dumps({'study':d,'retained_summary_exact':True}),flush=True)
 print('PASS: retained evidence unchanged; selected reproduction comparisons exact.')
if __name__=='__main__':main()
