"""Post-hoc instrumentation of one retained evaluation episode; never tunes policy."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
original=(ROOT/'study.py').read_text()
anchor="            if choices:\n                _,_,_,j,arrival,travel,sender=max(choices,key=lambda x:x[:3])"
replacement='''            if choices:
                selected=max(choices,key=lambda x:x[:3])
                fixed=max(choices,key=lambda x:((.75 if x[6] is not None else 1)/(1+x[5]+a['cost']),x[1],x[2]))
                event(t,'credit_opportunity',count=len(choices),remote_count=sum(x[6] is not None for x in choices),
                      changed_rank=selected[3]['id']!=fixed[3]['id'],chosen_remote=selected[6] is not None)
                _,_,_,j,arrival,travel,sender=selected'''
assert original.count(anchor)==1
instrumented=original.replace(anchor,replacement)
namespace={'__file__':str(ROOT/'study.py'),'__name__':'instrumented'}
exec(compile(instrumented,str(ROOT/'study.py'),'exec'),namespace)
result,trace=namespace['simulate'](4000,'A-credit',detailed=True)
retained=next(r for r in json.loads((ROOT/'evaluation/rows.json').read_text()) if r['seed']==4000 and r['condition']=='A-credit')
assert result==retained, 'instrumentation changed outcome'
events=[e for e in trace if e['action']=='credit_opportunity']
with_remote=[e for e in events if e['remote_count']]
report=dict(post_hoc=True,seed=4000,condition='A-credit',matches_every_retained_result_field=True,
            candidate_decisions=len(events),decisions_with_remote_option=len(with_remote),
            remote_option_only_one_candidate=sum(e['count']==1 for e in with_remote),
            ranking_changed_against_fixed_weight=sum(e['changed_rank'] for e in with_remote),
            source_sha256=hashlib.sha256(original.encode()).hexdigest(),instrumented_sha256=hashlib.sha256(instrumented.encode()).hexdigest(),
            interpretation='Diagnostic of this one trajectory, not a new outcome comparison. Positive weights cannot veto a lone feasible report.')
with (ROOT/'credit-opportunity-audit.json').open('x') as f: json.dump(report,f,indent=2); f.write('\n')
print(json.dumps(report,indent=2))
