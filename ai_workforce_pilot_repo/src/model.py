"""Aggregation, workforce scenarios, 3-year INR model, budget optimisation, robustness.
Every financial input below is an ASSUMPTION (no source in the pilot data) unless noted; see docs/assumptions.md."""
import numpy as np, pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds
DIMS = ["exposure","automation","augmentation","human_judgment","feasibility"]
ROLES = {  # N = headcount of a HYPOTHETICAL 10,000-person IT-BPM client (assumed); ctc in INR/yr (assumed)
 "15-1252.00": dict(key="dev", label="Software Developers", N=3000, ctc=1_200_000, target_ctc=1_800_000, isco="2512"),
 "15-1253.00": dict(key="qa",  label="QA Analysts & Testers", N=1200, ctc=700_000, target_ctc=1_200_000, isco="2519"),
 "43-4051.00": dict(key="csr", label="Customer Service Reps", N=3000, ctc=350_000, target_ctc=700_000, isco="4222")}
CFG = dict(scenario="base", discount=0.12, realisation=0.35, monet=0.6, completion=0.85, success=0.70, train_mult=1.0,
 lag=[0.6,0.9,1.0], attrition=0.15, budget=250_000_000, n_mult=1.0, reskill_mult=1.35, reskill_premium=0.05,
 train_cap=2500, b_cap=0.06, c_cap=0.25, min_cov=0.05)
ADOPT = {"conservative":[.10,.25,.40], "base":[.20,.45,.65], "accelerated":[.35,.65,.85]}
KS = ["D","A","B","C"]  # Redesign&monitor, Reskill, Redeploy, Hire AI-enablement specialists
KNAME = dict(D="Redesign & monitor", A="Reskill", B="Redeploy", C="Hire enablement specialists")

# ---------- aggregation ----------
def weights(g, scheme="importance"):
    w = np.ones(len(g)) if scheme=="equal" else g["task_importance"].astype(float).fillna(0).to_numpy()
    if w.sum()==0: w = np.ones(len(g))
    return w/w.sum()
def wstats(x, w):
    m = float(np.sum(w*x)); return m, float(np.sqrt(np.sum(w*(x-m)**2)))
def ilo_gradient(mu, sd):
    """ILO WP140 Table 5 rules; 0 = minimal/not exposed."""
    if mu>=0.6 and mu-sd>=0.5: return 4
    if 0.5<=mu<0.6 and mu+sd>=0.5: return 3
    if 0.4<=mu<0.5 and mu+sd>=0.5: return 2
    if mu<0.4 and mu+sd>=0.5: return 1
    if mu>=0.6: return 3   # extension: Table 5 leaves mu>=0.6 with mu-sd<0.5 undefined; treated as high-variability Gradient 3
    return 0
def aggregate(df, scheme="importance"):
    rows = []
    for soc, g in df.groupby("onet_soc", sort=False):
        w = weights(g, scheme); r = dict(onet_soc=soc, occupation=ROLES[soc]["label"], n_tasks=len(g))
        for d in DIMS: r[d], r[d+"_sd"] = wstats(g[d].to_numpy(float)/4, w)
        a = (0.5*g.automation+0.5*g.augmentation).to_numpy(float)/4*g.feasibility.to_numpy(float)/4
        r["assistable_share"] = float(np.sum(w*a))
        r["share_high_exposure"] = float(np.sum(w*(g.exposure>=3)))
        r["share_automatable"] = float(np.sum(w*(g.automation>=3)))
        r["share_human_led"] = float(np.sum(w*((g.automation<=1)&(g.human_judgment>=3))))
        r["gradient_auto"] = ilo_gradient(r["automation"], r["automation_sd"])
        r["gradient_exposure"] = ilo_gradient(r["exposure"], r["exposure_sd"])
        rows.append(r)
    return pd.DataFrame(rows)

# ---------- unit economics (INR per employee in scope, 3 years) ----------
def unit(soc, k, agg, c):
    R, ctc = ROLES[soc], ROLES[soc]["ctc"]; s = float(agg.loc[agg.onet_soc==soc,"assistable_share"].iloc[0])
    u = s*c["realisation"]; ad = np.array(ADOPT[c["scenario"]]); bau = 0.25*ad; lag = np.array(c["lag"]); t = np.arange(1,4)
    surv = (1-c["attrition"])**t; hr = ctc/2000
    tool = np.array([12_000.]*3); chg = np.array([6_000.,0,0]); mon = np.array([2_000.]*3)
    costD = tool+mon+chg
    base = ctc*u*(ad-bau)*c["monet"]*lag          # D benefit
    cost = costD.copy(); ben = base.copy()
    if k=="A":
        course = np.array([45_000*c["train_mult"]*1.2 + 3_000 + 100*hr*c["train_mult"],0,0])
        ad2 = np.minimum(ad*1.15,.95); inc = ctc*u*(ad2*c["reskill_mult"]-ad)*c["monet"]*lag
        prem = np.array([0, ctc*c["reskill_premium"], ctc*c["reskill_premium"]])
        comp = c["completion"]; cost = costD+course; ben = base+comp*(inc+prem)*surv
    elif k=="B":
        cost = np.array([30_000*c["train_mult"]*1.15 + 0.3*ctc*2/12 + 0.0,0,0])
        gain = 0.25*R["target_ctc"] + R["target_ctc"]/12   # avoided external hire + vacancy cost
        ben = np.array([0, c["success"]*gain*surv[1], 0.])
    elif k=="C":
        spec = 2_000_000; cost = costD + np.array([spec/40 + .25*spec/40, spec/40, spec/40])
        ben = ctc*u*(np.minimum(ad*1.25,.95)-bau)*c["monet"]*lag
    df = 1/(1+c["discount"])**t
    return dict(cost=cost.sum(), npv=float(((ben-cost)*df).sum()), pv_cost=float((cost*df).sum()), pv_ben=float((ben*df).sum()),
                cost_y=cost, ben_y=ben)

def table(agg, c):
    rows = []
    for soc in ROLES:
        for k in KS:
            x = unit(soc,k,agg,c); rows.append(dict(onet_soc=soc, role=ROLES[soc]["label"], k=k, **x))
    return pd.DataFrame(rows)

# ---------- optimisation ----------
def optimise(agg, c, force=None):
    U = table(agg,c); socs = list(ROLES); n = len(socs)*len(KS); N = {s:int(ROLES[s]["N"]*c["n_mult"]) for s in socs}
    idx = lambda i,j: i*len(KS)+j
    npv = U.npv.to_numpy(); cost = U.cost.to_numpy()
    rows, lo, hi = [], [], []
    def con(coefs, l, h): v = np.zeros(n); [v.__setitem__(i,x) for i,x in coefs]; rows.append(v); lo.append(l); hi.append(h)
    for i,s in enumerate(socs):
        con([(idx(i,j),1) for j in range(4)], c["min_cov"]*N[s], N[s])               # coverage floor and headcount cap
        con([(idx(i,2),1)], 0, c["b_cap"]*N[s]); con([(idx(i,3),1)], 0, c["c_cap"]*N[s])
    con([(i,cost[i]) for i in range(n)], 0, c["budget"])
    con([(idx(i,j),1) for i in range(len(socs)) for j in (1,2)], 0, c["train_cap"])
    res = milp(-npv, constraints=LinearConstraint(np.array(rows),lo,hi), integrality=np.ones(n), bounds=Bounds(0,[N[socs[i//4]] for i in range(n)]))
    x = np.round(res.x).astype(int) if res.success else np.zeros(n,int)
    return U, x, res.success

def evaluate(U, x):
    cost_y = sum(x[i]*U.cost_y.iloc[i] for i in range(len(U))); ben_y = sum(x[i]*U.ben_y.iloc[i] for i in range(len(U)))
    return dict(npv=float((U.npv.to_numpy()*x).sum()), cost=float((U.cost.to_numpy()*x).sum()),
                pv_cost=float((U.pv_cost.to_numpy()*x).sum()), pv_ben=float((U.pv_ben.to_numpy()*x).sum()),
                net_y=(ben_y-cost_y), employees=int(x.sum()))

def strategies(agg, c):
    U, xo, ok = optimise(agg,c); n=len(U); out = {"Optimised portfolio": xo}
    N = {s:int(ROLES[s]["N"]*c["n_mult"]) for s in ROLES}; socs=list(ROLES)
    xe = np.zeros(n,int)                                           # equal budget per role, best ROI of D/A
    for i,s in enumerate(socs):
        sub = U[(U.onet_soc==s)&U.k.isin(["D","A"])]; best = (sub.npv/sub.cost).idxmax()
        xe[best] = min(N[s], int(c["budget"]/3/U.cost[best]))
    out["Equal budget per role"] = xe
    xh = np.zeros(n,int); left = c["budget"]; cap = c["train_cap"]  # highest exposure first, reskill
    for s in agg.sort_values("exposure",ascending=False).onet_soc:
        i = [j for j in range(n) if U.onet_soc[j]==s and U.k[j]=="A"][0]
        m = min(N[s], cap, int(left/U.cost[i])); xh[i]=m; left-=m*U.cost[i]; cap-=m
    out["Highest-exposure-first (reskill)"] = xh
    out["Business as usual"] = np.zeros(n,int)
    return U, out

def robustness(agg, c):
    rows = []; U0, x0, _ = optimise(agg,c); base = evaluate(U0,x0)["npv"]
    cases = [("AI adoption","scenario","conservative","accelerated"),("Training completion","completion",0.6,0.95),
     ("Internal transition success","success",0.5,0.85),("Productivity realisation","realisation",0.2,0.5),
     ("Training cost","train_mult",1.3,0.7),("Time to benefit (yr-1 realisation)","lag",[.3,.7,1.],[.9,1.,1.]),
     ("Annual attrition","attrition",0.25,0.10),("Discount rate","discount",0.14,0.10),
     ("Workforce size","n_mult",0.8,1.2),("Reskill productivity multiplier","reskill_mult",1.2,1.7),("Budget","budget",150_000_000,400_000_000)]
    for name,key,lo,hi in cases:
        r = {}
        for tag,v in (("low",lo),("high",hi)):
            c2 = dict(c); c2[key]=v; U,x,_ = optimise(agg,c2); r[tag]=evaluate(U,x)["npv"]
            r[tag+"_reskilled"] = int(sum(x[i] for i in range(len(U)) if U.k[i]=="A"))
        rows.append(dict(driver=name, npv_low=r["low"], npv_high=r["high"], reskilled_low=r["low_reskilled"], reskilled_high=r["high_reskilled"], base_npv=base))
    return pd.DataFrame(rows)
