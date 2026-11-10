import importlib.util
from pathlib import Path
import random
import unittest
from medium import Medium
from study import NEIGHBORS,simulate
spec=importlib.util.spec_from_file_location('original',Path(__file__).resolve().parents[1]/'simulate.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

class MediumTests(unittest.TestCase):
    def test_local_feedback_and_direction(self):
        m=Medium(NEIGHBORS);m.step([.5]*24,False);eligibility=m.eligibility(3);before=dict(m.weights)
        m.feedback(3,eligibility,True)
        self.assertTrue(all(w>before[e] if 3 in e else w==before[e] for e,w in m.weights.items()))
        with self.assertRaises(ValueError):m.feedback(3,{(0,1):1},True)
    def test_failed_arrival_reduces_and_zero_activity_does_nothing(self):
        m=Medium(NEIGHBORS);before=dict(m.weights);m.feedback(0,{(0,1):0},False);self.assertEqual(before,m.weights)
        m.feedback(0,{(0,1):1},False);self.assertLess(m.weights[0,1],1)
    def test_bounds_and_conservative_mixing(self):
        rng=random.Random(84);m=Medium(NEIGHBORS)
        m.weights={e:rng.uniform(.1,1.9) for e in m.weights}
        for _ in range(50):
            x=[rng.random() for _ in range(24)];y=m.step(x,False)
            self.assertAlmostEqual(sum(y),.88*sum(x));self.assertTrue(all(0<=v<=1 for v in y))
        for _ in range(500):m.feedback(0,{(0,1):1},False)
        self.assertEqual(m.weights[0,1],.1)
        for _ in range(500):m.feedback(0,{(0,1):1},True)
        self.assertEqual(m.weights[0,1],1.9)
    def test_reset_and_relaxation(self):
        m=Medium(NEIGHBORS);m.feedback(0,{(0,1):1},True);w=m.weights[0,1]
        m.step([.5]*24,True);self.assertTrue(1<m.weights[0,1]<w)
        m.reset();self.assertTrue(all(v==1 for v in m.weights.values()));self.assertEqual(m.eligibility(0),{})
    def test_fixed_medium_matches_original(self):
        a,_=simulate(7000,'C');b,_=old.simulate(7000,'C',96)
        for k,v in b.items():self.assertEqual(a[k],v,k)
    def test_intervention_prefixes_and_actual_learning(self):
        d,td=simulate(7001,'D',detailed=True)
        f,tf=simulate(7001,'D-frozen',detailed=True)
        r,tr=simulate(7001,'D-reset',detailed=True)
        self.assertGreater(d['feedback_updates'],0);self.assertGreater(d['weight_max'],d['weight_min'])
        for category in ['events','snapshots']:
            self.assertEqual([e for e in td[category] if e['t']<1000],[e for e in tf[category] if e['t']<1000])
            self.assertEqual([e for e in td[category] if e['t']<2400],[e for e in tr[category] if e['t']<2400])
        self.assertEqual(d['primary_done'],r['primary_done'])
        self.assertEqual(f['relaxations'],48000)
        self.assertEqual(d['edge_updates'],288000);self.assertEqual(d['receipt_writes'],288000)
        self.assertEqual(d['prohibited_executions'],0)
        self.assertEqual(d['agent_completions'][0],0)
if __name__=='__main__':unittest.main()
