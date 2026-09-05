# Roadmap

This roadmap records the staged direction discussed for T1Pal. It is intentionally high level and does not initialize implementation work.

## V0

Goal: make personal diabetes data locally useful through deterministic analysis and a CLI.

Planned direction:

- Python-based core.
- Local SQLite storage.
- Provider-neutral canonical data model.
- Tandem Source CSV importer first.
- Deterministic statistics and pattern analysis.
- CLI commands for statistics, timelines, lows, highs, and pattern exploration.
- Typed LLM provider boundary.
- Natural-language questions over structured analytical output.
- Synthetic test data only.
- Read-only operation.

Representative future CLI ideas discussed:

```text
t1pal import tandem <export.csv>
t1pal status
t1pal stats --days 30
t1pal lows --days 30
t1pal highs --days 30
t1pal timeline <date>
t1pal patterns
t1pal ask "Do you see any recurring nighttime patterns?"
```

These examples describe intended product behavior only; they are not yet implemented.

## V0.2

Goal: reduce dependence on manual exports.

Planned direction:

- Nightscout integration.
- Dexcom integration where supported and appropriate.
- Additional provider adapters as useful.
- Preserve the same provider-neutral domain model.

## V0.3

Goal: introduce dedicated glucose forecasting.

Planned direction:

- Build naive and statistical baselines first.
- Add time-aware backtesting.
- Introduce scikit-learn models where useful.
- Estimate future glucose and low/high risk over defined horizons.
- Add complexity only when it provides measurable improvement over baselines.

## V0.4

Goal: strengthen local/private AI operation.

Planned direction:

- Local LLM provider support through Ollama and/or llama.cpp.
- Keep cloud LLM providers optional behind the same abstraction.
- Continue passing structured evidence to the LLM instead of raw history wherever practical.

## V1

Goal: add a richer application interface without changing the core architecture.

Planned direction:

- FastAPI application/API layer.
- React + TypeScript + Vite web UI.
- Reuse the same domain, analytics, forecasting, and application layers used by the CLI.

## Later research

Potential later work includes:

- richer personalized forecasting models,
- additional diabetes-data sources,
- more advanced pattern detection,
- PyTorch-based models if justified by experiments,
- richer personal annotations and contextual data,
- improved reproducibility and assistant-run auditing.

## Deliberately not scheduled

The following are not part of the early roadmap:

- autonomous pump control,
- automatic bolusing,
- automatic pump-setting changes,
- custom LLM training or fine-tuning without demonstrated need,
- hosted multi-user infrastructure before the local product proves useful,
- infrastructure complexity that does not solve a demonstrated problem.
