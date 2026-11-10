import copy,unittest
from replay import replay

def fixture():
    agents=[dict(id=a,site=0,rates={'X':1},refused=[]) for a in ('a','b')]
    ops=[dict(id='x',site=0,release=0,deadline=2,demands=[['X',1]],predecessors=[]),dict(id='y',site=0,release=0,deadline=3,demands=[['X',1]],predecessors=['x'])]
    events=[dict(operation='x',crew=['a'],origin=0,committed=0,depart=0,start=0,finish=1),dict(operation='y',crew=['b'],origin=0,committed=0,depart=0,start=2,finish=3)]
    return dict(agents=agents,operations=ops,jobs={'job':['x','y']}),events

class ReplayTests(unittest.TestCase):
    def test_zero_and_deadline_equality(self):
        w,e=fixture();before=copy.deepcopy((w,e));r=replay(w,e,{'x':0,'y':0})
        self.assertEqual(r['events'],e);self.assertEqual(r['completed'],1);self.assertEqual((w,e),before)
    def test_dependency_delay_propagates_without_retroactive_departure(self):
        w,e=fixture();r=replay(w,e,{'x':1,'y':0})
        self.assertEqual(r['events'][1]['depart'],0);self.assertEqual(r['events'][1]['start'],3)
        self.assertEqual(r['events'][1]['finish'],4);self.assertEqual(r['completed'],0)
        self.assertEqual(r['late_operations'],['y'])
    def test_same_agent_delay_blocks_departure_and_travel(self):
        w,e=fixture();w['operations'][1]['site']=2;e[1].update(crew=['a'],depart=1,start=3,finish=4)
        w['operations'][1]['deadline']=5
        r=replay(w,e,{'x':1,'y':0});self.assertEqual(r['events'][1]['depart'],2)
        self.assertEqual(r['events'][1]['start'],4);self.assertEqual(r['completed'],1)
    def test_slack_absorbs_overrun(self):
        w,e=fixture();e[1].update(start=5,finish=6);w['operations'][1]['deadline']=6
        self.assertEqual(replay(w,e,{'x':1,'y':0})['events'][1],e[1])
    def test_missing_work_never_receives_whole_job_credit(self):
        w,e=fixture();self.assertEqual(replay(w,e[:1],{'x':0,'y':1})['completed'],0)
        with self.assertRaises(ValueError):replay(w,e[1:],{'x':0,'y':0})
    def test_invalid_inputs_and_overtime(self):
        w,e=fixture()
        for d in ({'x':0},{'x':-1,'y':0},{'x':True,'y':0}):
            with self.assertRaises(ValueError):replay(w,e,d)
        r=replay(w,e,{'x':20,'y':0});self.assertEqual(r['last_finish'],23)
        self.assertEqual(r['completed'],0)
if __name__=='__main__':unittest.main()
