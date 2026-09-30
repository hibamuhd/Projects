"""Fixed benchmark. Relevance labels are RULE-DEFINED from catalogue tags (see docs/EVALUATION_REPORT.md for the circularity caveat).
`oracle_*` fields define hard constraints independently of the intent parser."""
def q(qid, query, interests, budget=None, exclude=(), kind="answerable", expect="ok", category=None):
    return {"id": qid, "query": query, "expected_interests": list(interests), "oracle_budget_max": budget,
            "oracle_exclusions": list(exclude), "kind": kind, "expect_status": expect, "category": category}


EVAL_QUERIES = [
    q("Q01", "Find a thoughtful gift under ₹1,500 for a friend who loves reading, prefers practical things, and dislikes generic gifts", ["reading"], 1500),
    q("Q02", "Gift for a coffee lover, budget ₹1,000", ["coffee"], 1000),
    q("Q03", "Something for my sister who is into yoga and fitness under ₹1200", ["yoga", "fitness"], 1200),
    q("Q04", "Birthday present for a colleague who loves tea, up to ₹700", ["tea"], 700),
    q("Q05", "Gift for a friend who loves cooking, no candles, under 1500", ["cooking"], 1500, ["candle"]),
    q("Q06", "Practical tech gadget for a college student under ₹1,000", ["tech"], 1000),
    q("Q07", "A travel lover is moving abroad, what can I get under ₹1,200", ["travel"], 1200),
    q("Q08", "Creative gift for someone who loves sketching and art, max ₹1,500", ["art"], 1500),
    q("Q09", "Something for a board game and puzzle fan under 1000", ["games"], 1000),
    q("Q10", "Gift for my mom who loves plants and home decor under ₹900", ["plants", "home"], 900),
    q("Q11", "Unique gift for a friend who loves reading", ["reading"], None),
    q("Q12", "Housewarming gift under ₹800", ["home"], 800, kind="answerable_loose"),
    q("Q13", "Gift for a baking enthusiast, budget 1,200, nothing generic", ["baking", "cooking"], 1200),
    q("Q14", "Study essentials for an exam-prep student under ₹600", ["study"], 600),
    q("Q15", "Wellness gift for my dad who wants to relax and sleep better, under ₹1,500", ["wellness"], 1500),
    q("Q16", "Gift for a music lover under ₹1,500", ["music"], 1500),
    q("Q17", "Snack hamper for a colleague under ₹1,000", ["snacks"], 1000),
    q("Q18", "Journaling and writing gift for a friend under ₹500", ["writing"], 500),
    q("Q19", "Eco-friendly practical gift for someone who loves fitness, under ₹1,000", ["fitness"], 1000),
    q("Q20", "Gift for a friend who loves fashion accessories under ₹700", ["fashion"], 700),
    q("Q21", "Learning gift for a curious teenager under ₹2,000", ["learning"], 2000),
    q("Q22", "Coffee lover gift between ₹500 and ₹900", ["coffee"], 900),
    q("Q23", "Reading gift, no books, under ₹1000 for a bookworm friend", ["reading"], 1000, ["book"], kind="conflict", expect="needs_clarification"),
    q("Q24", "Photography and art gift for a friend, up to 2,000", ["art"], 2000),
    q("E01", "something nice", [], None, kind="vague", expect="needs_clarification"),
    q("E02", "Gift under ₹500 but at least ₹900 for a friend who loves tea", ["tea"], None, kind="conflict", expect="needs_clarification"),
    q("E03", "Buy this for me now", [], None, kind="unsupported", expect="unsupported"),
    q("E04", "Gift for someone who loves scuba diving under ₹100", ["scuba"], 100, kind="no_match", expect="no_results"),
    q("E05", "Reading gift under ₹50", ["reading"], 50, kind="no_match", expect="no_results"),
    q("E06", "Cheap but premium gift for my friend", [], None, kind="conflict", expect="needs_clarification"),
]
