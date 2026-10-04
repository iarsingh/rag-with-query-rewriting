from fastapi.testclient import TestClient
from rewrite.main import app

client = TestClient(app)


def test_rewrite_finds_the_passage():
    payload = client.post("/ask", json={"question": 'What does pdb keep available?'}).json()
    assert payload["answered"] is True
    assert payload["citation"] == "pdb.md"
    assert payload["rewritten"] != 'What does pdb keep available?'
