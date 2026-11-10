import unittest
from study import Agent,Operation,simulate,workload,TEAM
from service import maximize_service
class Tests(unittest.TestCase):
 def test_atomic_failed_plan(self):
  a=[Agent('a',0,{'X':1,'Y':1})];ops=[Operation('x',0,0,1,(('X',1),)),Operation('y',0,0,1,(('Y',1),),('x',))];jobs={'j':['x','y']}
  stage=simulate(ops,jobs,'stage',a);whole=simulate(ops,jobs,'whole',a)
  self.assertEqual(stage['partial'],1);self.assertEqual(whole['events'],[]);self.assertEqual(whole['completed'],0)
 def test_no_future_job_effect(self):
  early=[Operation('e',0,0,4,(('X',1),))];late=[Operation('l',2,3,7,(('Y',2),))]
  for policy in ('stage','whole'):
   before=simulate(early,{'e':['e']},policy);after=simulate(early+late,{'e':['e'],'l':['l']},policy)
   self.assertEqual(before['decisions'],[e for e in after['decisions'] if e['t']<3])
   self.assertEqual(before['events'],[e for e in after['events'] if e['operation']=='e'])
 def test_refusal(self):
  a=[Agent('a',0,{'X':1},('X',))];o=[Operation('x',0,0,3,(('X',1),))]
  for p in ('stage','whole'):self.assertEqual(simulate(o,{'j':['x']},p,a)['completed'],0)
 def test_witnesses_and_oracle_bound(self):
  for seed in range(31,37):
   ops,jobs=workload(seed);bound=maximize_service(TEAM,ops,jobs,lag=1)
   for p in ('stage','whole'):
    r=simulate(ops,jobs,p);self.assertLessEqual(r['completed'],bound['upper'])
    if p=='whole':self.assertEqual(r['partial'],0)
if __name__=='__main__':unittest.main()
