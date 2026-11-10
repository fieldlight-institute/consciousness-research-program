import unittest,importlib.util
from pathlib import Path
from participant import Participant,CONDITIONS
from study import simulate
ROOT=Path(__file__).resolve().parent
class ParticipantTests(unittest.TestCase):
    def test_observation_window_and_uncertainty(self):
        p=Participant();self.assertEqual(p.estimate()[0],.5)
        p.arrive(True);self.assertEqual(p.recorded,0)
        for i in range(40):p.commit(.8);p.arrive(False)
        self.assertEqual(len(p.history),32);self.assertEqual(p.estimate()[0],33/34)
        self.assertGreater(p.estimate()[1],0)
        p.reset_history();self.assertEqual(len(p.history),0);self.assertIsNone(p.pending)
    def test_authority_enforced_and_local_direction(self):
        for c in CONDITIONS[:-1]:
            p=Participant()
            for _ in range(32):p.commit(.1);p.arrive(True)
            p.revise(0,0,c)
            self.assertAlmostEqual(p.g,1.1 if c in ('R0A1','R1A1') else 1.)
        p=Participant()
        for _ in range(32):p.commit(.1);p.arrive(False)
        for t in range(0,1000,25):p.revise(t,0,'R1A1')
        self.assertEqual(p.g,.5)
    def test_clock_and_yoke_independent_of_history(self):
        for c in ('R0A1','Yoked'):
            p,q=Participant(),Participant()
            p.history.extend([1]*32);q.history.extend([0]*32)
            for t in range(0,1000,25):
                p.revise(t,1,c,1.4);q.revise(t,1,c,1.4);self.assertEqual(p.g,q.g)
        with self.assertRaises(ValueError):Participant().revise(0,0,'Yoked',float('nan'))
    def test_original_adaptive_reproduction(self):
        spec=importlib.util.spec_from_file_location('oldstudy',ROOT.parent/'adaptive-medium/study.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
        a,ta=simulate(41,'R0A0',detailed=True);b,tb=old.simulate(41,'D',detailed=True)
        for k in b:
            if k!='condition':self.assertEqual(a[k],b[k],k)
        for k in tb:self.assertEqual(ta[k],tb[k],k)
    def test_factorial_negative_control_replay_and_refusal(self):
        a,ta=simulate(43,'R0A0',detailed=True);b,tb=simulate(43,'R1A0',detailed=True)
        for k in a:
            if k!='condition':self.assertEqual(a[k],b[k],k)
        self.assertEqual(ta,tb)
        donor,td=simulate(100043,'R1A1',detailed=True)
        y,ty=simulate(43,'Yoked',detailed=True,replay=td['couplings'])
        self.assertEqual(ty['couplings'],td['couplings'])
        for r in (a,b,donor,y):
            self.assertEqual(r['prohibited_executions'],0);self.assertEqual(r['agent_completions'][0],0)
            self.assertEqual(r['reserved_scan_slots'],r['reliability_summaries']*32)
            self.assertEqual(r['edge_updates'],288000)
        self.assertGreater(donor['coupling_changes'],0)
if __name__=='__main__':unittest.main()
