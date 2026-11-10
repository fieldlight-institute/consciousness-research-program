import unittest
from itertools import product
from oracle import Agent,Operation,solve,verify,capacity
S=[Agent('a',0,{'X':2}),Agent('b',0,{'Y':2})]
G=[Agent('a',0,{'X':1,'Y':1}),Agent('b',0,{'X':1,'Y':1})]
def seq(deadline):return [Operation('x',0,0,deadline,(('X',2),)),Operation('y',0,0,deadline,(('Y',2),),('x',))]
class OracleTests(unittest.TestCase):
    def test_matched_skill_vector_opposite_feasibility(self):
        self.assertEqual(capacity(S)['potential'],capacity(G)['potential'])
        self.assertNotEqual(capacity(S)['sum_individual_max_rates'],capacity(G)['sum_individual_max_rates'])
        self.assertEqual(solve(S,seq(2))['status'],'feasible');self.assertEqual(solve(G,seq(2))['status'],'infeasible')
        self.assertEqual(solve(S,seq(4),3)['status'],'infeasible');self.assertEqual(solve(G,seq(4),3)['status'],'feasible')
    def test_simultaneous_distinct_agents_and_held_duration(self):
        op=[Operation('xy',0,0,2,(('X',2),('Y',2)))]
        self.assertEqual(solve(G,op)['accounting']['work_occupancy_ticks'],4)
        self.assertEqual(solve(G[:1],op)['status'],'infeasible')
    def test_travel_release_and_refusal(self):
        o=[Operation('x',2,5,6,(('X',2),))]
        r=solve(S,o);self.assertEqual(r['witness'][0]['start'],5);self.assertEqual(r['accounting']['travel_ticks'],2)
        self.assertEqual(solve([Agent('a',0,{'X':2},('X',))],o)['status'],'infeasible')
    def test_individual_not_joint_feasibility(self):
        a=[Agent('a',0,{'X':1})];ops=[Operation(str(i),0,0,1,(('X',1),)) for i in range(2)]
        self.assertTrue(all(solve(a,[o])['status']=='feasible' for o in ops));self.assertEqual(solve(a,ops)['status'],'infeasible')
    def test_budget_and_invalid_input(self):
        self.assertEqual(solve(S,seq(4),node_limit=1)['status'],'unknown')
        with self.assertRaises(ValueError):solve(S,[Operation('x',0,0,3,(('X',1),),('x',))])
        with self.assertRaises(ValueError):solve(S,[Operation('x',0,0,3,(('X',0),))])
    def test_validator_rejects_bad_witness(self):
        events=solve(S,seq(4),1)['witness'];events[1]['start']-=1;events[1]['finish']-=1
        with self.assertRaises(ValueError):verify(S,seq(4),1,events)
        events=solve(G,[Operation('xy',0,0,3,(('X',2),('Y',2)))])['witness'];events[0]['crew']=['a','a']
        with self.assertRaises(ValueError):verify(G,[Operation('xy',0,0,3,(('X',2),('Y',2)))],0,events)
    def test_independent_tick_enumeration(self):
        # Independently enumerate all integer start times for two one-agent jobs.
        a=[Agent('a',0,{'X':1})]
        for xsite,ysite,release,deadline in product((0,1),(0,2),(0,1),range(2,6)):
            ops=[Operation('x',xsite,0,deadline,(('X',1),)),Operation('y',ysite,release,deadline,(('X',1),))]
            ends=[]
            for sx,sy in product(range(deadline),repeat=2):
                if sy<release:continue
                if sx+1<=sy and sx>=abs(xsite) and sy>=sx+1+abs(ysite-xsite):ends.append(max(sx,sy)+1)
                if sy+1<=sx and sy>=abs(ysite) and sx>=sy+1+abs(ysite-xsite):ends.append(max(sx,sy)+1)
            r=solve(a,ops);self.assertEqual(r['status']=='feasible',bool(ends))
            if ends:self.assertEqual(r['minimum_makespan'],min(ends))
            self.assertEqual(r['status'],solve(a,list(reversed(ops)))['status'])
if __name__=='__main__':unittest.main()
