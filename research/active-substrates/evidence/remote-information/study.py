"""RI-01 synthetic addressed observations; see frozen SPECIFICATION.md."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('claim_study', Path(__file__).resolve().parents[1]/'claim-specificity/study.py')
common=importlib.util.module_from_spec(spec); spec.loader.exec_module(common)
base=common.base
CONDITIONS=['local','A-fixed','A-credit','A-credit-reset']


def credit_weight(credit, recipient, sender):
    successes, attempts=credit.get((recipient,sender),(0,0))
    return (3+successes)/(4+attempts)


def update_credit(credit, recipient, sender, success):
    s,n=credit.get((recipient,sender),(0,0))
    credit[recipient,sender]=(s+int(success),n+1)


def expired(packet, now):
    return now >= packet["observed"] + 8 or now > packet["job"]["deadline"]


def deliver(mailbox, packet):
    mailbox[packet['job']['id']]=packet
    if len(mailbox)>8:
        victim=min(mailbox, key=lambda k:(mailbox[k]['observed'],k))
        del mailbox[victim]
        return 1
    return 0


def simulate(seed, condition, *, ticks=3000, stream_override=None, positions=None, detailed=False):
    assert condition in CONDITIONS
    rng=base.random.Random(seed+90000)
    stream=base.task_stream(seed) if stream_override is None else stream_override
    births={}
    for j in stream: births.setdefault(j['born'],[]).append(j)
    agents=[dict(id=i,site=rng.randrange(base.N),skill=i%4,cost=1+i%3,active=True,busy=None,arrival=0) for i in range(base.AGENTS)]
    if positions is not None:
        for a,p in zip(agents,positions): a['site']=p
    active={}; done=set(); eligible=set(); primary=set(); replacement=set()
    mail=[{} for _ in agents]; pending=[]; board={}; credit={}; trace=[]
    c={k:0 for k in ['transmissions','deliveries','evictions','expired_reports','observation_scans','mailbox_scans',
        'board_reads','board_writes','board_comparisons','travel','wasted_travel','collisions','duplicate_arrivals',
        'expired_arrivals','remote_commitments','remote_successes','credit_updates','refusals','prohibited_executions',
        'cancelled_claims','vetoed_candidates','peak_credit_cells','peak_mailbox_entries']}
    def event(t,action,**kw):
        if detailed: trace.append(dict(t=t,action=action,**kw))
    for t in range(ticks):
        if t==1800:
            for a in agents[:3]:
                c['cancelled_claims']+=int(a['busy'] is not None)
                a['active']=False; a['busy']=None; board.pop(a['id'],None); mail[a['id']].clear()
        if t==2400 and condition=='A-credit-reset':
            credit.clear(); event(t,'credit_reset')
        for job in births.get(t,[]):
            active[job['id']]=job
            if any(a['active'] and a['skill']==job['skill'] and not(a['id']<4 and job['skill']==0) for a in agents):
                eligible.add(job['id'])
                if 1000<=t<1500: primary.add(job['id'])
                if 2400<=t<2900: replacement.add(job['id'])
        active={k:j for k,j in active.items() if j['deadline']>=t and k not in done}
        order=sorted(agents,key=lambda a:(a['id']-t)%base.AGENTS)
        for a in order:
            if not a['active'] or a['busy'] is None or a['arrival']>t: continue
            jid,target,travel,sender=a['busy']; a['site']=target
            success=jid in active and jid not in done
            if success:
                assert a['skill']==active[jid]['skill'] and not(a['id']<4 and a['skill']==0)
                done.add(jid)
                c['remote_successes']+=int(sender is not None)
            else:
                c['collisions']+=1; c['wasted_travel']+=travel
                c['duplicate_arrivals' if jid in done else 'expired_arrivals']+=1
            if sender is not None and condition in ('A-credit','A-credit-reset'):
                update_credit(credit,a['id'],sender,success); c['credit_updates']+=1
            event(t,'arrival',agent=a['id'],job=jid,remote=sender is not None,success=success)
            a['busy']=None
        for p in pending:
            if agents[p['recipient']]['active']:
                c['deliveries']+=1; c['evictions']+=deliver(mail[p['recipient']],p)
        pending=[]
        for inbox in mail:
            for jid in list(inbox):
                c['mailbox_scans']+=1
                if expired(inbox[jid], t):
                    del inbox[jid]; c['expired_reports']+=1
        board={i:r for i,r in board.items() if r['expiry']>t}
        snapshot=list(board.values()); deposits=[]; proposals={}
        for a in agents:
            if not a['active'] or a['busy'] is not None: continue
            visible=base.VISIBLE[a['site']]
            local={}
            for jid,j in active.items():
                c['observation_scans']+=1
                if j['site'] in visible and jid not in done: local[jid]=j
            # Local absence may clear stale mail; never consult completion truth for remote reports.
            for jid,p in list(mail[a['id']].items()):
                c['mailbox_scans']+=1
                if p['job']['site'] in visible and jid not in local: del mail[a['id']][jid]
            if condition!='local' and local:
                j=min(local.values(),key=lambda j:(j['deadline'],j['id']))
                recipients=[b['id'] for b in agents if b['id']!=a['id'] and b['skill']==j['skill'] and not(b['id']<4 and j['skill']==0)]
                # Static capability directory deliberately does not inspect active/busy/site state.
                if recipients:
                    receiver=recipients[(t+a['id']+j['id'])%len(recipients)]
                    proposals[a['id']]=dict(sender=a['id'],recipient=receiver,observed=t,job=dict(j))
            candidates={jid:(p['job'],p['sender']) for jid,p in mail[a['id']].items()}
            candidates.update({jid:(j,None) for jid,j in local.items()})
            records=[r for r in snapshot if r['site'] in visible]; c['board_reads']+=len(records)
            choices=[]
            for jid,(j,sender) in candidates.items():
                if j['skill']!=a['skill']: continue
                if a['id']<4 and j['skill']==0:
                    c['refusals']+=1; continue
                travel=base.distance(a['site'],j['site']); arrival=t+travel+a['cost']
                if arrival>j['deadline']: continue
                c['board_comparisons']+=len(records)
                if common.claim_blocks(records,j,'skill-site-veto'):
                    c['vetoed_candidates']+=1; continue
                weight=1 if sender is None else (credit_weight(credit,a['id'],sender) if condition in ('A-credit','A-credit-reset') else .75)
                choices.append((weight/(1+travel+a['cost']),-j['deadline'],-jid,j,arrival,travel,sender))
            if choices:
                _,_,_,j,arrival,travel,sender=max(choices,key=lambda x:x[:3])
                a['busy']=(j['id'],j['site'],travel,sender); a['arrival']=arrival; c['travel']+=travel
                c['remote_commitments']+=int(sender is not None)
                deposits.append(dict(owner=a['id'],site=j['site'],skill=j['skill'],job=j['id'],expiry=arrival))
                event(t,'claim',agent=a['id'],job=j['id'],sender=sender,arrival=arrival)
            elif t%5==a['id']%5:
                options=sorted(j for j in range(base.N) if base.distance(a['site'],j)==1)
                if options: a['site']=options[(seed+t+a['id'])%len(options)]; c['travel']+=1
        for r in deposits: board[r['owner']]=r; c['board_writes']+=1
        pending=[proposals[a['id']] for a in order if a['id'] in proposals][:4]
        c['transmissions']+=len(pending)
        c['peak_credit_cells']=max(c['peak_credit_cells'],len(credit))
        c['peak_mailbox_entries']=max(c['peak_mailbox_entries'],sum(map(len,mail)))
        assert len(pending)<=4 and all(len(m)<=8 for m in mail)
        event(t,'send',packets=pending)
    result=dict(seed=seed,condition=condition,task_hash=base.hash_json(stream),eligible=len(eligible),completed=len(done&eligible),
        primary_n=len(primary),primary_done=len(done&primary),primary_rate=len(done&primary)/max(1,len(primary)),
        replacement_n=len(replacement),replacement_done=len(done&replacement),replacement_rate=len(done&replacement)/max(1,len(replacement)),
        payload_scalars=8*c['transmissions'],board_scalar_reads=5*c['board_reads'],board_scalar_writes=5*c['board_writes'],**c)
    return result,trace
