# Store both the local time and a derived instant

Every source T1Pal reads writes naive local wall-clock time with no offset and no zone
column, so a stored value can be a faithful copy of the file or an orderable point in
time, but not both. T1Pal stores both: the local time exactly as written, and an instant
resolved from it at import using an explicitly configured IANA timezone, which is recorded
on the import alongside the file hash.

## Considered options

Storing only the local time keeps the file faithful but makes ordering and subtraction
wrong across a daylight-saving transition. Storing only a derived instant makes analytics
correct but silently bakes in a timezone that came from outside the file and cannot be
audited or corrected later without re-importing.

## Consequences

The timezone becomes a recorded input with provenance rather than an ambient assumption,
which is the same commitment `docs/ARCHITECTURE.md` makes for values.

At a fall-back transition the local time is ambiguous. Dexcom Clarity can resolve it
exactly, because its transmitter clock is strictly increasing within a sensor session and
differs by exactly 3600 seconds between the two passes. Tandem Source cannot: it has no
monotonic clock and no record identifier, so a record whose fold cannot be determined is
marked as unresolved rather than guessed at silently.

Neither real export in hand crosses a transition; both fall entirely inside one
summer-time period. This logic therefore cannot be tested against real data and needs
synthetic fixtures built from the documented fall-back shape.
