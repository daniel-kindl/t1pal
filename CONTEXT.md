# T1Pal

T1Pal is a personal, local-first Type 1 diabetes data and analytics companion. It reads
exports from CGM and pump vendors, normalizes them into one provider-neutral model, and
calculates deterministic statistics over them.

This file is the glossary. It records what each word means, and which words not to use.

## Language

### Sources and imports

**Source**:
A vendor's export format, such as Dexcom Clarity or Tandem Source. A source is a format,
not a company and not a piece of hardware.
_Avoid_: provider, feed, integration

**Adapter**:
The code that reads one source and produces source records. An adapter turns bytes into
rows. It does not build domain objects.
_Avoid_: parser, importer, driver, connector

**Source record**:
One row as it appeared in an export file, with its values unchanged. Every canonical
record is derived from at least one source record.
_Avoid_: raw row, staging row

**Import**:
One execution of an adapter over one input path. An import either completes in full or
writes nothing.
_Avoid_: ingestion, sync, load, upload

**Provenance**:
The record of where a value came from: which source, which import, which source record,
and which device.

**Device**:
The physical hardware that produced data — one CGM sensor or one insulin pump. A device
has an identity of its own, because one export can contain several.
_Avoid_: transmitter, pump (as a modelling term), source device

### Glucose

**Reading**:
One CGM glucose measurement.
_Avoid_: EGV, glucose value, measurement, data point, sample

**Out-of-range reading**:
A reading where the sensor reported that glucose was below or above the range it can
report, instead of reporting a number. It has no numeric value and never gains one.
_Avoid_: sentinel, clamped reading, Low/High, floor value

**Coverage**:
The proportion of expected readings actually present in a window. Coverage is how T1Pal
expresses the absence of data; there is no record for a gap.
_Avoid_: completeness, uptime, gap, missing data

**Time in range**:
The proportion of readings inside 3.9–10.0 mmol/L. Time below range and time above range
are its counterparts. This range is a fixed analytics constant, not a user setting.
_Avoid_: TIR (in prose), in-target, target range

**Alert threshold**:
A glucose level at which a device is configured to alarm. Alert thresholds are settings,
they belong to a device, and they are never used to calculate time in range.
_Avoid_: target, limit, range

### Insulin

**Bolus**:
A discrete insulin dose. One concept, whatever requested it and however it was delivered.
_Avoid_: delivery, dose, injection, shot

**Initiator**:
Whether a bolus was requested by the user or by the pump's automation. One of `user` or
`automatic`. An automatic bolus is a bolus.
_Avoid_: Control-IQ bolus, auto bolus, manual bolus

**Bolus kind**:
What a bolus was for: food, correction, or both.
_Avoid_: bolus type, reason

**Delivery method**:
How a bolus was delivered: standard, extended, or quick. Independent of both initiator and
kind.
_Avoid_: delivery, bolus type, mode

**Basal**:
Continuous background insulin delivery, expressed as a rate.
_Avoid_: basal dose, background bolus

### Time

**Local time**:
The naive wall-clock value exactly as the source wrote it, with no offset. Every source
T1Pal reads writes local time and none of them records a zone.
_Avoid_: timestamp, naive time, device time

**Instant**:
An unambiguous point in time, resolved from a local time using a configured timezone. The
only value that may be ordered or subtracted.
_Avoid_: timestamp, UTC time, epoch

**Fold**:
Which pass through a repeated local hour a record belongs to, at a daylight-saving
fall-back. A record whose fold could not be determined is marked as such.
_Avoid_: DST flag, ambiguity

**Window**:
The span of time a statistic is computed over, bounded by local calendar days.
_Avoid_: period, range, timeframe

## Words this project does not use

**event**.
It means four incompatible things across the vendor formats and the early T1Pal documents:
a CSV row, a carbohydrate entry, a device state change, and an activity. Name the specific
concept instead — reading, bolus, activity, alert threshold.

**provider**.
Split into source (a format), device (hardware), and adapter (code). `docs/ARCHITECTURE.md`
still uses it for all three; that is a document to correct, not a term to keep.
