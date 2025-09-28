# CodeGen Service

Prod-ready сервис генерации кода на базе OpenAI.

## TL;DR
- **Стек:** FastAPI, Async SQLAlchemy, Pydantic Settings, OpenAI (async).
- **Архитектура:** Clean Architecture + MVC + DDD (domain / application / infrastructure / interfaces).
- **RB-гейты:** секреты и дрейф модели.
- **Плагины:** постпроцессинг (trim, black, авто-тесты и т.д.).

## Быстрый старт
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# пропишите OPENAI_API_KEY
uvicorn interfaces.http.api:app --reload
```

## Переменные окружения
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
DB_URL=sqlite+aiosqlite:///./dev.db
```

## API
- `GET /health` — liveness/readiness.
- `POST /generate` — сгенерировать код (языки: python|javascript|go).
- `GET /history?limit=20&language=python` — история генераций.

## Тесты и покрытие
```bash
coverage run -m pytest && coverage report
```

## Прод рекомендации
- БД: PostgreSQL (`DB_URL=postgresql+asyncpg://...`).
- Логи: STDOUT + JSON, ротация на уровне оркестратора.
- Secrets — vault/CI-secrets, никаких `.env` в проде.
- Лимиты токенов — через `.env` + валидация схемой.

## Плагины
Добавляйте плагины по протоколу `Plugin.run(code, language) -> str`. Регистрация через `PluginManager`.

## Дальше
- Подключить `ruff`/`mypy`, добавить SBOM/Trivy.
- Вынести плагины в пакет с entry points.
- Добавить gRPC API на тех же use-case слоях.
- Включить Observability: OTEL трассинг, метрики (tokens_in/out, RB flags, latency).
