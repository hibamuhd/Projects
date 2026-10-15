import json, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False})
a=pd.read_csv("outputs/occupation_exposure.csv"); s=pd.read_csv("outputs/strategy_comparison.csv"); r=pd.read_csv("outputs/sensitivity.csv"); al=pd.read_csv("outputs/allocation_by_strategy.csv")
lab=["Software\nDevelopers","QA Analysts\n& Testers","Customer Service\nReps"]
# 1 exposure vs automation vs ILO benchmark
f,ax=plt.subplots(figsize=(8,4.2)); x=np.arange(3); w=.26
ax.bar(x-w,a.exposure,w,label="AI exposure (this study)",color="#1f4e79"); ax.bar(x,a.automation,w,label="Automation potential (this study)",color="#5b9bd5")
ax.bar(x+w,a.ilo_mean,w,label="ILO 2025 mean score (ISCO-08)",color="#bfbfbf")
for i,v in enumerate(a.ilo_mean): ax.errorbar(i+w,v,yerr=a.ilo_sd[i],color="k",capsize=3)
ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_ylabel("Score (0-1)"); ax.set_ylim(0,1); ax.legend(frameon=False,fontsize=9,loc="upper left"); ax.set_title("Exposure ranking matches the ILO; levels differ by task definition",fontsize=11)
f.tight_layout(); f.savefig("outputs/figures/fig1_exposure_vs_ilo.png",dpi=160); plt.close()
# 2 strategy NPV (INR crore)
f,ax=plt.subplots(figsize=(8,4)); v=s.npv/1e7; c=["#1f4e79" if n.startswith("Opt") else "#c00000" if x<0 else "#9dc3e6" for n,x in zip(s.strategy,v)]
ax.barh(s.strategy[::-1],v[::-1],color=c[::-1]); ax.axvline(0,color="k",lw=.8); ax.set_xlabel("3-year NPV, INR crore (base case)")
for i,x in enumerate(v[::-1]): ax.text(x+(.3 if x>=0 else -.3),i,f"{x:.1f}",va="center",ha="left" if x>=0 else "right")
ax.set_title("Optimised portfolio beats training the most exposed roles",fontsize=11); f.tight_layout(); f.savefig("outputs/figures/fig2_strategy_npv.png",dpi=160); plt.close()
# 3 tornado
f,ax=plt.subplots(figsize=(8,4.6)); b=r.base_npv[0]/1e7; r["sp"]=(r.npv_high-r.npv_low).abs(); r=r.sort_values("sp")
for i,(lo,hi) in enumerate(zip(r.npv_low/1e7,r.npv_high/1e7)): ax.barh(i,hi-lo,left=lo,color="#5b9bd5")
ax.set_yticks(range(len(r))); ax.set_yticklabels(r.driver,fontsize=9); ax.axvline(b,color="k",lw=.8); ax.set_xlabel("Re-optimised 3-year NPV, INR crore (base = line)")
ax.set_title("Value is most sensitive to AI adoption and productivity realisation",fontsize=11); f.tight_layout(); f.savefig("outputs/figures/fig3_tornado.png",dpi=160); plt.close()
# 4 allocation
f,ax=plt.subplots(figsize=(8,4)); piv=al.pivot_table(index="role",columns="k",values="Optimised portfolio",aggfunc="sum").reindex(["Software Developers","QA Analysts & Testers","Customer Service Reps"])
bot=np.zeros(3); col=dict(D="#1f4e79",A="#ed7d31",B="#70ad47",C="#a5a5a5"); nm=dict(D="Redesign & monitor",A="Reskill",B="Redeploy",C="Hire specialists")
for k in "DABC":
    ax.bar(range(3),piv[k],bottom=bot,color=col[k],label=nm[k]); bot+=piv[k].to_numpy()
ax.set_xticks(range(3)); ax.set_xticklabels(lab); ax.set_ylabel("Employees"); ax.legend(frameon=False,fontsize=9); ax.set_title("Base-case optimal allocation (hypothetical 10,000-person client)",fontsize=11)
f.tight_layout(); f.savefig("outputs/figures/fig4_allocation.png",dpi=160); plt.close()
