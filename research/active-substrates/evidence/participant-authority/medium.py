"""Local symmetric conductance and receipt state; no task or reward oracle."""
class Medium:
    def __init__(self,neighbors):
        self.n=len(neighbors)
        self.edges=[(i,j) for i in range(self.n) for j in neighbors[i] if i<j]
        self.weights={e:1. for e in self.edges}
        self.receipts=[{} for _ in range(self.n)]
        self.feedback_updates=0; self.relaxations=0; self.receipt_writes=0
    def reset(self):
        self.weights={e:1. for e in self.edges}; self.receipts=[{} for _ in range(self.n)]
    def eligibility(self,site): return dict(self.receipts[site])
    def feedback(self,site,eligibility,success):
        if any(site not in edge or edge not in self.weights for edge in eligibility): raise ValueError('nonlocal eligibility')
        total=sum(eligibility.values())
        if total<=0:return
        for edge,value in eligibility.items():
            self.weights[edge]=max(.1,min(1.9,self.weights[edge]+.02*(1 if success else -1)*value/total))
            self.feedback_updates+=1
    def step(self,field,learning):
        if learning:
            for edge,w in self.weights.items():
                self.weights[edge]=w+.001*(1-w);self.relaxations+=1
        old=field[:];new=[.88*x for x in old]
        for (i,j),w in self.weights.items():
            delta=.04*w*(old[j]-old[i]);new[i]+=delta;new[j]-=delta
            self.receipts[i][i,j]=.04*w*old[j];self.receipts[j][i,j]=.04*w*old[i]
            self.receipt_writes+=2
        assert min(new)>=-1e-12 and max(new)<=1+1e-12
        return [max(0.,min(1.,x)) for x in new]
