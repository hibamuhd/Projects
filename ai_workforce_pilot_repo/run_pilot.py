import sys, json; sys.path.insert(0,"src")
import numpy as np, pandas as pd
import scoring, model as M
df = scoring.build(); df.to_csv("data/processed/scored_tasks.csv", index=False)
agg = M.aggregate(df); agg_eq = M.aggregate(df,"equal")
ilo = pd.read_csv("data/processed/ilo_wp140_tableA1_isco08.csv", dtype={"isco08_code":str})
agg["isco08"] = agg.onet_soc.map(lambda s: M.ROLES[s]["isco"])
agg = agg.merge(ilo[["isco08_code","mean_score","sd_score","gradient"]].rename(columns={"isco08_code":"isco08","mean_score":"ilo_mean","sd_score":"ilo_sd","gradient":"ilo_gradient"}), on="isco08")
agg["equal_weight_automation"] = agg_eq.automation.values
agg.to_csv("outputs/occupation_exposure.csv", index=False)
C = dict(M.CFG)
U, strat = M.strategies(agg, C)
res = {}
for name, x in strat.items():
    e = M.evaluate(U, x); res[name] = e
    cum = np.cumsum(e["net_y"]); e["payback"] = next((i+1 for i,v in enumerate(cum) if v>=0 and e["employees"]>0), None)
    e["roi"] = (e["pv_ben"]-e["pv_cost"])/e["pv_cost"] if e["pv_cost"]>0 else None
alloc = pd.DataFrame({"role":U.role,"intervention":U.k.map(M.KNAME),"k":U.k,"npv_per_employee":U.npv.round(0),"cost_per_employee":U.cost.round(0)})
for name,x in strat.items(): alloc[name]=x
alloc.to_csv("outputs/allocation_by_strategy.csv", index=False)
pd.DataFrame([{k:v for k,v in dict(strategy=n, **e).items() if k!="net_y"} for n,e in res.items()]).to_csv("outputs/strategy_comparison.csv", index=False)
scen = {}
xo = strat["Optimised portfolio"]
for s in M.ADOPT:
    c2 = dict(C, scenario=s); U2,_ = M.optimise(agg,c2)[:2]; ev = M.evaluate(U2, xo); U3,x3,_ = M.optimise(agg,c2)
    scen[s] = dict(fixed_portfolio_npv=ev["npv"], reoptimised_npv=M.evaluate(U3,x3)["npv"], reoptimised=dict(zip([f"{U3.role[i]}|{U3.k[i]}" for i in range(len(U3)) if x3[i]], [int(v) for v in x3 if v])))
# threshold robustness + human-validation template (blank human columns)
th=[]
for soc,g in df.groupby("onet_soc",sort=False):
    w=M.weights(g)
    for t in (2,3,4): th.append(dict(occupation=M.ROLES[soc]["label"],threshold=f"exposure>={t}",weighted_task_share=float(np.sum(w*(g.exposure>=t)))))
pd.DataFrame(th).to_csv("outputs/threshold_robustness.csv",index=False)
tpl=pd.concat([g.sample(8,random_state=42) for _,g in df.groupby("onet_soc")])[["onet_soc","task_id","task_statement"]]
for d in scoring.DIMS: tpl["human_"+d]=""
tpl.to_csv("outputs/human_validation_template.csv",index=False)
rob = M.robustness(agg, C); rob.to_csv("outputs/sensitivity.csv", index=False)
# break-even productivity improvement for the optimised portfolio
e = res["Optimised portfolio"]; be = e["pv_cost"]/e["pv_ben"] if e["pv_ben"] else None
json.dump(dict(strategies={n:{k:(v if not isinstance(v,np.ndarray) else v.tolist()) for k,v in e.items()} for n,e in res.items()},
    scenarios=scen, breakeven_benefit_scale=be, config={k:v for k,v in C.items()}), open("outputs/results.json","w"), indent=1, default=float)
print(agg[["occupation","automation","gradient_auto","ilo_mean","ilo_gradient"]].round(2).to_string()); print({n:round(e["npv"]/1e7,2) for n,e in res.items()})
