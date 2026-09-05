# T1Pal

T1Pal is a personal, local-first Type 1 diabetes data and analytics companion.

The project is intended to ingest diabetes-related data, normalize it into a provider-neutral model, calculate deterministic statistics and patterns, support forecasting and machine-learning experiments, and expose the results through a CLI first and richer interfaces later.

The LLM is a natural-language reasoning and explanation layer over structured evidence. It is not the source of truth for glucose calculations, insulin calculations, forecasts, or safety-critical decisions.

## Product principles

- Local-first and privacy-first by default.
- Read-only device and data integrations first.
- Provider-agnostic domain model.
- Deterministic analytics before LLM reasoning.
- Evidence, provenance, and reproducibility behind generated conclusions.
- CLI-first initial product; API and web UI later.
- Synthetic test data only in the public repository.

## Initial direction

The first useful version should focus on importing real diabetes data and making it understandable before attempting advanced automation.

Initial source priority:

1. Tandem Source CSV exports.
2. Nightscout.
3. Dexcom where supported and appropriate.
4. Additional CGM and pump providers through adapters.
5. Manual annotations and events where useful.

Initial user-facing capabilities are expected to include statistics, timelines, recurring low/high pattern analysis, and natural-language questions over structured analysis.

## Safety boundary

Early T1Pal integrations are read-only.

T1Pal must not autonomously:

- send a bolus,
- change basal delivery,
- modify pump settings,
- directly control therapy or a medical device.

Safety-critical calculations belong in deterministic, testable code or dedicated predictive models. The LLM may summarize and explain structured outputs, but it must not act as an autonomous medical control loop.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Technology stack](docs/TECH_STACK.md)
- [Safety and privacy](docs/SAFETY_AND_PRIVACY.md)
- [Roadmap](docs/ROADMAP.md)
