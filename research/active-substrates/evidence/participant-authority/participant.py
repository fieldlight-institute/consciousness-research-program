"""Local observations and independently enforced boundary adjustment authority."""
from collections import deque
from math import sqrt,isfinite
CONDITIONS=('R0A0','R1A0','R0A1','R1A1','Yoked')
class Participant:
    def __init__(self):
        self.history=deque(maxlen=32);self.g=1.;self.pending=None
        self.recorded=0;self.scanned=0;self.allowance=0;self.summaries=0;self.writes=0
    def commit(self,raw):self.pending=raw
    def arrive(self,success):
        if self.pending is not None:
            self.history.append(int((self.pending<.25)==bool(success)));self.recorded+=1
        self.pending=None
    def reset_history(self):self.history.clear();self.pending=None
    def estimate(self):
        n=len(self.history);hits=sum(self.history);a=1+hits;b=1+n-hits
        return a/(a+b),sqrt(a*b/((a+b)**2*(a+b+1))),n
    def revise(self,t,agent,condition,replay=None):
        if condition not in CONDITIONS:raise ValueError('condition')
        mean,sd,n=self.estimate();self.scanned+=n;self.allowance+=32;self.summaries+=1
        target=1. if n<8 else (1.5 if mean>.6 else .5 if mean<.4 else 1.)
        comparator=1.5 if ((t//25+agent)//10)%2==0 else .5
        old=self.g
        if condition=='R1A1':self.g+=max(-.1,min(.1,target-self.g))
        elif condition=='R0A1':self.g+=max(-.1,min(.1,comparator-self.g))
        elif condition=='Yoked':
            if replay is None or not isfinite(replay) or not .25<=replay<=1.75:raise ValueError('invalid replay')
            self.g=replay
        self.g=max(.25,min(1.75,self.g));self.writes+=int(self.g!=old)
        return dict(mean=mean,sd=sd,n=n,g=self.g)
