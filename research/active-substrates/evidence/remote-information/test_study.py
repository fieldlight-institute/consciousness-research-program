import unittest
from study import simulate, deliver, credit_weight, update_credit, common, expired

class RemoteTests(unittest.TestCase):
    def test_remote_commitment_and_stale_failure(self):
        job=dict(id=0,born=0,site=0,skill=2,deadline=30)
        positions=[23]*12; positions[1]=0; positions[2]=0
        result,trace=simulate(3000,'A-fixed',ticks=20,stream_override=[job],positions=positions,detailed=True)
        remote=[e for e in trace if e['action']=='claim' and e['sender'] is not None]
        self.assertTrue(remote)
        self.assertTrue(all(e['t']>=1 for e in remote))
        self.assertTrue(any(e['action']=='arrival' and e['remote'] and not e['success'] for e in trace))
        self.assertGreater(result['duplicate_arrivals'],0)

    def test_expiry_boundaries(self):
        p=dict(observed=10,job={"deadline":30})
        self.assertFalse(expired(p,17)); self.assertTrue(expired(p,18))
        p["job"]["deadline"]=12
        self.assertFalse(expired(p,12)); self.assertTrue(expired(p,13))

    def test_capacity_evicts_oldest(self):
        inbox={}
        for i in range(9): deliver(inbox,dict(observed=i,job={'id':i}))
        self.assertEqual(len(inbox),8); self.assertNotIn(0,inbox)

    def test_local_credit_only_on_remote_arrival(self):
        result,trace=simulate(3000,'A-credit',ticks=150,detailed=True)
        arrivals=[e for e in trace if e['action']=='arrival' and e['remote']]
        self.assertEqual(result['credit_updates'],len(arrivals))
        credit={}; self.assertEqual(credit_weight(credit,1,2),.75)
        update_credit(credit,1,2,False); self.assertEqual(credit_weight(credit,1,2),.6)
        self.assertEqual(credit_weight(credit,2,1),.75)

    def test_refusal_and_transmission_budget(self):
        jobs=[dict(id=i,born=i,site=0,skill=0,deadline=i+30) for i in range(10)]
        result,trace=simulate(3001,'A-credit',ticks=30,stream_override=jobs,positions=[0]*12,detailed=True)
        self.assertGreater(result['refusals'],0)
        self.assertFalse(any(e['action']=='claim' and e['agent']==0 for e in trace))
        self.assertTrue(all(len(e['packets'])<=4 for e in trace if e['action']=='send'))
        self.assertEqual(result['payload_scalars'],result['transmissions']*8)
        self.assertEqual(result['prohibited_executions'],0)

    def test_policy_reset_preserves_prereset_trajectory(self):
        a,ta=simulate(3002,'A-credit',ticks=2401,detailed=True)
        b,tb=simulate(3002,'A-credit-reset',ticks=2401,detailed=True)
        self.assertEqual([e for e in ta if e['t']<2400],[e for e in tb if e['t']<2400])
        self.assertTrue(any(e['action']=='credit_reset' for e in tb))

    def test_local_control_matches_preceding_mechanism(self):
        a,_=simulate(3003,'local')
        b,_=common.simulate(3003,'skill-site-veto')
        for field in ['task_hash','completed','primary_n','primary_done','primary_rate','replacement_rate','travel','collisions','wasted_travel']:
            self.assertEqual(a[field],b[field],field)

if __name__=='__main__': unittest.main()
