import unittest
from itertools import product,combinations
from service import Agent,Operation,maximize_service,score_schedule
A=[Agent('a',0,{'X':1,'Y':1})]
def singles(durations,deadline):
    ops=[Operation(str(i),0,0,deadline,(('X',d),)) for i,d in enumerate(durations)]
    return ops,{str(i):[str(i)] for i in range(len(ops))}
class ServiceTests(unittest.TestCase):
    def test_conflicting_jobs(self):
        ops,jobs=singles([1,1],1);r=maximize_service(A,ops,jobs)
        self.assertEqual((r['status'],r['lower'],r['upper']),('exact',1,1))
    def test_partial_has_no_credit(self):
        ops=[Operation('x',0,0,1,(('X',1),)),Operation('y',0,0,1,(('Y',1),),('x',))];jobs={'whole':['x','y']}
        self.assertEqual(maximize_service(A,ops,jobs)['lower'],0)
        score=score_schedule(A,ops,jobs,[dict(operation='x',crew=['a'],start=0,finish=1)])
        self.assertEqual(score['service'],0);self.assertEqual(score['partial_jobs'],['whole'])
        with self.assertRaises(ValueError):score_schedule(A,ops,jobs,[dict(operation='y',crew=['a'],start=0,finish=1)])
    def test_cross_job_closure_and_automatic_credit(self):
        ops=[Operation('x',0,0,2,(('X',1),)),Operation('y',0,0,2,(('Y',1),),('x',))]
        r=maximize_service(A,ops,{'first':['x'],'second':['y']});self.assertEqual(r['lower'],2)
        self.assertEqual(len(r['witness']),2)
    def test_partial_prerequisite_job(self):
        ops=[Operation('a1',0,0,2,(('X',1),)),Operation('a2',0,0,2,(('Z',1),)),Operation('b',0,0,2,(('Y',1),),('a1',))]
        r=maximize_service(A,ops,{'A':['a1','a2'],'B':['b']})
        self.assertEqual(r['completed_jobs'],['B']);self.assertEqual(r['partial_jobs'],['A']);self.assertEqual(r['lower'],r['upper'])
    def test_incomplete_search_keeps_upper_bound(self):
        ops,jobs=singles([1,1],2);r=maximize_service(A,ops,jobs,node_limit=1)
        self.assertEqual((r['status'],r['lower'],r['upper']),('bounded',0,2))
        r=maximize_service(A,ops,jobs,node_limit=10,per_candidate_limit=2)
        self.assertEqual((r['status'],r['lower'],r['upper']),('bounded',1,2))
    def test_partition_and_witness_validation(self):
        ops,jobs=singles([1,1],2)
        with self.assertRaises(ValueError):maximize_service(A,ops,{'a':['0'],'b':['0','1']})
        with self.assertRaises(ValueError):score_schedule(A,ops,jobs,[dict(operation='0',crew=['a'],start=2,finish=3)])
    def test_independent_duration_optimum(self):
        for durations in product(range(1,4),repeat=3):
            for deadline in range(1,7):
                ops,jobs=singles(durations,deadline)
                expected=max([0]+[len(c) for size in range(1,4) for c in combinations(durations,size) if sum(c)<=deadline])
                r=maximize_service(A,ops,jobs)
                self.assertEqual((r['lower'],r['upper']),(expected,expected))
if __name__=='__main__':unittest.main()
