import sys; sys.path.insert(0,"src")
import numpy as np, pandas as pd, pytest
import scoring, model as M
@pytest.fixture(scope="module")
def agg(): return M.aggregate(scoring.build())
def test_weights_normalised_and_equal_fallback():
    g=pd.DataFrame({"task_importance":[80,20,np.nan]}); w=M.weights(g); assert abs(w.sum()-1)<1e-9 and w[2]==0
    assert np.allclose(M.weights(pd.DataFrame({"task_importance":[np.nan,np.nan]})),[.5,.5])
def test_schema_rejects_out_of_range():
    d=scoring.build(); d.loc[0,"exposure"]=5
    with pytest.raises(AssertionError): scoring.validate(d)
def test_ilo_gradient_rules():
    assert M.ilo_gradient(.70,.03)==4 and M.ilo_gradient(.55,.10)==3 and M.ilo_gradient(.45,.10)==2 and M.ilo_gradient(.30,.25)==1 and M.ilo_gradient(.2,.05)==0
def test_aggregation_bounds(agg):
    assert agg[["exposure","automation","assistable_share"]].apply(lambda s:s.between(0,1).all()).all()
def test_budget_and_headcount_constraints(agg):
    c=dict(M.CFG); U,x,ok=M.optimise(agg,c); assert ok
    assert (U.cost.to_numpy()*x).sum()<=c["budget"]+1
    for i,s in enumerate(M.ROLES): assert x[i*4:i*4+4].sum()<=M.ROLES[s]["N"]
    assert sum(x[i] for i in range(len(U)) if U.k[i] in "AB")<=c["train_cap"]
def test_bau_has_zero_value(agg):
    U,st=M.strategies(agg,dict(M.CFG)); assert M.evaluate(U,st["Business as usual"])["npv"]==0
def test_higher_discount_lowers_npv(agg):
    a=M.unit("15-1252.00","D",agg,dict(M.CFG,discount=.10))["npv"]; b=M.unit("15-1252.00","D",agg,dict(M.CFG,discount=.14))["npv"]; assert a>b
def test_qwk_perfect_and_worse():
    a=[0,1,2,3,4,2]; assert scoring.qwk(a,a)==pytest.approx(1.0); assert scoring.qwk(a,[4,3,2,1,0,2])<0.5
