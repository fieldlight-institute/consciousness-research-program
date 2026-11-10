import unittest
from copy import deepcopy
from lifecycle import Agent,Operation,propose,apply,validate_snapshot

def fixture(early=False):
 a=[Agent('a',0,{'X':1}),Agent('b',0,{'X':1})]
 ops=[Operation('p',0,0,9,(('X',2),)),Operation('q',1,0,9,(('X',1),)),Operation('r',2,0,9,(('X',1),)),Operation('s',1,0,9,(('X',1),),('q',))]
 jobs={o.id:[o.id] for o in ops}
 def e(oid,agent,origin,depart,start,finish):return dict(operation=oid,crew=[agent],committed=0,origin=origin,depart=depart,start=start,finish=finish)
 events=[e('p','a',0,0,0,2),e('q','a',0,3,4,5),e('r','a',1,5,6,7),e('s','b',0,1 if early else 4,6,7)]
 return a,ops,jobs,events
class Tests(unittest.TestCase):
 def test_closure_and_completed_preservation(self):
  a,o,j,e=fixture();before=deepcopy(e);p=propose(a,o,j,e,['q'],2)
  self.assertEqual(p['withdrawals'],['q','r','s']);self.assertEqual(p['affected_agents'],['a','b'])
  r=apply(a,o,j,e,p,['a','b'],2);self.assertEqual(r['reservations'],[e[0]]);self.assertEqual(e,before);self.assertEqual(r['audit']['withdrawal_units'],3)
 def test_missing_authority_atomic(self):
  a,o,j,e=fixture();before=deepcopy(e);p=propose(a,o,j,e,['q'],2)
  with self.assertRaisesRegex(ValueError,'authority'):apply(a,o,j,e,p,['a'],2)
  self.assertEqual(e,before)
 def test_travel_not_work_start_is_boundary(self):
  a,o,j,e=fixture(True);p=propose(a,o,j,e,['q'],2)
  self.assertEqual(p['blockers'],['s'])
  with self.assertRaisesRegex(ValueError,'departed'):apply(a,o,j,e,p,['a','b'],2)
 def test_exact_departure_immutable(self):
  a,o,j,e=fixture();p=propose(a,o,j,e,['q'],3);self.assertIn('q',p['blockers'])
 def test_stale_time_state_and_tampering(self):
  a,o,j,e=fixture();p=propose(a,o,j,e,['q'],2)
  with self.assertRaisesRegex(ValueError,'stale'):apply(a,o,j,e,p,['a','b'],3)
  changed=deepcopy(e);changed[-1]['depart']=3
  with self.assertRaisesRegex(ValueError,'stale'):apply(a,o,j,changed,p,['a','b'],2)
  p['withdrawals']=['q']
  with self.assertRaisesRegex(ValueError,'altered'):apply(a,o,j,e,p,['a','b'],2)
 def test_invalid_physical_state(self):
  a,o,j,e=fixture();e[1]['origin']=9
  with self.assertRaisesRegex(ValueError,'origin'):validate_snapshot(a,o,j,e,2)
  a,o,j,e=fixture();e[1]['committed']=1
  with self.assertRaisesRegex(ValueError,'predecessor'):validate_snapshot(a,o,j,e,2)
 def test_result_does_not_alias_input(self):
  a,o,j,e=fixture();p=propose(a,o,j,e,['r'],2);r=apply(a,o,j,e,p,['a'],2)
  r['reservations'][0]['crew'][0]='changed';self.assertEqual(e[0]['crew'],['a'])
if __name__=='__main__':unittest.main()
