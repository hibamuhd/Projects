"""Task scoring: rubric, schema validation, and the LLM-generated score table.
Scores were produced by Claude Sonnet 5.5 in-conversation on 2026-10-15 (single pass, rubric v1.0).
They are NOT human-validated; see outputs/human_validation_template.csv."""
import pandas as pd, numpy as np
RUBRIC = {  # all 0-4
 "exposure": "How much of the task's information processing current GenAI could affect (0 none .. 4 nearly all)",
 "automation": "Share executable by current AI with limited human intervention (0 none .. 4 end-to-end)",
 "augmentation": "Productivity gain if AI assists while the employee stays accountable (0 none .. 4 very large)",
 "human_judgment": "Judgment, interpersonal work, accountability or verification that stays human (0 none .. 4 dominant)",
 "feasibility": "Adoption feasibility given integration, data access, security, regulation (0 hard .. 4 easy)"}
DIMS = list(RUBRIC)
SCORER, DATE, RUBRIC_V = "Claude Sonnet 5.5 (in-conversation)", "2026-10-15", "v1.0"
# (E, A, G, H, F, confidence, rationale) in raw-file row order
S = {
"15-1252.00": [
(3,1,3,4,3,"M","feasibility judgement stays human; AI drafts analysis"),(4,2,4,3,4,"H","code, test, doc generation mature; review needed"),
(2,1,2,4,3,"M","interpersonal design discussion"),(4,2,4,3,4,"H","bug fixing and refactoring well supported"),
(4,3,4,2,4,"H","report drafting"),(3,1,3,4,3,"M","planning needs context and accountability"),
(3,3,3,2,4,"H","routine data manipulation scriptable"),(3,2,4,4,3,"M","design with modelling; high verification"),
(2,1,2,4,3,"M","standards need organisational judgement"),(2,1,2,4,3,"M","client consultation"),
(2,1,2,4,3,"M","stakeholder coordination"),(2,3,2,3,4,"M","monitoring is tool-automatable"),
(2,2,2,3,3,"M","installation coordination mixed"),(1,0,2,4,2,"H","people supervision"),
(1,0,2,4,2,"H","people supervision"),(2,2,3,3,3,"M","config evaluation assisted"),(2,1,3,3,3,"M","training partly assisted")],
"15-1253.00": [
(3,2,4,3,4,"H","defect triage assisted; root cause needs context"),(4,3,4,2,4,"H","structured defect write-up"),
(4,3,4,3,4,"H","test generation"),(4,3,4,3,4,"H","test design generation"),
(4,3,4,2,4,"H","procedure documentation"),(3,1,3,4,3,"M","feedback needs judgement"),
(2,3,2,2,4,"M","tool operation"),(3,3,3,3,4,"M","execution partly automated"),
(3,3,3,2,4,"H","defect records structured"),(2,1,3,4,3,"M","release standards judgement"),
(3,3,3,2,4,"H","tracking automatable"),(4,3,4,3,4,"H","script maintenance well supported"),
(2,1,2,4,3,"M","review participation"),(3,2,3,3,3,"M","planning assisted"),
(3,3,3,2,4,"M","monitoring automatable"),(2,3,2,3,3,"M","compatibility matrices automatable"),
(3,2,3,3,3,"M","investigation assisted"),(4,3,4,3,4,"H","document review"),
(3,2,3,3,3,"M","standards check assisted"),(3,2,4,3,4,"M","log analysis assisted"),
(4,2,4,3,4,"H","tool code generation"),(2,2,2,3,3,"M","environment setup scriptable"),
(2,1,2,4,2,"M","field interaction"),(2,1,2,3,3,"M","coordination"),
(1,0,1,4,1,"H","physical site visits"),(3,3,4,2,4,"H","analytics on results"),
(2,1,3,4,3,"M","tool selection judgement"),(4,2,4,3,4,"M","code modification"),
(1,0,1,4,2,"H","physical facility decision"),(3,3,3,2,4,"M","data manipulation")],
"43-4051.00": [
(3,3,4,3,3,"M","voice/chat agents improving; escalation judgement"),(4,4,4,1,4,"H","auto-summarised interaction records"),
(3,3,3,2,4,"M","verification workflows"),(4,3,4,2,4,"H","templated responses"),
(3,3,3,2,3,"M","payments need compliance controls"),(4,4,4,1,4,"H","form completion automatable"),
(3,3,3,2,4,"M","routing rules"),(3,2,3,3,3,"M","policy plus empathy"),
(4,2,4,4,3,"M","coverage liability; high verification"),(3,2,3,3,3,"M","persuasion partly assisted"),
(4,3,3,2,4,"M","document matching"),(3,2,3,3,3,"M","assessment needs judgement"),
(3,1,3,4,3,"M","improvement recommendations judgement")]}
OCC = {"15-1252.00":"Software Developers","15-1253.00":"Software QA Analysts and Testers","43-4051.00":"Customer Service Representatives"}

def load_raw():
    a = pd.read_csv("data/raw/onet_15-1252.00_tasks.csv"); b = pd.read_csv("data/raw/onet_15-1253.00_tasks.csv")
    c = pd.read_csv("data/raw/onet_43-4051.00_tasks_raw.csv")
    c = pd.DataFrame({"onet_soc":"43-4051.00","occupation":OCC["43-4051.00"],"task_id":[f"CSR-{i+1:02d}" for i in range(len(c))],
        "task_importance":c["Importance"],"category":c["Category"],"task_statement":c["Task"],
        "source_url":"https://www.onetonline.org/link/details/43-4051.00","retrieved":DATE})
    return pd.concat([a,b,c],ignore_index=True)

def validate(df):
    assert df[DIMS].notna().all().all(), "missing scores"
    assert df[DIMS].apply(lambda s: s.between(0,4).all()).all(), "score out of 0-4"
    assert df["confidence"].isin(list("LMH")).all()
    return df

def build():
    raw = load_raw(); parts = []
    for soc, g in raw.groupby("onet_soc", sort=False):
        s = pd.DataFrame(S[soc], columns=DIMS+["confidence","rationale"])
        assert len(s)==len(g), f"{soc}: {len(s)} scores vs {len(g)} tasks"
        parts.append(pd.concat([g.reset_index(drop=True), s], axis=1))
    df = pd.concat(parts, ignore_index=True)
    df["scorer"], df["scoring_date"], df["rubric_version"] = SCORER, DATE, RUBRIC_V
    return validate(df)

def qwk(a, b, k=5):
    """Quadratic weighted kappa for human-vs-LLM agreement."""
    a, b = np.asarray(a, int), np.asarray(b, int)
    O = np.zeros((k,k)); [O.__setitem__((i,j), O[i,j]+1) for i,j in zip(a,b)]
    E = np.outer(np.bincount(a,minlength=k), np.bincount(b,minlength=k))/len(a)
    W = (np.subtract.outer(range(k),range(k))**2)/(k-1)**2
    return 1 - (W*O).sum()/(W*E).sum()
