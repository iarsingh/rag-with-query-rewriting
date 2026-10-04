from fastapi import FastAPI
from rewrite.answer import answer

app = FastAPI()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/ask")
def post_ask(body: dict):
    return answer(body.get("question", ""))
