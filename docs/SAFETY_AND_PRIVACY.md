# Safety and Privacy

T1Pal handles sensitive personal health information. Safety, privacy, provenance, and auditability are core architectural requirements rather than later additions.

## Local-first

T1Pal should prefer local storage and local processing by default.

Cloud services may be supported through explicit provider adapters, but the architecture must not require personal diabetes history to be sent to a cloud service simply to make the core product useful.

Local LLM inference should remain a supported direction alongside cloud LLM providers.

## Read-only integrations first

Early integrations with diabetes systems are read-only.

T1Pal must not initially:

- send insulin boluses,
- change basal delivery,
- modify pump settings,
- write therapy changes back to a pump or CGM,
- autonomously control a medical device.

## Separation of responsibilities

Deterministic code or dedicated predictive models own calculations and forecasting.

The LLM may:

- explain structured analytics,
- summarize detected patterns,
- answer questions over validated evidence,
- present model outputs in understandable language.

The LLM must not be relied upon to derive safety-critical quantities directly from raw context or act as an autonomous control loop.

## Data provenance

Imported records should preserve source information and timestamps where available.

Derived conclusions should preserve enough metadata to determine what data, analytical code, model, and prompt contributed to the result.

This supports debugging, reproducibility, and user trust.

## Public repository hygiene

The T1Pal repository is public. Real personal diabetes data, credentials, tokens, exports, local databases, and private model artifacts must never be committed.

Tests and examples should use synthetic data rather than real user history, including supposedly anonymized copies of real data.

Data categories that must remain outside version control include:

- Tandem/Dexcom/Nightscout exports,
- SQLite databases,
- CSV/JSONL health-data exports,
- API tokens and credentials,
- environment-secret files,
- private model artifacts derived from personal health data.

## Secrets

Provider credentials and API keys should be managed through a secret-storage abstraction rather than stored in application data or committed configuration.

Expected local approaches include operating-system keyring storage. Environment-backed secrets may be used in controlled environments.

## Model evaluation

Predictive models must be evaluated with time-aware methods. Training or validation logic must not allow future observations to leak into past predictions.

More complex models should only replace simpler baselines when they demonstrate measurable improvement under appropriate backtesting.

## Advisory scope

T1Pal is being designed as a personal data, analytics, forecasting, and companion system. It should present evidence and uncertainty clearly and avoid representing LLM-generated explanations as authoritative therapy instructions.
