import unittest
from study import Agent,Operation,simulate,workload,reference
class Tests(unittest.TestCase):
 def test_baseline_reproduces_preserved_policy(self):
  for seed in (61,62,63):
   o,j=workload(seed);a=simulate(o,j);b=reference.simulate(o,j,'whole')
   for key in ('completed','partial','work_occupancy_ticks','travel_ticks','assignment_checks'):self.assertEqual(a[key],b[key])
   self.assertEqual([{k:e[k] for k in ('operation','crew','start','finish')} for e in a['events']],b['events'])
 def test_revision_preserves_active_work_and_improves(self):
  a=[Agent('a',0,{'X':1,'Y':1})]
  o=[Operation('old-0',0,0,6,(('X',2),)),Operation('old-1',0,0,6,(('Y',2),),('old-0',)),Operation('urgent',0,1,3,(('X',1),))];j={'old':['old-0','old-1'],'urgent':['urgent']}
  fixed=simulate(o,j,0,a);revised=simulate(o,j,4,a)
  self.assertEqual((fixed['completed'],revised['completed']),(1,2));self.assertEqual(revised['cancellation_units'],1)
  self.assertEqual(fixed['events'][0],revised['events'][0])
 def test_no_unreleased_information(self):
  o,j=workload(65);r=simulate(o,j,4)
  for snapshot in r['traces']:
   for e in snapshot['after']:self.assertLessEqual(next(x.release for x in o if x.id==e['operation']),snapshot['t'])
  early=[Operation('e',0,0,6,(('X',2),))];late=Operation('l',1,3,8,(('Y',1),))
  a=simulate(early,{'e':['e']},4);b=simulate(early+[late],{'e':['e'],'l':['l']},4)
  self.assertEqual([x for x in a['traces'] if x['t']<3],[x for x in b['traces'] if x['t']<3])
 def test_budget_and_physical_preservation(self):
  for seed in range(70,80):
   o,j=workload(seed);r=simulate(o,j,4);self.assertLessEqual(r['cancellation_units'],4)
   for snapshot in r['traces']:
    for e in snapshot['before']:
     if e['depart']<=snapshot['t']:self.assertIn(e,snapshot['after'])
if __name__=='__main__':unittest.main()
