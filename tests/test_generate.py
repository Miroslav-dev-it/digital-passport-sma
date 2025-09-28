"""HTTP layer tests using pytest-asyncio."""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from interfaces.http.api import app

pytestmark = pytest.mark.asyncio


class DummyLLM:
    async def generate(self, prompt, language, max_tokens, temperature):
        code = "```python\nprint('hello')\n```" if language == "python" else "```\nconsole.log('hello')\n```"
        return {"code": code, "tokens_in": 10, "tokens_out": 5, "model": "gpt-4.1-mini"}


@pytest.fixture(autouse=True)
def env_setup(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_URL", f"sqlite+aiosqlite:///{tmp_path/'test.db'}")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    from interfaces.http.api import reset_dependency_cache

    reset_dependency_cache()


@pytest_asyncio.fixture
async def client():
    from interfaces.http import api as api_mod

    _, repo, _ = api_mod.get_di()
    await repo.init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_generate_python(client, monkeypatch):
    from interfaces.http import api as api_mod

    settings, repo, uc = api_mod.get_di()
    uc._llm = DummyLLM()
    monkeypatch.setattr(api_mod, "get_di", lambda: (settings, repo, uc))

    payload = {"prompt": "print hello", "language": "python", "max_tokens": 256}
    response = await client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "python"
    assert "print('hello')" in data["code"]


async def test_history(client):
    response = await client.get("/history?limit=5")
    assert response.status_code == 200
    assert "items" in response.json()
