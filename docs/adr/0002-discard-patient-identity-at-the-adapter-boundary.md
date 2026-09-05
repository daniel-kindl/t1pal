# Discard patient identity at the adapter boundary

The Dexcom Clarity export carries the patient's given name, surname and date of birth as
ordinary data rows, and both vendors put the patient's name in the export path. T1Pal
recognizes those rows, counts them, and discards them in the adapter. No domain object
holds them, no column exists for them, and no log line, error message or import record
contains an export path.

## Considered options

Storing a salted hash of the identity triple would let T1Pal warn that an export does not
belong to this user. For a single-user local database that guards against a mistake which
is easy to notice and cheap to undo, and it writes a derived personal identifier into a
file `docs/SAFETY_AND_PRIVACY.md` says should hold none.

## Consequences

T1Pal cannot detect that the wrong person's export was imported.

Import records refer to files by content hash and by role, never by path — otherwise the
name discarded from the rows returns through the filename.

A pump serial number is deliberately not covered by this decision. It is device identity
rather than patient identity, it is required to tell two pumps apart within one export,
and `docs/ARCHITECTURE.md` already names the source device as part of provenance. It is
stored once on a device record and never appears in a message or a filename.
