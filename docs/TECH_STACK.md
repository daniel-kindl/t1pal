# Technology Stack

This document records the initial T1Pal technology direction. It does not represent an implementation commitment beyond the decisions already discussed.

## Runtime and project management

- Python 3.14.
- CPython rather than the free-threaded build initially.
- `uv` for Python installation, virtual environments, dependency management, locking, scripts, and tools.

## CLI

- Typer for the command-line interface.
- Rich for terminal output, tables, and formatting.

The CLI is the initial product surface.

## Domain models and validation

- Pydantic v2 for typed domain/application contracts and validation.

Domain models should remain independent from persistence models.

## Persistence

- SQLite as the local source of truth.
- SQLAlchemy 2 for persistence.
- Alembic for schema migrations.
- Synchronous persistence initially.

The expected dataset size is comfortably within SQLite's capabilities for a local personal application.

## Analytics and scientific computing

- Polars for dataframe and time-series-oriented analysis.
- NumPy when needed.
- SciPy when needed.
- Parquet as a derived analytical/export format where useful.

SQLite remains authoritative; Parquet may be used for derived datasets, experimentation, or model training.

## Machine learning

Initial ML work should start with scikit-learn and simple baselines.

Candidate progression:

1. persistence/naive forecasting,
2. linear or logistic models,
3. tree-based models available through scikit-learn,
4. XGBoost or LightGBM only if experiments justify adding them,
5. PyTorch substantially later if neural approaches demonstrate a clear reason to exist.

Model evaluation must respect time ordering. Random train/test splitting is not appropriate for glucose forecasting.

## LLM layer

T1Pal should use its own small, typed orchestration layer rather than introducing a general LLM framework initially.

Expected provider boundary:

```text
LLMProvider
    |
    +--> OpenAI adapter
    +--> Anthropic adapter
    +--> Ollama adapter
    +--> llama.cpp adapter
```

Local and cloud models should both remain possible.

Do not introduce LangChain, LlamaIndex, Semantic Kernel, or a vector database unless a concrete use case later demonstrates a need.

## API and web UI

These are later-stage components, not part of the initial bootstrap.

Planned direction:

- FastAPI for an HTTP/API layer.
- React + TypeScript + Vite for a later web interface.

Both should sit on top of the same application/domain layer used by the CLI.

## Testing and quality

- pytest for tests.
- Hypothesis for property-based testing.
- Ruff for linting and formatting.
- Pyright for static type checking.
- GitHub Actions for CI.

Important invariants to test over time include:

- imports are idempotent,
- duplicate source records do not create duplicate canonical events,
- glucose units cannot silently change,
- chronological ordering is preserved,
- analytical percentages remain internally consistent,
- forecasting code cannot train on future observations.

## Secrets

Secrets should sit behind a `SecretStore`-style abstraction.

Expected implementations may include:

- environment-backed secrets for controlled environments,
- operating-system keyring storage for local use.

Provider credentials and API keys must not be stored in the public repository or alongside committed data.

## Explicitly deferred technologies

Do not introduce these without demonstrated need:

- PostgreSQL or TimescaleDB for the local V0,
- InfluxDB,
- Redis,
- Kafka,
- Kubernetes,
- vector databases,
- a general-purpose LLM orchestration framework,
- custom LLM training/fine-tuning.
