# Architecture

## Core idea

T1Pal is not primarily an LLM application. Its core is a personal diabetes data and analytics platform. The LLM sits above deterministic analytics and predictive models as a natural-language interface.

Conceptually:

```text
Data sources
    |
    v
Provider adapters
    |
    v
Canonical T1Pal data model
    |
    +--> Analytics engine
    +--> Prediction engine
    +--> Safety rules
    |
    v
Structured evidence/context
    |
    v
LLM companion
    |
    v
CLI first, richer interfaces later
```

## Provider boundaries

External systems must remain behind provider interfaces. The domain layer must not depend directly on Dexcom, Tandem, Nightscout, OpenAI, Anthropic, Ollama, llama.cpp, or another vendor.

Expected provider categories include:

- glucose data providers,
- pump data providers,
- LLM providers,
- secret stores.

This allows T1Pal to support different sources without reshaping the core domain around one vendor.

## Canonical data model

The internal model should represent diabetes concepts rather than source-specific payloads.

Initial concepts include:

- glucose readings,
- insulin delivery,
- carbohydrate events,
- basal delivery,
- pump settings,
- device events,
- activity events,
- annotations.

Source adapters convert external records into this canonical model.

## Provenance

Imported and derived data should retain provenance. T1Pal should be able to distinguish, where applicable:

- the value,
- the unit,
- when it was observed,
- when it was received or imported,
- its source,
- its source record identifier,
- the import that introduced it.

Derived analysis should similarly retain enough information to reproduce how a conclusion was produced.

## Analytics engine

The analytics engine owns deterministic calculations such as:

- time in range,
- time below range,
- time above range,
- mean and median glucose,
- standard deviation,
- coefficient of variation,
- daily and nighttime patterns,
- low/high frequency,
- insulin totals,
- basal/bolus relationships where supported by the available data.

The LLM must not be responsible for deriving these values from raw data.

## Prediction engine

Forecasting should be developed as a separate component from the LLM.

Candidate features may include:

- current glucose,
- glucose velocity and acceleration,
- time of day,
- insulin on board,
- carbohydrates on board,
- recent basal delivery,
- recent boluses,
- exercise or meal events,
- historical response patterns.

Candidate outputs may include future glucose estimates and probabilities of low/high glucose over defined horizons.

Development should begin with simple baselines and progress only when more complex models demonstrate measurable improvement under time-aware backtesting.

## LLM companion

The LLM consumes structured evidence rather than raw history wherever practical.

A typical flow is:

```text
user question
    |
    v
select deterministic tools/analysis
    |
    v
structured result
    |
    v
LLM explanation
```

The LLM may explain patterns, summarize findings, and help the user explore their data. It must not replace deterministic calculations or directly control therapy.

## Interfaces

The initial interface is a CLI.

A later HTTP/API and web interface should sit on top of the same application layer. Domain and analytical logic must not be embedded in the CLI or future HTTP handlers.

## Auditability

T1Pal should make assistant conclusions reproducible. An assistant run should eventually be able to record information such as:

- question,
- model and model version,
- prompt version,
- data range,
- analytics version,
- forecast model version where applicable,
- input hash or equivalent reproducibility metadata,
- generated output.

The objective is to make it possible to inspect what data and logic supported a generated conclusion.
