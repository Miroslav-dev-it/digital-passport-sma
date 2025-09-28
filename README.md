# CodeGen Service

Enterprise-ready async code generation service built on FastAPI + OpenAI.

## TL;DR
- Clean layers via Golden Framework (domain/application/infrastructure/interfaces/config).
- OpenAI GPT-4.1 hooked through async client with safety gates + token guard rails.
- SQLite for dev, PostgreSQL for prod. Generation history + audit logs persisted via async SQLAlchemy.
- Plugin system for post-processing (formatters/linters/tests ready to slot in).

## Quickstart
1. **Install deps**
   ```bash
   pip install poetry
   poetry install
   ```
2. **Configure env**
   ```bash
   cp .env.example .env
   # edit with your OpenAI key + DB URL
   ```
3. **Run API**
   ```bash
   poetry run uvicorn src.main:app --reload
   ```
4. **Hit endpoints**
   ```bash
   curl -X POST http://localhost:8000/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "build a fastapi ping", "language": "python"}'
   ```

## Configuration (.env)
```env
CODEGEN_OPENAI_API_KEY=sk-***
CODEGEN_DATABASE_URL=sqlite+aiosqlite:///./codegen.db
CODEGEN_MAX_TOKENS_LIMIT=2048
CODEGEN_ENVIRONMENT=dev
```

## Architecture
Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for layer breakdown + Mermaid diagram.

## API Contract
OpenAPI spec lives at [docs/openapi.yaml](docs/openapi.yaml). Highlights:
- `POST /generate` – async codegen with safety validation.
- `GET /history` – fetch latest generation runs.
- `GET /health` – ops ping.

## OpenAI Integration Snippet
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.openai_api_key)
response = await client.responses.create(
    model=settings.openai_model,
    input=payload.prompt,
    max_output_tokens=payload.max_tokens,
    metadata={"language": payload.language.value},
)
code = response.output[0].content[0].text
```

## Testing & Quality Gates
```bash
poetry run pytest
poetry run ruff check src tests
```
Coverage target: **85%+** enforced via `pytest --cov`.

## CI/CD
See [.github/workflows/ci.yml](.github/workflows/ci.yml) – runs lint + tests + coverage on every push/PR.

## Deployment Notes
- Flip `CODEGEN_DATABASE_URL` to `postgresql+asyncpg://...` in prod.
- Extend safety gates or plugins by registering new implementations inside `interfaces/api/dependencies.py`.
- Ready for gRPC add-ons by layering new interface adapters without touching core domain.
