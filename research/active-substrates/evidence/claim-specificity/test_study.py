import unittest
from study import claim_blocks, simulate, CONDITIONS

class ClaimTests(unittest.TestCase):
    def test_specificity(self):
        record = dict(owner=0, site=4, skill=1, job=7, expiry=10)
        same = dict(id=7, site=4, skill=1)
        other_job = dict(id=8, site=4, skill=1)
        other_skill = dict(id=9, site=4, skill=2)
        remote = dict(id=10, site=5, skill=1)
        for condition in CONDITIONS:
            self.assertEqual(claim_blocks([record], same, condition), condition != 'no-veto')
            self.assertFalse(claim_blocks([record], remote, condition))
        self.assertTrue(claim_blocks([record], other_skill, 'site-veto'))
        self.assertFalse(claim_blocks([record], other_skill, 'skill-site-veto'))
        self.assertTrue(claim_blocks([record], other_job, 'skill-site-veto'))
        self.assertFalse(claim_blocks([record], other_job, 'job-veto'))

    def test_simultaneous_claims_still_possible(self):
        jobs = [dict(id=0,born=0,site=0,skill=1,deadline=20)]
        for condition in CONDITIONS:
            row, trace = simulate(200, condition, detailed=True, stream_override=jobs, positions=[0]*12,ticks=10)
            claims = [e for e in trace['events'] if e['action']=='claim']
            self.assertEqual(len(claims), 3)
            self.assertTrue(all(e['t']==0 for e in claims))
            self.assertEqual(row['completed'],1)
            self.assertEqual(row['duplicate_arrivals'],2)
            self.assertEqual(row['expired_arrivals'],0)

    def test_refusal_and_pairing(self):
        rows = [simulate(200,c,ticks=180)[0] for c in CONDITIONS]
        self.assertEqual(len({r['task_hash'] for r in rows}),1)
        self.assertEqual(len({r['eligible'] for r in rows}),1)
        for r in rows:
            self.assertEqual(r['prohibited_executions'],0)
            self.assertEqual(r['agent_completions'][0],0)
            self.assertEqual(r['collisions'],r['duplicate_arrivals']+r['expired_arrivals'])
        self.assertEqual(simulate(200,'job-veto',ticks=180)[0],rows[-1])

    def test_visible_record_can_defer_a_later_claim(self):
        # Skill-1 agents start two steps apart: distant agent's cost keeps its
        # record alive when another agent first becomes able to see the job.
        jobs = [dict(id=0,born=0,site=0,skill=1,deadline=20)]
        pos=[23]*12
        pos[1]=2
        pos[5]=3
        pos[9]=23
        baseline, bt=simulate(199,'no-veto',True,jobs,pos,ticks=20)
        exact, et=simulate(199,'job-veto',True,jobs,pos,ticks=20)
        self.assertGreater(baseline['duplicate_arrivals'],exact['duplicate_arrivals'])
        self.assertGreater(exact['deferred_decisions'],0)

if __name__=='__main__': unittest.main()
