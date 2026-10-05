# rag-with-query-rewriting — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does rag-with-query-rewriting address, and what can you demonstrate?

Rewrite short slang (`pdb` → pod disruption budget) before retrieval.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/rewrite/main.py`](src/rewrite/main.py): Implementation or supporting configuration.
- [`src/rewrite/answer.py`](src/rewrite/answer.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/rewrite/__init__.py`](src/rewrite/__init__.py): Implementation or supporting configuration.
- [`tests/test_ask.py`](tests/test_ask.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `answer` and explain the decision it makes?

The main walkthrough here is `answer(question)` in [`src/rewrite/answer.py`](src/rewrite/answer.py#L20).

```python
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
```

The implementation calls `len`, `ranked.append`, `ranked.sort`, `rewrite`, `words`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `rewrite` have?

`rewrite(question)` is defined in [`src/rewrite/answer.py`](src/rewrite/answer.py#L12).

Its return expressions include:

- `question`
- `question + ' ' + dst`

It uses `REWRITES.items`, `question.lower`. This is the code path I would compare against the caller to explain responsibility boundaries.

## 5. Where would you add input-validation tests?

Start with the handlers `healthz` in [`src/rewrite/main.py`](src/rewrite/main.py#L8), `post_ask` in [`src/rewrite/main.py`](src/rewrite/main.py#L13). Use the request schema or body access in each handler to build valid, missing-field, wrong-type, and boundary inputs. I would inspect existing tests before claiming coverage.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_ask.py`](tests/test_ask.py#L7) contains `test_rewrite_finds_the_passage`:

```python
def test_rewrite_finds_the_passage():
    payload = client.post("/ask", json={"question": 'What does pdb keep available?'}).json()
    assert payload["answered"] is True
    assert payload["citation"] == "pdb.md"
    assert payload["rewritten"] != 'What does pdb keep available?'
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/rewrite/main.py`](src/rewrite/main.py#L8).
- `POST /ask` → `post_ask` in [`src/rewrite/main.py`](src/rewrite/main.py#L13).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `PASSAGES`, `REWRITES`, `STOP` in [`src/rewrite/answer.py`](src/rewrite/answer.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `answer`?

In [`src/rewrite/answer.py`](src/rewrite/answer.py#L20), `answer(question)` receives the inputs. The function computes these intermediate values:

- `rewritten = rewrite(question)`
- `query = words(rewritten)`
- `ranked = []`
- `best = ranked[0]`

Its result is defined by:

- `{'rewritten': rewritten, 'answered': best['overlap'] >= 2, 'answer': best['text'] if best['overlap'] >= 2 else 'No passage shares enough terms.', 'citation': best['source'] if best['overlap'] >= 2 else None, 'passages': ranked}`
