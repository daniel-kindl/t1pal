# Glucose comes from Clarity, insulin from Tandem, and the two are never merged

The pump receives its readings from the same sensor the phone does, so the same reading
exists in both exports. T1Pal imports and stores both, deduplicates neither, and reads
glucose from Dexcom Clarity and insulin from Tandem Source. The schema keeps a canonical
record's provenance in a separate table with no cardinality constraint, so today every
record has exactly one source record and merging two later is a change of one foreign key
rather than a migration.

## Considered options

Serving both glucose and insulin from Tandem alone is a real option and is thinner: one
adapter, one clock, and glucose aligned with insulin by construction. Coverage is not an
argument against it — measured over the period the two exports share, their reading counts
agree to within single digits, values agree byte-identically over 98% of the time, and
every remaining difference is exactly 0.1 mmol/L of mg/dL rounding. They are the same data
at equal quality.

It is rejected on two grounds. Tandem's only available key is the pump serial and the
local timestamp, which collides in a daylight-saving fall-back with nothing in the file to
break the tie, whereas Clarity's transmitter clock resolves it exactly (ADR-0001). And
Tandem substitutes a number for an out-of-range reading, which is the fabrication ADR-0003
exists to prevent, committed upstream where T1Pal cannot see it.

Cross-source deduplication was considered and deferred rather than solved. There is no
shared identifier, and the offset between the two clocks is not the small constant it was
believed to be: measured across several thousand matched pairs it runs from a few seconds
to over three minutes, bimodal with one mode per pump, drifting a few seconds per day, with
a step of tens of seconds where a pump clock resynced. A nearest-timestamp match is
therefore wrong for one of the two pumps — the true pairing sits a full five-minute slot
away. Matching on time proximity is a research problem, not a layer of a first slice.

## Consequences

Glucose and insulin come from two free-running clocks that drift apart by minutes. For
30-day bolus totals this does not matter. For insulin-on-board and forecasting it will,
and that needs to be solved before V0.3 rather than discovered there.

Tandem CGM data is imported and never read. This will look like dead weight to a future
reader; it is what keeps the deferral above honest and cheap to reverse.
