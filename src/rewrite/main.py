from rewrite.ops import router as ops_router
from fastapi import FastAPI
from rewrite.answer import answer

app = FastAPI()
app.include_router(ops_router, prefix="/v1")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/ask")
def post_ask(body: dict):
    return answer(body.get("question", ""))
