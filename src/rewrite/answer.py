import re

PASSAGES = [("pdb.md", 'A pod disruption budget keeps two replicas available during eviction.'), ("hpa.md", 'HPA scales on CPU when the average is above seventy percent.')]
REWRITES = {"pdb": "pod disruption budget replicas eviction", "hpa": "horizontal pod autoscaler cpu"}
STOP = {"the", "a", "an", "is", "of", "to", "in", "what"}


def words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower())) - STOP


def rewrite(question):
    lowered = question.lower()
    for src, dst in REWRITES.items():
        if src in lowered:
            return question + " " + dst
    return question


def answer(question):
    rewritten = rewrite(question)
    query = words(rewritten)
    ranked = []
    for name, text in PASSAGES:
        ranked.append({"source": name, "text": text, "overlap": len(query & words(text))})
    ranked.sort(key=lambda row: -row["overlap"])
    best = ranked[0]
    return {
        "rewritten": rewritten,
        "answered": best["overlap"] >= 2,
        "answer": best["text"] if best["overlap"] >= 2 else "No passage shares enough terms.",
        "citation": best["source"] if best["overlap"] >= 2 else None,
        "passages": ranked,
    }
